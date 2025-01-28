import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"

def main():
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = []
    for h3 in soup.find_all('h3', class_='mw-headline'):
        category = h3.get_text(strip=True)
        vehicles = []
        
        sibling = h3.find_next_sibling()
        while sibling and sibling.name != 'h3':
            if sibling.name == 'a':
                link = sibling['href']
                if not link.startswith('http'):
                    link = f"https://www.oryxspioenkop.com{link}"
                vehicles.append({
                    'name': sibling.get_text(strip=True),
                    'url': link
                })
            sibling = sibling.find_next_sibling()
        
        data.append({'category': category, 'vehicles': vehicles})
    
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
