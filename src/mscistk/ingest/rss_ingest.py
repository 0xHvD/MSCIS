import feedparser, time, hashlib
from datetime import datetime, timezone
from dateutil import parser as dtparser

def normalize_entry(feed_name, entry):
    published = None
    if getattr(entry, 'published', None):
        try:
            published = dtparser.parse(entry.published)
        except Exception:
            published = None
    if not published and getattr(entry, 'updated', None):
        try:
            published = dtparser.parse(entry.updated)
        except Exception:
            published = None
    if not published:
        published = datetime.now(timezone.utc)
    uid = hashlib.sha256((entry.get('link','') + entry.get('title','')).encode()).hexdigest()[:16]
    return {
        "id": uid,
        "source": feed_name,
        "title": entry.get("title", "").strip(),
        "link": entry.get("link", ""),
        "summary": entry.get("summary", ""),
        "published": published.isoformat(),
        "tags": [t['term'] for t in entry.get("tags", [])] if getattr(entry, 'tags', None) else [],
    }

def fetch_feed(name, url):
    d = feedparser.parse(url)
    return [normalize_entry(name, e) for e in d.entries]

if __name__ == "__main__":
    import yaml, sys, json
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "src/mscistk/config/settings.yaml"
    cfg = yaml.safe_load(open(cfg_path))
    items = []
    for s in cfg.get("sources",{}).get("rss", []):
        items.extend(fetch_feed(s["name"], s["url"]))
    print(json.dumps(items, indent=2, ensure_ascii=False))
