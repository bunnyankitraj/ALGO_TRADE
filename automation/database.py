import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json
from datetime import datetime
import pytz

# Global client to reuse
db_client = None

def get_db():
    global db_client
    if db_client:
        return db_client

    if not firebase_admin._apps:
        # Check for env var with JSON content (GitHub Actions)
        # The user should paste the entire content of serviceAccountKey.json into this ENV var
        creds_json = os.getenv("FIREBASE_CREDENTIALS")
        
        if creds_json:
            try:
                # Handle case where newlines might be escaped in some CI environments
                if isinstance(creds_json, str) and "{" in creds_json:
                    cred_dict = json.loads(creds_json)
                    cred = credentials.Certificate(cred_dict)
                else:
                    # Fallback if it's a path
                    cred = credentials.Certificate(creds_json)
            except Exception as e:
                print(f"Error loading FIREBASE_CREDENTIALS env: {e}")
                # Fallback to local file for testing
                cred = credentials.Certificate("firebase_credentials.json")
        else:
            # Fallback to local file for local testing
            if os.path.exists("firebase_credentials.json"):
                cred = credentials.Certificate("firebase_credentials.json")
            else:
                raise Exception("No FIREBASE_CREDENTIALS env var or firebase_credentials.json found.")
        
        firebase_admin.initialize_app(cred)
    
    db_client = firestore.client()
    return db_client

def init_db():
    """
    Initializes the Firestore connection.
    Schema creation is not needed for Firestore (NoSQL).
    """
    return get_db()

def save_article(db, title, url, published_date, source, raw_content=""):
    try:
        articles_ref = db.collection("articles")
        
        # Check for duplicates by URL
        # We assume URL is unique enough.
        query = articles_ref.where("url", "==", url).limit(1).stream()
        existing = list(query)
        
        if existing:
            # Return True/ID to indicate success/existence
            return existing[0].id
            
        # Add new
        # .add() returns (update_time, document_ref)
        timestamp, doc_ref = articles_ref.add({
            "title": title,
            "url": url,
            "published_date": published_date,
            "source": source,
            "raw_content": raw_content,
            "fetched_at": datetime.now(pytz.utc).isoformat()
        })
        return doc_ref.id
            
    except Exception as e:
        print(f"Error saving article {url}: {e}")
        return None

def save_rating(db, article_id, stock_name, rating, target_price, broker, currency="INR", article_data=None):
    try:
        ratings_ref = db.collection("ratings")
        
        # Check for duplicate
        query = ratings_ref.where("article_id", "==", article_id)\
                           .where("stock_name", "==", stock_name)\
                           .where("broker", "==", broker)\
                           .limit(1).stream()
                           
        if list(query):
            print(f"Rating already exists for {stock_name} by {broker}")
            return
            
        doc_data = {
            "article_id": article_id,
            "stock_ticker": stock_name.upper().replace(" ", ""),
            "stock_name": stock_name,
            "rating": rating,
            "broker": broker,
            "target_price": target_price,
            "currency": currency,
            "entry_date": datetime.now().date().isoformat() # Store as YYYY-MM-DD string
        }
        
        # Denormalize article data for easier frontend access
        if article_data:
            doc_data["article_title"] = article_data.get("title")
            doc_data["article_url"] = article_data.get("url")
            doc_data["article_date"] = article_data.get("published_date")
            
        ratings_ref.add(doc_data)
        print(f"Saved rating: {stock_name} ({rating})")
    except Exception as e:
        print(f"Error saving rating: {e}")
