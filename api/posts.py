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

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            supabase = self._get_supabase_client()
            response = supabase.table('posts').select('*').order('date', desc=True).limit(100).execute()
            self._send_response(200, response.data)
        except Exception as e:
            self._send_response(500, {'error': str(e)})