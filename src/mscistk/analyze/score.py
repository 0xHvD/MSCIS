from datetime import datetime, timezone
def trending_score(item, weights):
    # item fields: published (iso), linkedin={likes,comments,shares,views}, github={stars,issues,comments}, trends={score}
    w = weights
    age_days = max(0.1, (datetime.now(timezone.utc) - datetime.fromisoformat(item["published"])).days or 0.1)
    freshness = max(0, 1.0 - min(age_days/30.0, 1.0))  # 1 if today; ~0 after 30d
    li = item.get("linkedin",{})
    li_eng = (li.get("likes",0)*3 + li.get("comments",0)*4 + li.get("shares",0)*5 + li.get("views",0)/5000.0)
    li_norm = min(li_eng/100.0, 1.5)  # cap
    gh = item.get("github",{})
    gh_norm = min((gh.get("stars",0)*0.02 + gh.get("issues",0)*0.05 + gh.get("comments",0)*0.03), 1.0)
    gt = min(item.get("trends",{}).get("score",0)/100.0, 1.0)
    comm = min(item.get("community",0)/100.0, 1.0)
    score = (freshness*w["freshness_days"] + li_norm*w["linkedin_engagement"] +
             gh_norm*w["github_activity"] + gt*w["google_trends"] + comm*w["community_signal"])
    return round(score*100, 1)
