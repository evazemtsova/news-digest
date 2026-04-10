import os
import json
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
        
        # Get posts sorted by date desc, limit 100
        response = supabase.table('posts').select('*').order('date', desc=True).limit(100).execute()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response.data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }