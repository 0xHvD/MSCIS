import requests, sys, json, datetime

BASE = "https://api.msrc.microsoft.com/cvrf/v2.0"  # see MSRC API docs
def list_security_updates(api_key, year=None):
    params = {}
    if year:
        params["year"] = str(year)
    r = requests.get(f"{BASE}/updates", headers={"api-key": api_key, "Accept":"application/json"}, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    key = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print(json.dumps(list_security_updates(key, year), indent=2))
