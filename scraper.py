# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import scraperwiki

def scrape_oryx_data():
    url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36"}

    try:
        # Check robots.txt compliance
        robots = requests.get("https://www.oryxspioenkop.com/robots.txt")
        if "disallow: /2022/02/attack-on-europe" in robots.text.lower():
            raise Exception("Scraping disallowed by robots.txt")

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        categories = soup.find_all('h3', {'class': 'mw-headline'})
        
        data = []
        for category in categories:
            category_name = category.get_text(strip=True)
            vehicles = []
            
            next_element = category.find_next_sibling()
            while next_element and next_element.name != 'h3':
                if next_element.name == 'a':
                    link = next_element.get('href')
                    if link and not link.startswith('http'):
                        link = "https://www.oryxspioenkop.com" + link
                    vehicles.append({
                        'text': next_element.get_text(strip=True),
                        'url': link
                    })
                next_element = next_element.find_next_sibling()
            
            data.append({'category': category_name, 'vehicles': vehicles})
        
        return data

    except Exception as e:
        print "Error: %s" % str(e)
        return []

# Morph.io entry point
if __name__ == '__main__':
    # Initialize database
    scraperwiki.sqlite.execute("CREATE TABLE IF NOT EXISTS data (category TEXT, vehicle_text TEXT, vehicle_url TEXT)")
    
    # Scrape and save to SQLite
    combat_data = scrape_oryx_data()
    total_records = 0
    
    for category in combat_data:
        for vehicle in category['vehicles']:
            record = {
                'category': category['category'].encode('utf-8'),
                'vehicle_text': vehicle['text'].encode('utf-8'),
                'vehicle_url': vehicle['url'].encode('utf-8')
            }
            scraperwiki.sqlite.save(
                unique_keys=['category', 'vehicle_text'],
                data=record
            )
            total_records += 1
    
    print "Successfully saved %d records across %d categories" % (total_records, len(combat_data))
