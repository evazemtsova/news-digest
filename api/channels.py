import os
import json
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
    
    def do_GET(self):
        try:
            supabase = self._get_supabase_client()
            response = supabase.table('channels').select('*').execute()
            self._send_response(200, response.data)
        except Exception as e:
            self._send_response(500, {'error': str(e)})
    
    def do_POST(self):
        try:
            supabase = self._get_supabase_client()
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body)
            
            username = data.get('username', '').strip()
            tag = data.get('tag', 'other')
            
            if not username:
                self._send_response(400, {'error': 'Username is required'})
                return
            
            # Check if channel already exists
            existing = supabase.table('channels').select('id').eq('username', username).execute()
            if existing.data:
                self._send_response(409, {'error': 'Channel already exists'})
                return
            
            # Insert new channel
            channel_data = {
                'username': username,
                'tag': tag
            }
            
            response = supabase.table('channels').insert(channel_data).execute()
            self._send_response(201, response.data[0])
        except Exception as e:
            self._send_response(500, {'error': str(e)})
    
    def do_DELETE(self):
        try:
            supabase = self._get_supabase_client()
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body)
            
            username = data.get('username', '').strip()
            
            if not username:
                self._send_response(400, {'error': 'Username is required'})
                return
            
            response = supabase.table('channels').delete().eq('username', username).execute()
            self._send_response(200, {'message': f'Channel {username} deleted'})
        except Exception as e:
            self._send_response(500, {'error': str(e)})