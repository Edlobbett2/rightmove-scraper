from flask import Flask, jsonify, render_template_string, request
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)

# HTML template for our test page
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Rightmove Property Scraper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .property {
            border: 1px solid #ddd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
        }
        .price {
            color: #2b8a3e;
            font-weight: bold;
            font-size: 1.2em;
        }
        .address {
            color: #333;
            margin: 10px 0;
        }
        .rooms {
            color: #666;
        }
        .form-container {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="url"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background: #2b8a3e;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #2f9e44;
        }
        .error {
            color: #e03131;
            margin: 10px 0;
        }
        .success {
            color: #2b8a3e;
            margin: 10px 0;
        }
        .status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <h1>Rightmove Property Scraper</h1>
    
    <div class="form-container">
        <form method="POST" action="/scrape">
            <div class="form-group">
                <label for="url">Rightmove Property URL:</label>
                <input type="url" id="url" name="url" required 
                       placeholder="https://www.rightmove.co.uk/properties/12345678">
                <small style="color: #666;">Paste the URL of a single property page</small>
            </div>
            <button type="submit">Scrape Property Details</button>
        </form>
    </div>

    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}

    {% if success %}
    <div class="success">{{ success }}</div>
    {% endif %}

    {% if make_status %}
    <div class="status">{{ make_status }}</div>
    {% endif %}

    {% if properties %}
    <h2>Property Details</h2>
    <div id="properties">
        {% for property in properties %}
        <div class="property">
            <div class="price">{{ property.price }}</div>
            <div class="address">{{ property.address }}</div>
            <div class="rooms">{{ property.rooms }}</div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
'''

def send_to_make(property_data):
    try:
        # Replace this URL with your Make.com webhook URL
        make_webhook_url = "https://hook.eu2.make.com/7ejahqwjswer61ae36ffw0bvacbdhfs5"
        
        # Extract ad ID from the source URL
        ad_id = property_data["source_url"].split("/")[-1]
        
        # Convert bedrooms and bathrooms to integers if they exist
        bedrooms = int(property_data["rooms_info"].get("bedrooms", 0))
        bathrooms = int(property_data["rooms_info"].get("bathrooms", 0))
        
        # Clean up the price string - remove the pound symbol, spaces, and 'pcm'
        price = property_data["price"].replace("£", "").replace(" ", "").replace("pcm", "")
        
        # Prepare the data for Make.com
        make_data = {
            "ad_id": ad_id,
            "price": price,
            "address": property_data["address"],
            "bedrooms": bedrooms,
            "bathrooms": bathrooms
        }
        
        print("\n=== Sending to Make.com ===")
        print(f"Data being sent: {json.dumps(make_data, indent=2)}")
        
        # Send data to Make.com webhook
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(make_webhook_url, json=make_data, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        print("=== End Make.com Response ===\n")
        
        if response.status_code != 200:
            return f"Error sending to Make.com: Status {response.status_code} - {response.text}"
        
        return f"Successfully sent to Make.com (Ad ID: {ad_id})"
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error sending to Make.com: {str(e)}"
        print(f"\nError: {error_msg}")
        return error_msg
    except ValueError as e:
        error_msg = f"Data formatting error: {str(e)}"
        print(f"\nError: {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error sending to Make.com: {str(e)}"
        print(f"\nError: {error_msg}")
        return error_msg

def scrape_rightmove(url):
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all text content with better formatting
        text_content = ' '.join(soup.stripped_strings)
        
        # Debug print the full text content
        print("\n=== Full Text Content ===")
        print(text_content)
        print("=== End Full Text Content ===\n")
        
        # Extract property details from text content
        try:
            # Extract address - it appears after "BUILT FOR RENTERS"
            address_start = text_content.find("BUILT FOR RENTERS") + len("BUILT FOR RENTERS")
            address_end = text_content.find("£", address_start)
            address = text_content[address_start:address_end].strip()
            
            # Extract price - it appears after the address
            price_start = text_content.find("£", address_end)
            price_end = text_content.find("£", price_start + 1)
            price = text_content[price_start:price_end].strip()
            
            # Extract rooms - look for both BEDROOMS and BATHROOMS
            rooms_info = {}
            
            # Find bedrooms
            bedrooms_start = text_content.find("BEDROOMS")
            if bedrooms_start != -1:
                bedrooms_text = text_content[bedrooms_start:bedrooms_start+30]
                print("\n=== Bedrooms Text ===")
                print(bedrooms_text)
                print("=== End Bedrooms Text ===\n")
                parts = bedrooms_text.split()
                if len(parts) > 1:
                    rooms_info['bedrooms'] = parts[1]
            
            # Find bathrooms
            bathrooms_start = text_content.find("BATHROOMS")
            if bathrooms_start != -1:
                bathrooms_text = text_content[bathrooms_start:bathrooms_start+30]
                print("\n=== Bathrooms Text ===")
                print(bathrooms_text)
                print("=== End Bathrooms Text ===\n")
                parts = bathrooms_text.split()
                if len(parts) > 1:
                    rooms_info['bathrooms'] = parts[1]
            
            # Format rooms info
            rooms = f"Bedrooms: {rooms_info.get('bedrooms', 'N/A')}, Bathrooms: {rooms_info.get('bathrooms', 'N/A')}"
            
            # Debug print
            print("\n=== Extracted Information ===")
            print(f"Price: {price}")
            print(f"Address: {address}")
            print(f"Rooms Info: {rooms}")
            print("=== End Extracted Information ===\n")
            
            # Prepare property data for Make.com
            property_data = {
                "price": price,
                "address": address,
                "rooms": rooms,
                "rooms_info": rooms_info,
                "source_url": url
            }
            
            return property_data
            
        except Exception as e:
            print(f"Error extracting property details: {str(e)}")
            raise Exception(f"Error extracting property details: {str(e)}")
                
    except Exception as e:
        print(f"Error scraping Rightmove: {str(e)}")
        raise Exception(f"Error scraping Rightmove: {str(e)}")

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url', '')
    if not url:
        return render_template_string(HTML_TEMPLATE, error="Please enter a URL")
    
    try:
        property_data = scrape_rightmove(url)
        
        # Format data for display
        properties = [{
            "price": property_data["price"],
            "address": property_data["address"],
            "rooms": property_data["rooms"]
        }]
        
        # Send to Make.com
        make_status = send_to_make(property_data)
        
        return render_template_string(HTML_TEMPLATE, 
                                   properties=properties,
                                   success="Successfully scraped property details",
                                   make_status=make_status)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=str(e))

@app.route('/api/properties')
def get_properties():
    mock_properties = {
        "properties": [
            {
                "id": "123456",
                "price": "£500,000",
                "address": "123 Test Street",
                "description": "A lovely test property"
            },
            {
                "id": "789012",
                "price": "£750,000",
                "address": "456 Sample Road",
                "description": "Another test property"
            }
        ]
    }
    return jsonify(mock_properties)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask server on port {port}...")
    print("Press Ctrl+C to stop the server")
    print(f"You can view the web interface at: http://localhost:{port}")
    print("You can access the API at: http://localhost:8000/api/properties")
    app.run(host='0.0.0.0', port=port) 