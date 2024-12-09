import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

from database import MentionDatabase


def get_session_token(api_key: str) -> Optional[str]:
    """Get a session token using the API key"""
    login_url = "https://app.mentionmind.com/api/login.php"
    
    print("Getting session token...")
    response = requests.post(login_url, data={'key': api_key})
    
    if not response.ok:
        print(f"Login failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    try:
        data = response.json()
        if 'token' in data:
            print("Successfully obtained session token")
            return data['token']
        else:
            print(f"Unexpected response format: {data}")
            return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse login response: {e}")
        print(f"Raw response: {response.text}")
        return None


def sanitize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    try:
        # First try to handle as string
        if isinstance(text, str):
            # Replace problematic characters with their closest ASCII equivalent
            text = text.encode('ascii', errors='replace').decode('ascii')
        return str(text)
    except Exception:
        return "[Text contains invalid characters]"


def process_mention(mention: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        # Get ID directly from the raw mention
        mention_id = str(mention.get('id', 'Unknown'))
        
        # Get date from date_added
        date_str = mention.get('date_added', '')
        
        # Get content from snippet and text_summary
        content = mention.get('snippet', '')
        if mention.get('text_summary'):
            content = f"{content}\n{mention['text_summary']}"
            
        # Clean the content - replace problematic characters
        content = sanitize_text(content)
        
        sanitized_mention = {
            'mention_id': mention_id,
            'timestamp': int(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp()) if date_str else 0,
            'source': sanitize_text(mention.get('source', '')),
            'content': content if content else '[No content available]',
            'url': sanitize_text(mention.get('url', '')),
            'author': sanitize_text(mention.get('author', '')),
            'sentiment': mention.get('sentiment', 0),
            'title': sanitize_text(mention.get('title', '')),
            'keywords': sanitize_text(mention.get('keywords', ''))
        }
        
        # Print formatted output
        print("\n---")
        print(f"ID: {mention_id}")
        print(f"Date: {date_str}")
        print(f"Source: {sanitized_mention['source']}")
        print(f"Title: {sanitized_mention['title']}")
        print(f"Keywords: {sanitized_mention['keywords']}")
        print(f"Content: {content if content else '[No content available]'}")
        print(f"URL: {sanitized_mention['url']}")
        print("---")
        
        return sanitized_mention
        
    except Exception as e:
        print(f"Error processing mention {mention.get('id', 'unknown')}: {str(e)}")
        return None


def get_mentions(token: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
    url = 'https://app.mentionmind.com/api/mention.php'
    params = {
        'token': token,
        'func': 'getMentions',
        'project_id': '1597',
        'limit': str(limit),
        'sort': 'date',
        'order': 'DESC'
    }
    
    try:
        response = requests.get(url, params=params)
        print("\nAPI URL:", response.url)
        print("Using params:", params)
        print("\nResponse Status:", response.status_code)
        
        if response.status_code == 200:
            # Parse JSON response
            mentions = response.json()
            if mentions:
                print("\nFirst mention data (debug):")
                print(json.dumps(mentions[0], indent=2))
                print(f"\nFetched {len(mentions)} mentions")
                return mentions
            else:
                print("No mentions found in response")
                return []
        else:
            print(f"Error: Response status code {response.status_code}")
            print(f"Raw response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {str(e)}")
        print(f"Raw response text: {response.text}")
        return None


def import_real_mentions(limit: int = 10) -> None:
    # Load environment variables
    load_dotenv()
    
    # Initialize API key and database
    api_key = os.getenv('MENTIONMIND_API_KEY')
    if not api_key:
        raise ValueError("MENTIONMIND_API_KEY not found in environment variables")
    
    # Get session token
    session_token = get_session_token(api_key)
    if not session_token:
        print("Failed to get session token")
        return
    
    db = MentionDatabase()
    
    # Fetch mentions
    mentions = get_mentions(session_token, limit)
    if not mentions:
        print("No mentions found!")
        return
    
    # Convert mentions to DynamoDB format
    dynamo_mentions = []
    for mention in mentions:
        sanitized = process_mention(mention)
        if sanitized:
            dynamo_mentions.append(sanitized)
    
    if not dynamo_mentions:
        print("No mentions to store!")
        return
    
    # Store in DynamoDB
    print(f"\nStoring {len(dynamo_mentions)} mentions in DynamoDB...")
    successful, failed = db.batch_store_mentions(dynamo_mentions)
    
    print(f"\nSuccessfully stored: {len(successful)} mentions")
    if failed:
        print(f"Failed to store: {len(failed)} mentions")
    
    # Print out the stored mentions
    print("\nStored Mentions:")
    for mention in mentions:  # Use raw mentions for display
        process_mention(mention)


if __name__ == "__main__":
    import_real_mentions(10)
