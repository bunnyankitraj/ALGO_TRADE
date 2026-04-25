from gnews import GNews
import dateparser
from datetime import datetime
import time

def fetch_news(broker_name, queries, days=7):
    """
    Fetches news about a specific broker and India/Stocks from the last N days.
    Uses GNews (RSS-based) instead of the broken GoogleNews scraper.
    """
    gn = GNews(language='en', country='IN', period=f'{days}d', max_results=10)

    all_articles = []
    seen_urls = set()
    seen_titles = set()

    BLACKLIST_SOURCES = ["scanx.trade", "market screener", "marketscreener"]

    print(f"Fetching news for {broker_name} with queries: {queries}")

    for query in queries:
        try:
            results = gn.get_news(query)

            for res in results:
                url = res.get('url', '')
                title = res.get('title', '')
                source = res.get('publisher', {}).get('title', '').lower()

                # Deduplication & Filtering
                if not url or not title:
                    continue
                if url in seen_urls or title in seen_titles:
                    continue
                if any(b in source for b in BLACKLIST_SOURCES):
                    continue

                seen_urls.add(url)
                seen_titles.add(title)

                # Parse Date
                raw_date = res.get('published date', '')
                parsed_date = dateparser.parse(raw_date) if raw_date else datetime.now()
                published_date_str = parsed_date.isoformat() if parsed_date else str(raw_date)

                article = {
                    "title": title,
                    "url": url,
                    "published_date": published_date_str,
                    "source": res.get('publisher', {}).get('title', 'Google News'),
                    "desc": res.get('description', '')
                }

                # Check broker name appears in article text
                text_blob = (title + " " + article['desc']).lower()
                match = False
                if broker_name.lower() in text_blob:
                    match = True
                elif broker_name == "JPMC" and (
                    "jp morgan" in text_blob or "jpmorgan" in text_blob or "jpmc" in text_blob
                ):
                    match = True
                elif broker_name == "Kotak" and (
                    "kotak institutional equities" in text_blob or "kotak securities" in text_blob
                ):
                    match = True

                if match:
                    all_articles.append(article)

            time.sleep(0.5)

        except Exception as e:
            print(f"Error fetching for query '{query}': {e}")

    print(f"  → Found {len(all_articles)} matching articles for {broker_name}")
    return all_articles
