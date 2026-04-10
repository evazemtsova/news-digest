import os
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client


def handler(event, context):
    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Missing Supabase configuration'})
            }
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Fetch channels from Supabase
        channels_response = supabase.table('channels').select('*').execute()
        channels = channels_response.data
        
        if not channels:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No channels to parse'})
            }
        
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
        
        new_posts_count = 0
        
        # Parse each channel
        for channel in channels:
            username = channel['username']
            tag = channel['tag']
            
            try:
                # Fetch channel page
                url = f"https://t.me/s/{username}"
                resp = requests.get(url, headers=headers, timeout=15)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Parse posts
                for msg in soup.select(".tgme_widget_message"):
                    # Extract text
                    text_el = msg.select_one(".tgme_widget_message_text")
                    text = text_el.get_text("\n", strip=True) if text_el else ""
                    if not text:
                        continue
                    
                    # Extract date and link
                    time_el = msg.select_one(".tgme_widget_message_date time")
                    date_str = ""
                    if time_el and time_el.get("datetime"):
                        try:
                            dt = datetime.fromisoformat(time_el["datetime"])
                            date_str = dt.astimezone(timezone.utc).isoformat()
                        except ValueError:
                            date_str = datetime.now(timezone.utc).isoformat()
                    
                    link_el = msg.select_one(".tgme_widget_message_date")
                    link = link_el.get("href", url) if link_el else url
                    
                    # Check if post already exists (deduplication)
                    existing_post = supabase.table('posts').select('id').eq('link', link).execute()
                    if existing_post.data:
                        continue  # Skip if already exists
                    
                    # Insert new post
                    post_data = {
                        'text': text,
                        'date': date_str,
                        'link': link,
                        'channel': username,
                        'tag': tag
                    }
                    
                    supabase.table('posts').insert(post_data).execute()
                    new_posts_count += 1
                    
            except Exception as e:
                print(f"Error parsing channel {username}: {str(e)}")
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Parsing completed. Added {new_posts_count} new posts.'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }