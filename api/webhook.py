from http.server import BaseHTTPRequestHandler
import json
import requests

BOT_TOKEN = '8268995077:AAGq3egb-Ffwfq85AIIwVe_CjFagzy2pM5k'

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data.decode('utf-8'))
            
            if 'message' in update:
                message = update['message']
                text = message.get('text', '').lower()
                chat_id = message['chat']['id']
                
                if text == '/price':
                    price_message = """🎧 OnePlus Earbuds - All Sites Prices:

📱 OnePlus Buds 3:
💰 Amazon: ₹5,999
🔗 https://www.amazon.in/dp/B0CSTJBQB8
💰 Flipkart: ₹5,999
🔗 https://www.flipkart.com/oneplus-buds-3
💰 Croma: ₹6,299
🔗 https://www.croma.com/oneplus-buds-3
💰 JioMart: ₹5,999
🔗 https://www.jiomart.com/p/electronics/oneplus-buds-3

📱 OnePlus Nord Buds 2:
💰 Amazon: ₹2,999
🔗 https://www.amazon.in/dp/B0BYX7VYQZ
💰 Flipkart: ₹2,899
🔗 https://www.flipkart.com/oneplus-nord-buds-2
💰 Croma: ₹2,999
🔗 https://www.croma.com/oneplus-nord-buds-2
💰 JioMart: ₹2,799
🔗 https://www.jiomart.com/p/electronics/oneplus-nord-buds-2

📱 OnePlus Nord Buds 2r:
💰 Amazon: ₹1,999
🔗 https://www.amazon.in/oneplus-nord-buds-2r
💰 Flipkart: ₹1,899
🔗 https://www.flipkart.com/oneplus-nord-buds-2r
💰 Croma: ₹1,999
🔗 https://www.croma.com/oneplus-nord-buds-2r
💰 JioMart: ₹1,799
🔗 https://www.jiomart.com/p/electronics/oneplus-nord-buds-2r

🏆 BEST DEAL: OnePlus Nord Buds 2r - ₹1,799 on JioMart
🛒 https://www.jiomart.com/p/electronics/oneplus-nord-buds-2r"""
                    
                    # Send message
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    requests.post(url, data={'chat_id': chat_id, 'text': price_message})
        
        except Exception as e:
            print(f"Error: {e}")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')