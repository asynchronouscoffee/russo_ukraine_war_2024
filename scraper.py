import requests
from bs4 import BeautifulSoup
import scraperwiki
from urllib.parse import urljoin

BASE_URL = 'https://www.oryxspioenkop.com'

def get_absolute_url(path):
    """Handle URL joining safely"""
    return urljoin(BASE_URL, path) if path else ''

def scrape_data():
    try:
        # Configure request
        url = '{}/2022/02/attack-on-europe-documenting-ukrainian.html'.format(BASE_URL)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
        
        # Fetch page
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Parse content
        soup = BeautifulSoup(response.content, 'html.parser')
        records = []
        
        # Find all category headers
        for h3 in soup.find_all('h3', class_='mw-headline'):
            category = h3.get_text(strip=True)
            current_sibling = h3.find_next_sibling()
            
            # Collect vehicle links under category
            while current_sibling and current_sibling.name != 'h3':
                if current_sibling.name == 'a':
                    link = current_sibling.get('href', '')
                    record = {
                        'category': category,
                        'vehicle': current_sibling.get_text(strip=True),
                        'url': get_absolute_url(link)
                    }
                    records.append(record)
                current_sibling = current_sibling.find_next_sibling()
        
        return records
    
    except Exception as e:
        print('Scraping error: {}'.format(str(e)))
        return []

if __name__ == '__main__':
    # Initialize database
    scraperwiki.sql.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            category TEXT,
            vehicle TEXT,
            url TEXT,
            UNIQUE(category, vehicle)
        )
    ''')
    
    # Scrape and save data
    data = scrape_data()
    for idx, record in enumerate(data, 1):
        scraperwiki.sql.save(
            unique_keys=['category', 'vehicle'],
            data=record,
            table_name='vehicles'
        )
    
    print('Successfully stored {} vehicle records'.format(len(data)))
