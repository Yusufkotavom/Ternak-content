"""
WordPress Publisher Module
Publish content ke WordPress menggunakan REST API
"""

import asyncio
import aiohttp
import requests
from typing import Dict, Optional
import json
import base64
from datetime import datetime
import os
import re

from src.utils.config import Settings

class WordPressPublisher:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.wordpress_url
        self.username = self.settings.wordpress_user
        self.app_password = self.settings.wordpress_app_password
        
        # Create auth header
        if self.username and self.app_password:
            credentials = f"{self.username}:{self.app_password}"
            self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        else:
            self.auth_header = None
    
    async def publish_post(self, keyword: str, content: str, title: str = None) -> Optional[int]:
        """Publish post ke WordPress"""
        
        if not self.base_url or not self.auth_header:
            print("WordPress credentials not configured")
            return None
        
        try:
            # Prepare post data
            post_data = {
                'title': title or f"Panduan Lengkap: {keyword.title()}",
                'content': content,
                'status': 'publish',
                'categories': [1],  # Default category
                'tags': [keyword],
                'meta': {
                    '_yoast_wpseo_metadesc': f"Panduan lengkap tentang {keyword}. Pelajari cara, tips, dan manfaat {keyword}.",
                    '_yoast_wpseo_focuskw': keyword
                }
            }
            
            # Publish via REST API
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wp-json/wp/v2/posts"
                headers = {
                    'Authorization': self.auth_header,
                    'Content-Type': 'application/json'
                }
                
                async with session.post(url, json=post_data, headers=headers) as response:
                    if response.status == 201:
                        post = await response.json()
                        post_id = post.get('id')
                        print(f"Post published successfully: {post_id}")
                        return post_id
                    else:
                        error_text = await response.text()
                        print(f"Error publishing post: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error publishing to WordPress: {str(e)}")
            return None
    
    async def update_post(self, post_id: int, content: str, title: str = None) -> bool:
        """Update existing post"""
        
        try:
            post_data = {
                'content': content
            }
            
            if title:
                post_data['title'] = title
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wp-json/wp/v2/posts/{post_id}"
                headers = {
                    'Authorization': self.auth_header,
                    'Content-Type': 'application/json'
                }
                
                async with session.put(url, json=post_data, headers=headers) as response:
                    if response.status == 200:
                        print(f"Post updated successfully: {post_id}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"Error updating post: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            print(f"Error updating WordPress post: {str(e)}")
            return False
    
    async def get_categories(self) -> list:
        """Get WordPress categories"""
        categories = []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wp-json/wp/v2/categories"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        categories = await response.json()
                        
        except Exception as e:
            print(f"Error getting categories: {str(e)}")
        
        return categories
    
    async def create_category(self, name: str, description: str = "") -> Optional[int]:
        """Create new category"""
        
        try:
            category_data = {
                'name': name,
                'description': description
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wp-json/wp/v2/categories"
                headers = {
                    'Authorization': self.auth_header,
                    'Content-Type': 'application/json'
                }
                
                async with session.post(url, json=category_data, headers=headers) as response:
                    if response.status == 201:
                        category = await response.json()
                        category_id = category.get('id')
                        print(f"Category created: {category_id}")
                        return category_id
                    else:
                        error_text = await response.text()
                        print(f"Error creating category: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error creating category: {str(e)}")
            return None
    
    async def upload_media(self, image_path: str, alt_text: str = "") -> Optional[str]:
        """Upload media ke WordPress"""
        
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Prepare multipart data
            data = aiohttp.FormData()
            data.add_field('file', image_data, filename=os.path.basename(image_path))
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wp-json/wp/v2/media"
                headers = {
                    'Authorization': self.auth_header
                }
                
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 201:
                        media = await response.json()
                        media_url = media.get('source_url')
                        print(f"Media uploaded: {media_url}")
                        return media_url
                    else:
                        error_text = await response.text()
                        print(f"Error uploading media: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error uploading media: {str(e)}")
            return None
    
    async def test_connection(self) -> bool:
        """Test WordPress connection"""
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wp-json/wp/v2/posts"
                headers = {'Authorization': self.auth_header} if self.auth_header else {}
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        print("WordPress connection successful")
                        return True
                    else:
                        print(f"WordPress connection failed: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"Error testing WordPress connection: {str(e)}")
            return False
    
    def prepare_content_for_wordpress(self, html_content: str) -> str:
        """Prepare HTML content untuk WordPress"""
        
        # WordPress-specific modifications
        content = html_content
        
        # Remove external CSS (WordPress will use theme CSS)
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Add WordPress-specific classes
        content = content.replace('<h1>', '<h1 class="entry-title">')
        content = content.replace('<h2>', '<h2 class="section-title">')
        content = content.replace('<h3>', '<h3 class="subsection-title">')
        
        # Add responsive image classes
        content = re.sub(r'<img([^>]+)>', r'<img\1 class="wp-image-responsive" />', content)
        
        return content
    
    async def publish_bulk_content(self, content_list: list) -> Dict:
        """Publish multiple articles"""
        results = {
            'success': [],
            'failed': []
        }
        
        for content_item in content_list:
            try:
                post_id = await self.publish_post(
                    keyword=content_item['keyword'],
                    content=content_item['content'],
                    title=content_item.get('title')
                )
                
                if post_id:
                    results['success'].append({
                        'keyword': content_item['keyword'],
                        'post_id': post_id
                    })
                else:
                    results['failed'].append({
                        'keyword': content_item['keyword'],
                        'error': 'Failed to publish'
                    })
                    
            except Exception as e:
                results['failed'].append({
                    'keyword': content_item['keyword'],
                    'error': str(e)
                })
        
        return results