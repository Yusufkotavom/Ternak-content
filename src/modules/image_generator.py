"""
Image Generator Module
Generate gambar menggunakan AI dan stock photo APIs
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

from src.utils.config import Settings

class ImageGenerator:
    def __init__(self):
        self.settings = Settings()
        self.ua = UserAgent()
        
        # API endpoints
        self.apis = {
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
    
    async def generate_images(self, keyword: str, content: Dict) -> List[str]:
        """Generate images untuk artikel"""
        images = []
        
        try:
            # 1. Generate AI images (DALL-E)
            ai_images = await self._generate_ai_images(keyword)
            images.extend(ai_images)
            
            # 2. Get stock photos
            stock_images = await self._get_stock_images(keyword)
            images.extend(stock_images)
            
            # 3. Save images locally
            saved_images = await self._save_images_locally(keyword, images)
            
            return saved_images[:self.settings.max_images_per_article]
            
        except Exception as e:
            print(f"Error generating images for '{keyword}': {str(e)}")
            return []
    
    async def _generate_ai_images(self, keyword: str) -> List[str]:
        """Generate AI images menggunakan DALL-E"""
        images = []
        
        try:
            if not self.settings.openai_api_key:
                return images
            
            # Generate prompts untuk AI
            prompts = self._create_image_prompts(keyword)
            
            for prompt in prompts[:2]:  # Generate 2 AI images
                try:
                    response = await openai.Image.acreate(
                        prompt=prompt,
                        n=1,
                        size="1024x1024",
                        quality="standard"
                    )
                    
                    if response.data:
                        image_url = response.data[0].url
                        images.append(image_url)
                        
                except Exception as e:
                    print(f"Error generating AI image: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in AI image generation: {str(e)}")
        
        return images
    
    async def _get_stock_images(self, keyword: str) -> List[str]:
        """Get stock images dari berbagai API"""
        images = []
        
        # Try Unsplash
        if self.settings.unsplash_api_key:
            unsplash_images = await self._get_unsplash_images(keyword)
            images.extend(unsplash_images)
        
        # Try Pixabay
        if self.settings.pixabay_api_key:
            pixabay_images = await self._get_pixabay_images(keyword)
            images.extend(pixabay_images)
        
        # Try Pexels
        if self.settings.pexels_api_key:
            pexels_images = await self._get_pexels_images(keyword)
            images.extend(pexels_images)
        
        return images
    
    async def _get_unsplash_images(self, keyword: str) -> List[str]:
        """Get images dari Unsplash API"""
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'query': keyword,
                    'per_page': 3,
                    'orientation': 'landscape'
                }
                
                async with session.get(
                    self.apis['unsplash']['url'],
                    params=params,
                    headers=self.apis['unsplash']['headers']
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
        """Get images dari Pixabay API"""
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': keyword,
                    'per_page': 3,
                    'image_type': 'photo',
                    'orientation': 'horizontal'
                }
                params.update(self.apis['pixabay']['params'])
                
                async with session.get(
                    self.apis['pixabay']['url'],
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
        """Get images dari Pexels API"""
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'query': keyword,
                    'per_page': 3,
                    'orientation': 'landscape'
                }
                
                async with session.get(
                    self.apis['pexels']['url'],
                    params=params,
                    headers=self.apis['pexels']['headers']
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for photo in data.get('photos', []):
                            if photo.get('src', {}).get('large'):
                                images.append(photo['src']['large'])
        
        except Exception as e:
            print(f"Error getting Pexels images: {str(e)}")
        
        return images
    
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