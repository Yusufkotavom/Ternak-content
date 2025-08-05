"""
Content Generator Module
Generate konten dengan E-E-A-T (Experience, Expertise, Authority, Trust)
Using free AI APIs
"""

import asyncio
import openai
from typing import Dict, List, Optional
import json
import re
from datetime import datetime
import requests
import os

# Free AI APIs
try:
    from transformers import pipeline
    from huggingface_hub import InferenceClient
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from src.utils.config import Settings

class ContentGenerator:
    def __init__(self):
        self.settings = Settings()
        
        # Initialize AI clients
        self.openai_client = None
        self.cohere_client = None
        self.anthropic_client = None
        self.hf_client = None
        
        # Setup AI clients
        self._setup_ai_clients()
        
        # E-E-A-T prompts
        self.eeat_prompts = {
            'expertise': [
                "Seperti seorang ahli dengan pengalaman 10+ tahun di bidang ini",
                "Dengan latar belakang akademis dan sertifikasi profesional",
                "Berdasarkan penelitian dan studi terbaru"
            ],
            'experience': [
                "Berdasarkan pengalaman langsung menangani ribuan kasus",
                "Dari pengalaman praktis selama bertahun-tahun",
                "Setelah menguji dan menerapkan berbagai metode"
            ],
            'authority': [
                "Disetujui oleh para ahli dan praktisi terkemuka",
                "Mengikuti standar industri dan best practices",
                "Berdasarkan rekomendasi dari asosiasi profesional"
            ],
            'trust': [
                "Dengan data dan statistik yang dapat dipercaya",
                "Berdasarkan testimoni dan review dari pengguna nyata",
                "Dengan jaminan kualitas dan hasil yang terukur"
            ]
        }
    
    def _setup_ai_clients(self):
        """Setup various AI clients for fallback"""
        try:
            if self.settings.openai_api_key:
                openai.api_key = self.settings.openai_api_key
                self.openai_client = openai
        except Exception as e:
            print(f"OpenAI setup failed: {e}")
        
        try:
            if hasattr(self.settings, 'cohere_api_key') and self.settings.cohere_api_key:
                self.cohere_client = cohere.Client(self.settings.cohere_api_key)
        except Exception as e:
            print(f"Cohere setup failed: {e}")
        
        try:
            if hasattr(self.settings, 'anthropic_api_key') and self.settings.anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        except Exception as e:
            print(f"Anthropic setup failed: {e}")
        
        try:
            if TRANSFORMERS_AVAILABLE:
                self.hf_client = InferenceClient()
        except Exception as e:
            print(f"HuggingFace setup failed: {e}")
    
    async def generate_outline(self, keyword: str, research_data: Dict) -> Dict:
        """Generate content outline berdasarkan keyword dan research data"""
        
        outline_prompt = f"""
        Buat outline artikel untuk keyword: "{keyword}"
        
        Research Data:
        - Related Keywords: {research_data.get('related_keywords', [])}
        - Questions: {research_data.get('questions', [])}
        - Competition: {research_data.get('competition', 'Unknown')}
        
        Buat outline dengan struktur:
        1. H1: Judul utama yang menarik dan SEO-friendly
        2. H2: 3-5 subheading yang mencakup aspek penting
        3. H3: 2-3 sub-subheading untuk setiap H2
        4. FAQ: 5-7 pertanyaan umum
        5. Conclusion
        
        Format output JSON:
        {{
            "title": "Judul Artikel",
            "h1": "Judul Utama",
            "h2_sections": [
                {{
                    "title": "Subheading 1",
                    "h3_subsections": ["Sub-sub 1", "Sub-sub 2"]
                }}
            ],
            "faq": ["Pertanyaan 1", "Pertanyaan 2", ...],
            "conclusion": "Kesimpulan artikel"
        }}
        """
        
        try:
            # Try different AI providers
            result = await self._try_ai_generation(outline_prompt, "outline")
            
            if result:
                outline = json.loads(result)
                return outline
            else:
                return self._create_fallback_outline(keyword)
                
        except Exception as e:
            print(f"Error generating outline: {str(e)}")
            return self._create_fallback_outline(keyword)
    
    async def generate_content(self, keyword: str, outline: Dict, research_data: Dict) -> Dict:
        """Generate full content dengan E-E-A-T"""
        
        # Build E-E-A-T context
        eeat_context = self._build_eeat_context(keyword, research_data)
        
        content_prompt = f"""
        Tulis artikel lengkap untuk keyword: "{keyword}"
        
        Outline:
        {json.dumps(outline, indent=2)}
        
        Research Data:
        - Related Keywords: {research_data.get('related_keywords', [])}
        - Top Results: {research_data.get('top_results', [])}
        
        E-E-A-T Requirements:
        {eeat_context}
        
        Instruksi:
        1. Tulis dalam bahasa Indonesia yang natural dan mudah dipahami
        2. Sertakan data, statistik, dan contoh nyata
        3. Gunakan tone yang meyakinkan dan profesional
        4. Panjang artikel: {self.settings.content_length} kata
        5. Optimalkan untuk SEO dengan keyword density yang natural
        6. Sertakan call-to-action yang relevan
        
        Format output JSON:
        {{
            "title": "Judul Artikel",
            "meta_description": "Meta description untuk SEO",
            "content": "Konten artikel lengkap dengan HTML tags",
            "summary": "Ringkasan singkat artikel",
            "keywords": ["keyword1", "keyword2", ...],
            "word_count": 1500
        }}
        """
        
        try:
            result = await self._try_ai_generation(content_prompt, "content")
            
            if result:
                content = json.loads(result)
                return content
            else:
                return self._create_fallback_content(keyword, outline)
                
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return self._create_fallback_content(keyword, outline)
    
    async def _try_ai_generation(self, prompt: str, task_type: str) -> Optional[str]:
        """Try different AI providers in order of preference"""
        
        # 1. Try OpenAI first
        if self.openai_client:
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",  # Use cheaper model
                    messages=[
                        {"role": "system", "content": "Anda adalah content writer profesional."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI failed: {e}")
        
        # 2. Try Cohere
        if self.cohere_client:
            try:
                response = self.cohere_client.generate(
                    model="command",
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.generations[0].text
            except Exception as e:
                print(f"Cohere failed: {e}")
        
        # 3. Try Anthropic
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-instant-1.2",
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            except Exception as e:
                print(f"Anthropic failed: {e}")
        
        # 4. Try HuggingFace (free)
        if self.hf_client:
            try:
                response = self.hf_client.post(
                    "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                    json={"inputs": prompt}
                )
                return response.json()[0]["generated_text"]
            except Exception as e:
                print(f"HuggingFace failed: {e}")
        
        # 5. Fallback to simple template
        return self._generate_simple_content(prompt, task_type)
    
    def _generate_simple_content(self, prompt: str, task_type: str) -> str:
        """Generate simple content when AI APIs are not available"""
        if task_type == "outline":
            return json.dumps({
                "title": "Panduan Lengkap",
                "h1": "Panduan Lengkap",
                "h2_sections": [
                    {
                        "title": "Pengenalan",
                        "h3_subsections": ["Apa itu", "Manfaat", "Kegunaan"]
                    },
                    {
                        "title": "Cara Melakukan",
                        "h3_subsections": ["Langkah-langkah", "Tips", "Perhatian"]
                    }
                ],
                "faq": ["Apa itu?", "Bagaimana cara?", "Apa manfaatnya?"],
                "conclusion": "Kesimpulan"
            })
        else:
            return json.dumps({
                "title": "Panduan Lengkap",
                "meta_description": "Panduan lengkap dan informatif",
                "content": "<h2>Pengenalan</h2><p>Artikel informatif yang lengkap.</p>",
                "summary": "Ringkasan artikel",
                "keywords": ["keyword"],
                "word_count": 500
            })
    
    def _build_eeat_context(self, keyword: str, research_data: Dict) -> str:
        """Build E-E-A-T context untuk prompt"""
        
        context = """
        Tulis artikel dengan menerapkan E-E-A-T (Experience, Expertise, Authority, Trust):
        
        EXPERIENCE:
        - Sertakan pengalaman praktis dan studi kasus nyata
        - Berikan contoh implementasi yang sudah terbukti
        - Gunakan bahasa seperti "Berdasarkan pengalaman saya selama 10 tahun..."
        
        EXPERTISE:
        - Tunjukkan pengetahuan mendalam tentang topik
        - Sertakan data ilmiah dan penelitian terbaru
        - Gunakan terminologi yang tepat dan profesional
        
        AUTHORITY:
        - Kutip sumber terpercaya dan ahli di bidangnya
        - Sertakan statistik dan data dari lembaga resmi
        - Berikan rekomendasi yang berdasarkan best practices
        
        TRUST:
        - Jujur tentang keterbatasan dan risiko
        - Sertakan disclaimer jika diperlukan
        - Berikan informasi yang seimbang dan objektif
        """
        
        return context
    
    async def build_html(self, keyword: str, content: Dict, images: List[str]) -> str:
        """Build HTML content dengan styling"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{content.get('title', keyword)}</title>
            <meta name="description" content="{content.get('meta_description', '')}">
            <meta name="keywords" content="{', '.join(content.get('keywords', []))}">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .article-container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 2.5em;
                    margin-bottom: 20px;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    font-size: 1.8em;
                    margin-top: 30px;
                    margin-bottom: 15px;
                }}
                h3 {{
                    color: #2c3e50;
                    font-size: 1.4em;
                    margin-top: 25px;
                    margin-bottom: 10px;
                }}
                p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 15px;
                    border-left: 4px solid #ffc107;
                    margin: 20px 0;
                }}
                .faq-section {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 30px 0;
                }}
                .faq-item {{
                    margin-bottom: 15px;
                }}
                .faq-question {{
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 5px;
                }}
                .image-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .image-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .conclusion {{
                    background-color: #d4edda;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 30px;
                    border-left: 4px solid #28a745;
                }}
                .meta-info {{
                    background-color: #e9ecef;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    font-size: 0.9em;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="article-container">
                <div class="meta-info">
                    <strong>Keyword:</strong> {keyword} | 
                    <strong>Word Count:</strong> {content.get('word_count', 0)} | 
                    <strong>Published:</strong> {datetime.now().strftime('%Y-%m-%d')}
                </div>
                
                <h1>{content.get('title', keyword)}</h1>
                
                {content.get('content', '')}
                
                {self._build_image_html(images)}
                
                <div class="conclusion">
                    <h3>Kesimpulan</h3>
                    <p>{content.get('summary', '')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _build_image_html(self, images: List[str]) -> str:
        """Build HTML untuk images"""
        if not images:
            return ""
        
        image_html = '<div class="image-container">'
        for i, image_url in enumerate(images):
            image_html += f'<img src="{image_url}" alt="Gambar {i+1}" />'
        image_html += '</div>'
        
        return image_html
    
    def _create_fallback_outline(self, keyword: str) -> Dict:
        """Create fallback outline jika AI gagal"""
        return {
            "title": f"Panduan Lengkap: {keyword.title()}",
            "h1": f"Panduan Lengkap: {keyword.title()}",
            "h2_sections": [
                {
                    "title": f"Apa itu {keyword}?",
                    "h3_subsections": ["Definisi", "Manfaat", "Kegunaan"]
                },
                {
                    "title": f"Cara {keyword}",
                    "h3_subsections": ["Langkah-langkah", "Tips", "Hal yang Perlu Diperhatikan"]
                },
                {
                    "title": f"Tips dan Trik {keyword}",
                    "h3_subsections": ["Best Practices", "Kesalahan Umum", "Rekomendasi"]
                }
            ],
            "faq": [
                f"Apa itu {keyword}?",
                f"Bagaimana cara {keyword}?",
                f"Apa manfaat {keyword}?",
                f"Berapa biaya {keyword}?",
                f"Di mana bisa {keyword}?"
            ],
            "conclusion": f"Kesimpulan tentang {keyword}"
        }
    
    def _create_fallback_content(self, keyword: str, outline: Dict) -> Dict:
        """Create fallback content jika AI gagal"""
        return {
            "title": outline.get("title", f"Panduan {keyword.title()}"),
            "meta_description": f"Panduan lengkap tentang {keyword}. Pelajari cara, tips, dan manfaat {keyword}.",
            "content": f"""
            <h2>Apa itu {keyword}?</h2>
            <p>{keyword} adalah topik yang penting untuk dipahami. Dalam artikel ini, kita akan membahas secara mendalam tentang {keyword}.</p>
            
            <h2>Cara {keyword}</h2>
            <p>Berikut adalah langkah-langkah untuk {keyword}:</p>
            <ol>
                <li>Langkah pertama</li>
                <li>Langkah kedua</li>
                <li>Langkah ketiga</li>
            </ol>
            
            <h2>Tips dan Trik</h2>
            <p>Beberapa tips untuk {keyword}:</p>
            <ul>
                <li>Tip pertama</li>
                <li>Tip kedua</li>
                <li>Tip ketiga</li>
            </ul>
            
            <div class="faq-section">
                <h3>FAQ</h3>
                <div class="faq-item">
                    <div class="faq-question">Apa itu {keyword}?</div>
                    <div>Jawaban tentang {keyword}.</div>
                </div>
            </div>
            """,
            "summary": f"Artikel ini membahas tentang {keyword} secara lengkap.",
            "keywords": [keyword, f"cara {keyword}", f"tips {keyword}"],
            "word_count": 500
        }