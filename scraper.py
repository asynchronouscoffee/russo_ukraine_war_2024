import requests
from bs4 import BeautifulSoup
import scraperwiki

def scrape_oryx_data():
    url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    try:
        # Check robots.txt compliance
        robots = requests.get("https://www.oryxspioenkop.com/robots.txt", timeout=10)
        if "disallow: /2022/02/attack-on-europe" in robots.text.lower():
            raise RuntimeError("Scraping disallowed by robots.txt")

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        categories = soup.find_all('h3', class_='mw-headline')
        
        return [
            {
                "category": cat.get_text(strip=True),
                "vehicles": [
                    {
                        "text": a.get_text(strip=True),
                        "url": f"https://www.oryxspioenkop.com{a['href']}" 
                        if a['href'].startswith('/') else a['href']
                    }
                    for a in cat.find_next_siblings('a')
                    if cat.find_next_sibling() and cat.find_next_sibling().name != 'h3'
                ]
            }
            for cat in categories
        ]

    except Exception as e:
        print(f"Scraping failed: {str(e)}")
        return []

if __name__ == '__main__':
    # Clear previous data
    scraperwiki.sqlite.execute("DROP TABLE IF EXISTS combat_vehicles")
    
    # Create fresh table
    scraperwiki.sqlite.execute("""
        CREATE TABLE combat_vehicles (
            category TEXT,
            vehicle_name TEXT,
            vehicle_url TEXT,
            UNIQUE(category, vehicle_name)
        )
    """)
    
    # Insert new data
    data = scrape_oryx_data()
    for category in data:
        for vehicle in category['vehicles']:
            scraperwiki.sqlite.save(
                unique_keys=['category', 'vehicle_name'],
                data={
                    'category': category['category'],
                    'vehicle_name': vehicle['text'],
                    'vehicle_url': vehicle['url']
                },
                table_name='combat_vehicles'
            )
    
    print(f"Successfully stored {sum(len(c['vehicles']) for c in data)} vehicles")
