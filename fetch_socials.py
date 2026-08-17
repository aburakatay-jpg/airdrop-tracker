import feedparser

def fetch_airdrop_sites():
    print("Airdrop platformları taranıyor...")
    # Airdrops.io son airdroplar RSS
    rss_url = "https://airdrops.io/feed/"
    
    try:
        feed = feedparser.parse(rss_url)
        opportunities = []
        
        for entry in feed.entries[:10]:
            opp = {
                "project_name": entry.title,
                "url": entry.link,
                "description": entry.summary[:250],
                "source": "Airdrops.io"
            }
            opportunities.append(opp)
            
        return opportunities
    except Exception as e:
        print(f"Airdrop siteleri taranırken hata: {e}")
        return []
