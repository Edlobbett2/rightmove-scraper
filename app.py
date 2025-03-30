import re
import json
import requests
from flask import Flask, request, jsonify, render_template_string
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# HTML template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rightmove Scraper</title>
</head>
<body>
    <h1>Rightmove Scraper</h1>
    <form method="post">
        <input type="text" name="url" placeholder="Enter Rightmove URL" required>
        <button type="submit">Scrape</button>
    </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        return jsonify({"message": "Form submitted", "url": url})
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("Starting Flask application...")
    print("Please access the application at: http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080, use_reloader=False)
