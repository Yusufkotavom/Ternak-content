"""
Image Generator Module
Generate gambar menggunakan AI dan stock photo APIs
Windows compatible with free APIs
"""

import asyncio
import aiohttp
import requests
from typing import List, Dict, Optional
import json
import os
from PIL import Image
import io
import base64
import random

# Free AI APIs
try:
    from diffusers import StableDiffusionPipeline
    import torch
    STABLE_DIFFUSION_AVAILABLE = True
except ImportError:
    STABLE_DIFFUSION_AVAILABLE = False

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

from src.utils.config import Settings

class ImageGenerator:
    def __init__(self):
        self.settings = Settings()
        
        # Initialize free APIs
        self.hf_client = None
        self.stable_diffusion = None
        
        # Setup free AI clients
        self._setup_free_ai_clients()
        
        # Free stock photo APIs
        self.free_apis = {
            'unsplash': {
                'url': 'https://api.unsplash.com/search/photos',
                'headers': {'Authorization': f'Client-ID {self.settings.unsplash_api_key}'} if self.settings.unsplash_api_key else {}
            },
            'pixabay': {
                'url': 'https://pixabay.com/api/',
                'params': {'key': self.settings.pixabay_api_key} if self.settings.pixabay_api_key else {}
            },
            'pexels': {
                'url': 'https://api.pexels.com/v1/search',
                'headers': {'Authorization': self.settings.pexels_api_key} if self.settings.pexels_api_key else {}
            }
        }
        
        # Free image URLs for fallback
        self.free_image_urls = [
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
            "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800",
            "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800",
            "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800",
            "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800"
        ]
    
    def _setup_free_ai_clients(self):
        """Setup free AI clients"""
        try:
            if HF_AVAILABLE:
                self.hf_client = InferenceClient()
        except Exception as e:
            print(f"HuggingFace setup failed: {e}")
        
        try:
            if STABLE_DIFFUSION_AVAILABLE and torch.cuda.is_available():
                # Only load if GPU is available
                self.stable_diffusion = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16
                )
                self.stable_diffusion = self.stable_diffusion.to("cuda")
        except Exception as e:
            print(f"Stable Diffusion setup failed: {e}")
    
    async def generate_images(self, keyword: str, content: Dict) -> List[str]:
        """Generate images untuk artikel"""
        images = []
        
        try:
            # 1. Try free AI image generation
            ai_images = await self._generate_free_ai_images(keyword)
            images.extend(ai_images)
            
            # 2. Get free stock photos
            stock_images = await self._get_free_stock_images(keyword)
            images.extend(stock_images)
            
            # 3. Add fallback images if needed
            if len(images) < self.settings.max_images_per_article:
                fallback_images = self._get_fallback_images(keyword)
                images.extend(fallback_images)
            
            # 4. Save images locally
            saved_images = await self._save_images_locally(keyword, images)
            
            return saved_images[:self.settings.max_images_per_article]
            
        except Exception as e:
            print(f"Error generating images for '{keyword}': {str(e)}")
            # Return fallback images
            return self._get_fallback_images(keyword)
    
    async def _generate_free_ai_images(self, keyword: str) -> List[str]:
        """Generate AI images menggunakan free APIs"""
        images = []
        
        try:
            # Try HuggingFace free API
            if self.hf_client:
                prompts = self._create_image_prompts(keyword)
                
                for prompt in prompts[:1]:  # Generate 1 AI image
                    try:
                        response = self.hf_client.post(
                            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                            json={"inputs": prompt}
                        )
                        
                        if response.status_code == 200:
                            # Save image
                            image_data = response.content
                            image_path = f"output/images/{keyword.replace(' ', '_')}_ai.jpg"
                            
                            os.makedirs(os.path.dirname(image_path), exist_ok=True)
                            with open(image_path, 'wb') as f:
                                f.write(image_data)
                            
                            images.append(image_path)
                            
                    except Exception as e:
                        print(f"Error generating AI image: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error in free AI image generation: {str(e)}")
        
        return images
    
    async def _get_free_stock_images(self, keyword: str) -> List[str]:
        """Get stock images dari free APIs"""
        images = []
        
        # Try Unsplash (free tier)
        if self.settings.unsplash_api_key:
            unsplash_images = await self._get_unsplash_images(keyword)
            images.extend(unsplash_images)
        
        # Try Pixabay (free tier)
        if self.settings.pixabay_api_key:
            pixabay_images = await self._get_pixabay_images(keyword)
            images.extend(pixabay_images)
        
        # Try Pexels (free tier)
        if self.settings.pexels_api_key:
            pexels_images = await self._get_pexels_images(keyword)
            images.extend(pexels_images)
        
        return images
    
    async def _get_unsplash_images(self, keyword: str) -> List[str]:
        """Get images dari Unsplash API (free tier)"""
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'query': keyword,
                    'per_page': 3,
                    'orientation': 'landscape'
                }
                
                async with session.get(
                    self.free_apis['unsplash']['url'],
                    params=params,
                    headers=self.free_apis['unsplash']['headers']
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for photo in data.get('results', []):
                            if photo.get('urls', {}).get('regular'):
                                images.append(photo['urls']['regular'])
        
        except Exception as e:
            print(f"Error getting Unsplash images: {str(e)}")
        
        return images
    
    async def _get_pixabay_images(self, keyword: str) -> List[str]:
        """Get images dari Pixabay API (free tier)"""
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': keyword,
                    'per_page': 3,
                    'image_type': 'photo',
                    'orientation': 'horizontal'
                }
                params.update(self.free_apis['pixabay']['params'])
                
                async with session.get(
                    self.free_apis['pixabay']['url'],
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for hit in data.get('hits', []):
                            if hit.get('webformatURL'):
                                images.append(hit['webformatURL'])
        
        except Exception as e:
            print(f"Error getting Pixabay images: {str(e)}")
        
        return images
    
    async def _get_pexels_images(self, keyword: str) -> List[str]:
        """Get images dari Pexels API (free tier)"""
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'query': keyword,
                    'per_page': 3,
                    'orientation': 'landscape'
                }
                
                async with session.get(
                    self.free_apis['pexels']['url'],
                    params=params,
                    headers=self.free_apis['pexels']['headers']
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for photo in data.get('photos', []):
                            if photo.get('src', {}).get('large'):
                                images.append(photo['src']['large'])
        
        except Exception as e:
            print(f"Error getting Pexels images: {str(e)}")
        
        return images
    
    def _get_fallback_images(self, keyword: str) -> List[str]:
        """Get fallback images when APIs fail"""
        # Return random free images
        return random.sample(self.free_image_urls, min(3, len(self.free_image_urls)))
    
    async def _save_images_locally(self, keyword: str, image_urls: List[str]) -> List[str]:
        """Save images ke local storage"""
        saved_paths = []
        
        # Create output directory
        output_dir = f"output/images/{keyword.replace(' ', '_')}"
        os.makedirs(output_dir, exist_ok=True)
        
        for i, image_url in enumerate(image_urls):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            
                            # Save image
                            image_path = f"{output_dir}/image_{i+1}.jpg"
                            with open(image_path, 'wb') as f:
                                f.write(image_data)
                            
                            saved_paths.append(image_path)
                            
            except Exception as e:
                print(f"Error saving image {i+1}: {str(e)}")
                continue
        
        return saved_paths
    
    def _create_image_prompts(self, keyword: str) -> List[str]:
        """Create prompts untuk AI image generation"""
        prompts = [
            f"Professional stock photo of {keyword}, high quality, realistic, commercial use",
            f"Beautiful {keyword} concept, modern design, clean background",
            f"Professional {keyword} illustration, business style, high resolution",
            f"Realistic {keyword} photography, natural lighting, professional quality",
            f"Modern {keyword} design, minimalist style, clean composition"
        ]
        
        return prompts
    
    async def optimize_image(self, image_path: str, max_width: int = 800) -> str:
        """Optimize image untuk web"""
        try:
            with Image.open(image_path) as img:
                # Resize if too large
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Save optimized version
                optimized_path = image_path.replace('.jpg', '_optimized.jpg')
                img.save(optimized_path, 'JPEG', quality=85, optimize=True)
                
                return optimized_path
                
        except Exception as e:
            print(f"Error optimizing image: {str(e)}")
            return image_path
    
    def get_image_alt_text(self, keyword: str, image_index: int) -> str:
        """Generate alt text untuk image"""
        alt_texts = [
            f"{keyword} - ilustrasi utama",
            f"Gambar {keyword} - konsep visual",
            f"Foto {keyword} - referensi visual",
            f"Desain {keyword} - inspirasi",
            f"Visualisasi {keyword} - panduan"
        ]
        
        return alt_texts[image_index % len(alt_texts)]