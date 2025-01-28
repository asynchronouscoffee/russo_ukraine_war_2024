import requests
from bs4 import BeautifulSoup
import scraperwiki

def safe_get_text(element):
    return element.get_text(strip=True) if element else ''

def scrape_vehicles():
    url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        categories = []
        for h3 in soup.find_all('h3', {'class': 'mw-headline'}):
            category_name = safe_get_text(h3)
            vehicles = []
            
            sibling = h3.find_next_sibling()
            while sibling and sibling.name != 'h3':
                if sibling.name == 'a':
                    link = sibling.get('href', '')
                    if link.startswith('/'):
                        link = 'https://www.oryxspioenkop.com' + link
                    vehicles.append({
                        'name': safe_get_text(sibling),
                        'url': link
                    })
                sibling = sibling.find_next_sibling()
            
            categories.append({'category': category_name, 'vehicles': vehicles})
        
        return categories
    
    except Exception as e:
        print("Scraping error: {}".format(str(e)))
        return []

if __name__ == '__main__':
    scraperwiki.sql.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            category TEXT,
            vehicle_name TEXT,
            vehicle_url TEXT,
            UNIQUE(category, vehicle_name)
        )
    ''')
    
    data = scrape_vehicles()
    total = 0
    
    for cat in data:
        for vehicle in cat['vehicles']:
            scraperwiki.sql.save(
                unique_keys=['category', 'vehicle_name'],
                data={
                    'category': cat['category'],
                    'vehicle_name': vehicle['name'],
                    'vehicle_url': vehicle['url']
                },
                table_name='vehicles'
            )
            total += 1
    
    print("Successfully stored {} vehicle records".format(total))
