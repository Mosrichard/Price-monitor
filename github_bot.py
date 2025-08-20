import requests
import json
import os

BOT_TOKEN = '8268995077:AAGq3egb-Ffwfq85AIIwVe_CjFagzy2pM5k'
CHAT_ID = '1400730682'

# Current prices
current_prices = {
    'OnePlus Buds 3': [
        ('Amazon', 5999, 'https://www.amazon.in/dp/B0CSTJBQB8'),
        ('Flipkart', 5999, 'https://www.flipkart.com/oneplus-buds-3-bluetooth-truly-wireless-earbuds/p/itm6c6d5c0e1b4e5'),
        ('Croma', 5999, 'https://www.croma.com/oneplus-buds-3'),
        ('JioMart', 5999, 'https://www.jiomart.com/p/electronics/oneplus-buds-3-bluetooth-earbuds-splendid-blue-e509a/607698196')
    ],
    'OnePlus Nord Buds 2': [
        ('Amazon', 2999, 'https://www.amazon.in/dp/B0BYX7VYQZ'),
        ('Flipkart', 2899, 'https://www.flipkart.com/oneplus-nord-buds-2-bluetooth-truly-wireless-earbuds/p/itm123'),
        ('Croma', 2999, 'https://www.croma.com/oneplus-nord-buds-2'),
        ('JioMart', 2799, 'https://www.jiomart.com/p/electronics/oneplus-nord-buds-2/123')
    ],
    'OnePlus Nord Buds 2r': [
        ('Amazon', 1999, 'https://www.amazon.in/oneplus-nord-buds-2r'),
        ('Flipkart', 1899, 'https://www.flipkart.com/oneplus-nord-buds-2r'),
        ('Croma', 1999, 'https://www.croma.com/oneplus-nord-buds-2r'),
        ('JioMart', 1799, 'https://www.jiomart.com/p/electronics/oneplus-nord-buds-2r/456')
    ]
}

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
    message = "🎧 OnePlus Earbuds Current Prices:\n\n"
    
    all_results = []
    for product_name, price_data in current_prices.items():
        message += f"📱 {product_name}:\n"
        for site, price, url in price_data:
            message += f"💰 {site}: ₹{price:,}\n🔗 {url}\n\n"
            all_results.append((product_name, site, price, url))
    
    # Find best deal
    best_deal = min(all_results, key=lambda x: x[2])
    message += f"🏆 BEST DEAL: {best_deal[0]} - ₹{best_deal[2]:,} on {best_deal[1]}\n🛒 {best_deal[3]}"
    
    send_message(message)

def check_price_drops():
    """Check for price drops and send alerts"""
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
                if current_price <= 1499:
                    high_alert = f"🚨🚨 HIGH ALERT! 🚨🚨\n\n🔥 {product_site}\n💰 ONLY ₹{current_price:,}!\n⚡ UNDER ₹1499 TARGET!\n\n🛒 BUY NOW: {url}"
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