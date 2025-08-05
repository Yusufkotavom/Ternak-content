#!/usr/bin/env python3
"""
CLI Tool untuk Auto Content Generator
"""

import asyncio
import argparse
import sys
import os
from typing import List
import pandas as pd

from src.modules.keyword_research import KeywordResearch
from src.modules.content_generator import ContentGenerator
from src.modules.image_generator import ImageGenerator
from src.modules.wordpress_publisher import WordPressPublisher
from src.utils.config import Settings

class ContentGeneratorCLI:
    def __init__(self):
        self.settings = Settings()
        self.keyword_research = KeywordResearch()
        self.content_generator = ContentGenerator()
        self.image_generator = ImageGenerator()
        self.wordpress_publisher = WordPressPublisher()
    
    async def process_single_keyword(self, keyword: str, output_dir: str = "output") -> bool:
        """Process single keyword"""
        print(f"🔍 Processing keyword: {keyword}")
        
        try:
            # 1. Keyword Research
            print("  📊 Researching keyword...")
            research_data = await self.keyword_research.research_keyword(keyword)
            
            # 2. Generate Outline
            print("  📝 Generating content outline...")
            outline = await self.content_generator.generate_outline(keyword, research_data)
            
            # 3. Generate Content
            print("  ✍️  Generating content with E-E-A-T...")
            content = await self.content_generator.generate_content(keyword, outline, research_data)
            
            # 4. Generate Images
            print("  🖼️  Generating images...")
            images = await self.image_generator.generate_images(keyword, content)
            
            # 5. Build HTML
            print("  🌐 Building HTML...")
            html_content = await self.content_generator.build_html(keyword, content, images)
            
            # 6. Save to file
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{output_dir}/{keyword.replace(' ', '_')}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  ✅ Content saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error processing '{keyword}': {str(e)}")
            return False
    
    async def process_bulk_keywords(self, keywords: List[str], output_dir: str = "output") -> dict:
        """Process multiple keywords"""
        results = {
            'success': [],
            'failed': []
        }
        
        print(f"🚀 Processing {len(keywords)} keywords...")
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] Processing: {keyword}")
            
            success = await self.process_single_keyword(keyword, output_dir)
            
            if success:
                results['success'].append(keyword)
            else:
                results['failed'].append(keyword)
        
        return results
    
    async def process_csv_file(self, csv_path: str, output_dir: str = "output") -> dict:
        """Process keywords from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            if 'keyword' in df.columns:
                keywords = df['keyword'].tolist()
            else:
                keywords = df.iloc[:, 0].tolist()
            
            return await self.process_bulk_keywords(keywords, output_dir)
            
        except Exception as e:
            print(f"❌ Error reading CSV file: {str(e)}")
            return {'success': [], 'failed': [csv_path]}
    
    async def publish_to_wordpress(self, keyword: str, content_path: str) -> bool:
        """Publish content to WordPress"""
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare content for WordPress
            wp_content = self.wordpress_publisher.prepare_content_for_wordpress(content)
            
            # Publish
            post_id = await self.wordpress_publisher.publish_post(keyword, wp_content)
            
            if post_id:
                print(f"✅ Published to WordPress: Post ID {post_id}")
                return True
            else:
                print("❌ Failed to publish to WordPress")
                return False
                
        except Exception as e:
            print(f"❌ Error publishing to WordPress: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Auto Content Generator CLI")
    parser.add_argument('--keyword', '-k', help='Single keyword to process')
    parser.add_argument('--keywords', '-ks', nargs='+', help='Multiple keywords to process')
    parser.add_argument('--csv', '-c', help='CSV file with keywords')
    parser.add_argument('--output', '-o', default='output', help='Output directory')
    parser.add_argument('--wordpress', '-w', action='store_true', help='Publish to WordPress')
    parser.add_argument('--test', '-t', action='store_true', help='Test WordPress connection')
    
    args = parser.parse_args()
    
    cli = ContentGeneratorCLI()
    
    async def run():
        if args.test:
            # Test WordPress connection
            success = await cli.wordpress_publisher.test_connection()
            if success:
                print("✅ WordPress connection successful")
            else:
                print("❌ WordPress connection failed")
            return
        
        if args.keyword:
            # Process single keyword
            success = await cli.process_single_keyword(args.keyword, args.output)
            if success and args.wordpress:
                content_path = f"{args.output}/{args.keyword.replace(' ', '_')}.html"
                await cli.publish_to_wordpress(args.keyword, content_path)
        
        elif args.keywords:
            # Process multiple keywords
            results = await cli.process_bulk_keywords(args.keywords, args.output)
            print(f"\n📊 Results: {len(results['success'])} success, {len(results['failed'])} failed")
            
            if args.wordpress:
                for keyword in results['success']:
                    content_path = f"{args.output}/{keyword.replace(' ', '_')}.html"
                    await cli.publish_to_wordpress(keyword, content_path)
        
        elif args.csv:
            # Process CSV file
            results = await cli.process_csv_file(args.csv, args.output)
            print(f"\n📊 Results: {len(results['success'])} success, {len(results['failed'])} failed")
            
            if args.wordpress:
                for keyword in results['success']:
                    content_path = f"{args.output}/{keyword.replace(' ', '_')}.html"
                    await cli.publish_to_wordpress(keyword, content_path)
        
        else:
            print("❌ Please provide a keyword, keywords, or CSV file")
            parser.print_help()
    
    asyncio.run(run())

if __name__ == "__main__":
    main()