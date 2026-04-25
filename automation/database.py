from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import os
import json
from datetime import datetime
import pytz

# Global client to reuse
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise Exception("No MONGO_URI env var found. Please set it in your .env file.")

    _client = MongoClient(mongo_uri)
    _db = _client["jefferies_db"]

    # Create unique indexes to prevent duplicates
    _db["articles"].create_index("url", unique=True)
    _db["articles"].create_index("title", unique=True)  # also dedupe by title
    _db["ratings"].create_index(
        [("article_id", 1), ("stock_name", 1), ("broker", 1)],
        unique=True
    )
    _db["ratings"].create_index(
        [("article_title", 1), ("stock_name", 1), ("broker", 1)],
        unique=True
    )

    return _db


def init_db():
    return get_db()


def save_article(db, title, url, published_date, source, raw_content=""):
    try:
        articles_col = db["articles"]

        # Check for duplicates by URL or title
        existing = articles_col.find_one({"$or": [{"url": url}, {"title": title}]})
        if existing:
            return str(existing["_id"])

        result = articles_col.insert_one({
            "title": title,
            "url": url,
            "published_date": published_date,
            "source": source,
            "raw_content": raw_content,
            "fetched_at": datetime.now(pytz.utc).isoformat()
        })
        return str(result.inserted_id)

    except DuplicateKeyError:
        existing = db["articles"].find_one({"url": url})
        return str(existing["_id"]) if existing else None
    except Exception as e:
        print(f"Error saving article {url}: {e}")
        return None


def save_rating(db, article_id, stock_name, rating, target_price, broker, currency="INR", article_data=None):
    try:
        ratings_col = db["ratings"]

        # Check for duplicate
        existing = ratings_col.find_one({
            "article_id": article_id,
            "stock_name": stock_name,
            "broker": broker
        })
        if existing:
            print(f"Rating already exists for {stock_name} by {broker}")
            return

        doc = {
            "article_id": article_id,
            "stock_ticker": stock_name.upper().replace(" ", ""),
            "stock_name": stock_name,
            "rating": rating,
            "broker": broker,
            "target_price": target_price,
            "currency": currency,
            "entry_date": datetime.now().date().isoformat(),
            "fetched_at": datetime.now(pytz.utc).isoformat()  # for broker activity tracking
        }

        if article_data:
            doc["article_title"] = article_data.get("title")
            doc["article_url"] = article_data.get("url")
            doc["article_date"] = article_data.get("published_date")

        ratings_col.insert_one(doc)
        print(f"Saved rating: {stock_name} ({rating})")

    except DuplicateKeyError:
        print(f"Duplicate rating skipped: {stock_name} by {broker}")
    except Exception as e:
        print(f"Error saving rating: {e}")
