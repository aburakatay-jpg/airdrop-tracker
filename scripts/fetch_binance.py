import feedparser

def fetch_binance_opportunities():
    print("Binance ve Borsa haberleri taranıyor...")
    # Kripto haber sitelerinin stabil RSS beslemeleri
    rss_url = "https://cointelegraph.com/rss/tag/binance" 
    
    try:
        feed = feedparser.parse(rss_url)
        opportunities = []
        
        # Arayacağımız sihirli kelimeler (Küçük harfle)
        keywords = ["launchpool", "megadrop", "airdrop", "launchpad", "giveaway", "reward"]
        
        for entry in feed.entries[:15]: 
            title_lower = entry.title.lower()
            summary_lower = entry.summary.lower()
            
            if any(keyword in title_lower or keyword in summary_lower for keyword in keywords):
                opp = {
                    "project_name": entry.title,
                    "url": entry.link,
                    "description": entry.summary[:200],
                    "source": "Binance/Exchange News"
                }
                opportunities.append(opp)
                
        return opportunities
    except Exception as e:
        print(f"Borsa haberleri çekilirken hata: {e}")
        return []
