import os, requests, json, time

BASE = "https://api.github.com"

def repo_events(owner, repo, token=None):
    url = f"{BASE}/repos/{owner}/{repo}/events"
    h = {"Accept":"application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=h, timeout=30)
    r.raise_for_status()
    return r.json()

def search_repos(query, token=None):
    url = f"{BASE}/search/repositories"
    h = {"Accept":"application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=h, params={"q":query, "sort":"updated", "order":"desc"}, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    token = os.getenv("GITHUB_TOKEN")
    print(json.dumps(search_repos("Sysinternals in:name org:microsoft"), indent=2))
