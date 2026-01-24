from .news_fetcher import fetch_news
from .analyzer import analyze_article
from .database import init_db, save_article, save_rating
from dotenv import load_dotenv
import datetime
import sys
import os
import difflib

# Add parent directory to path to import fetch_full_list properly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from fetch_full_list import get_master_list

def run_job():
    load_dotenv()
    print(f"--- Job Started at {datetime.datetime.now()} ---")
    
    # 1. Init DB (Firestore)
    db = init_db()
    
    # 2. Load Master List (In-Memory)
    df_master = get_master_list()
    if not df_master.empty:
        all_company_names = df_master['company_name'].dropna().tolist()
        # Create a mapping for Symbol if needed, but we mostly store company_name
    else:
        print("Warning: Master List is empty. Validation will be skipped/limited.")
        all_company_names = []

    brokers = {
        "Jefferies": [
            "Jefferies India stock target",
            "Jefferies upgrade India stock",
            "Jefferies downgrade India stock",
            "Jefferies maintain buy India"
        ],
        "JPMC": [
            "JP Morgan India stock target",
            "JP Morgan upgrade India stock",
            "JP Morgan overweight India stock",
            "J.P. Morgan India equity research"
        ],
        "Goldman Sachs": [
            "Goldman Sachs India stock target",
            "Goldman Sachs upgrade India stock",
            "Goldman Sachs India equity research"
        ],
        "ICICI Securities": [
            "ICICI Securities stock target buy",
            "ICICI Securities research report India",
            "ICICI Securities upgrade rating"
        ],
        "Kotak": [
            "Kotak Institutional Equities stock target",
            "Kotak Securities buy rating India",
            "Kotak Investment Banking research"
        ],
        "Axis Capital": [
            "Axis Capital India stock target",
            "Axis Capital research report",
            "Axis Capital buy rating"
        ],
        "JM Financial": [
            "JM Financial stock target buy",
            "JM Financial research India",
            "JM Financial upgrade rating"
        ]
    }
    
    new_ratings_count = 0
    days_to_fetch = 2
    
    for broker_name, queries in brokers.items():
        print(f"Processing {broker_name}...")
        # 3. Fetch News
        articles = fetch_news(broker_name, queries, days=days_to_fetch)
        print(f"Fetched {len(articles)} articles for {broker_name}.")
        
        for art in articles:
            # 4. Save Article
            art_id = save_article(db, art['title'], art['url'], art['published_date'], art['source'], art.get('desc', ''))
            
            if not art_id:
                continue

            # Check if we already have ratings for this article AND this broker (Query Firestore)
            # Optimization: We check this inside save_rating usually, but efficient to check before analysis
            # In database.py save_rating does a check. We'll rely on that or add a 'has_rating' function
            # To save AI costs, we should verify existence first.
            # But Firestore query overhead vs AI cost... let's trust save_rating to handle duplicates
            # BUT, we want to skip ANALYZER call if exists.
            
            # Since we don't have a quick "check_rating_exists" helper, let's just proceed.
            # The original code did: existing_ratings = list(db["stock_ratings"]...)
            # We can replicate that query if we want to save AI tokens:
            try:
                ratings_ref = db.collection("ratings")
                q = ratings_ref.where("article_id", "==", art_id).where("broker", "==", broker_name).limit(1).get()
                if len(q) > 0:
                    print(f"Skipping analysis for {art['title']} (Rating exists)")
                    continue
            except Exception as e:
                print(f"Error checking existing rating: {e}")
                
            # 5. Analyze
            ratings = analyze_article(art, broker_name=broker_name)
            
            for r in ratings:
                raw_name = r.stock_name
                valid_name = None
                
                # Validate against Master List (In-Memory Fuzzy Match)
                if all_company_names:
                    # Clean the name
                    clean_input = raw_name.replace(".", "").replace(",", "").replace("-", " ").replace("\"", "").replace("'", "")
                    
                    # 1. Exact case-insensitive match check first
                    for name in all_company_names:
                        if clean_input.lower() == name.lower():
                            valid_name = name
                            break
                    
                    # 2. If no exact match, try fuzzy
                    if not valid_name:
                        matches = difflib.get_close_matches(clean_input, all_company_names, n=1, cutoff=0.6)
                        if matches:
                            valid_name = matches[0]
                else:
                    valid_name = raw_name # Fallback if no master list (shouldn't happen usually)
                
                if valid_name:
                    print(f"Found Rating: {valid_name} ({r.rating}) from {broker_name}")
                    save_rating(
                        db, 
                        art_id, 
                        valid_name, 
                        r.rating, 
                        r.target_price, 
                        broker_name, 
                        currency=r.currency,
                        article_data={
                            "title": art['title'],
                            "url": art['url'],
                            "published_date": art['published_date']
                        }
                    )
                    new_ratings_count += 1
                else:
                    print(f"Skipped unknown stock: {raw_name}")
            
    print(f"Job Finished. Added {new_ratings_count} new ratings.")
    print("-----------------------------------")

if __name__ == "__main__":
    run_job()
