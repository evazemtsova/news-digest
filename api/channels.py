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
        
        method = event.get('httpMethod', 'GET')
        
        if method == 'GET':
            # Return list of channels
            response = supabase.table('channels').select('*').execute()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response.data)
            }
            
        elif method == 'POST':
            # Add new channel
            body = json.loads(event.get('body', '{}'))
            username = body.get('username', '').strip()
            tag = body.get('tag', 'other')
            
            if not username:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Username is required'})
                }
            
            # Check if channel already exists
            existing = supabase.table('channels').select('id').eq('username', username).execute()
            if existing.data:
                return {
                    'statusCode': 409,
                    'body': json.dumps({'error': 'Channel already exists'})
                }
            
            # Insert new channel
            channel_data = {
                'username': username,
                'tag': tag
            }
            
            response = supabase.table('channels').insert(channel_data).execute()
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response.data[0])
            }
            
        elif method == 'DELETE':
            # Delete channel by username
            body = json.loads(event.get('body', '{}'))
            username = body.get('username', '').strip()
            
            if not username:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Username is required'})
                }
            
            response = supabase.table('channels').delete().eq('username', username).execute()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': f'Channel {username} deleted'})
            }
            
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }