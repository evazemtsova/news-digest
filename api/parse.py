import os
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client


class handler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, data, headers=None):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _get_supabase_client(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError('Missing Supabase configuration')
        
        return create_client(supabase_url, supabase_key)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            supabase = self._get_supabase_client()
            
            # Fetch channels from Supabase
            channels_response = supabase.table('channels').select('*').execute()
            channels = channels_response.data
            
            if not channels:
                self._send_response(200, {'message': 'No channels to parse'})
                return
            
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
                    
                    # Load all known links for this channel upfront (avoids N+1 queries)
                    existing_links_response = supabase.table('posts').select('link').eq('channel', username).execute()
                    existing_links = {row['link'] for row in existing_links_response.data}

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

                        # Skip if already exists (O(1) set lookup)
                        if link in existing_links:
                            continue

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
            
            self._send_response(200, {
                'message': f'Parsing completed. Added {new_posts_count} new posts.'
            })
            
        except Exception as e:
            self._send_response(500, {'error': str(e)})