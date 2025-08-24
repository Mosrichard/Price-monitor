import requests
import json
import os
import re
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Product URLs to scrape
PRODUCT_URLS = {
    'OnePlus Buds 3': {
        'Amazon': 'https://www.amazon.in/dp/B0CSTJBQB8',
        'JioMart': 'https://www.jiomart.com/p/electronics/oneplus-buds-3-bluetooth-earbuds-splendid-blue-e509a/607698196'
    },
    'OnePlus Nord Buds 2': {
        'Amazon': 'https://www.amazon.in/dp/B0BYX7VYQZ',
        'JioMart': 'https://www.jiomart.com/p/electronics/oneplus-nord-buds-2/123'
    },
    'OnePlus Nord Buds 2r': {
        'Amazon': 'https://www.amazon.in/oneplus-nord-buds-2r',
        'JioMart': 'https://www.jiomart.com/p/electronics/oneplus-nord-buds-2r/456'
    }
}

def scrape_price(url):
    """Scrape price from product URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all price elements
        price_texts = soup.find_all(string=re.compile(r'₹[\d,]+'))
        
        prices = []
        for text in price_texts:
            matches = re.findall(r'₹([\d,]+)', text)
            for match in matches:
                price = int(match.replace(',', ''))
                if 500 <= price <= 15000:  # Valid earbuds price range
                    prices.append(price)
        
        return min(prices) if prices else None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_current_prices():
    """Scrape current prices from all sites"""
    current_prices = {}
    
    for product_name, sites in PRODUCT_URLS.items():
        current_prices[product_name] = []
        print(f"Scraping {product_name}...")
        
        for site_name, url in sites.items():
            price = scrape_price(url)
            if price:
                current_prices[product_name].append((site_name, price, url))
                print(f"  ✅ {site_name}: ₹{price:,}")
            else:
                print(f"  ❌ {site_name}: Could not get price")
    
    return current_prices

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={'chat_id': CHAT_ID, 'text': text})
    return response.status_code == 200

def get_updates():
    """Check for /price commands and respond"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url, params={'limit': 10})
        updates = response.json()
        
        if updates.get('ok') and updates.get('result'):
            for update in updates['result']:
                if 'message' in update:
                    message = update['message']
                    text = message.get('text', '').lower()
                    
                    if text == '/price':
                        print("📱 /price command found - sending prices")
                        send_price_message()
                        
                        # Mark message as read
                        offset_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                        requests.get(offset_url, params={'offset': update['update_id'] + 1})
                        
    except Exception as e:
        print(f"Error checking updates: {e}")

def send_price_message():
    # Get live scraped prices
    current_prices = get_current_prices()
    
    if not any(current_prices.values()):
        send_message("❌ Could not fetch current prices. Please try again later.")
        return
    
    message = "🎧 OnePlus Earbuds - Live Prices:\n\n"
    
    all_results = []
    for product_name, price_data in current_prices.items():
        if price_data:  # Only show products with available prices
            message += f"📱 {product_name}:\n"
            for site, price, url in price_data:
                message += f"💰 {site}: ₹{price:,}\n🔗 {url}\n\n"
                all_results.append((product_name, site, price, url))
    
    if all_results:
        # Find best deal
        best_deal = min(all_results, key=lambda x: x[2])
        message += f"🏆 BEST DEAL: {best_deal[0]} - ₹{best_deal[2]:,} on {best_deal[1]}\n🛒 {best_deal[3]}"
    
    send_message(message)

def check_price_drops():
    """Check for price drops and send alerts"""
    # Get live scraped prices
    current_prices = get_current_prices()
    
    # Use environment variable for GitHub Actions persistence
    last_prices_str = os.environ.get('LAST_PRICES', '{}')
    try:
        last_prices = json.loads(last_prices_str)
    except:
        last_prices = {}
    
    current_flat = {}
    for product, price_list in current_prices.items():
        for site, price, url in price_list:
            key = f"{product}_{site}"
            current_flat[key] = {'price': price, 'url': url}
            
            # Check for price drops
            if key in last_prices:
                current_price = price
                last_price = last_prices[key]['price']
                
                if current_price < last_price:
                    product_site = key.replace('_', ' - ')
                    drop = last_price - current_price
                    
                    alert = f"🚨 PRICE DROP ALERT! 🚨\n\n📱 {product_site}\n📉 ₹{last_price:,} → ₹{current_price:,}\n💸 You Save: ₹{drop:,}\n\n🛒 BUY NOW: {url}"
                    if send_message(alert):
                        print(f"✅ Price drop alert sent for {product_site}")
            
            # High alert for items under ₹1499
            if price <= 1499:
                product_site = key.replace('_', ' - ')
                high_alert = f"🚨🚨 HIGH ALERT! 🚨🚨\n\n🔥 {product_site}\n💰 ONLY ₹{price:,}!\n⚡ UNDER ₹1499 TARGET!\n\n🛒 BUY NOW: {url}"
                send_message(high_alert)
    
    print(f"✅ Checked {len(current_flat)} products for price changes")

def main():
    print("🤖 GitHub Actions Price Bot Running...")
    
    # Check for /price commands
    get_updates()
    
    # Check for price drops
    check_price_drops()
    
    print("✅ Bot run completed!")

if __name__ == "__main__":
    main()