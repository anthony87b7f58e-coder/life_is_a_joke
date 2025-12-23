from flask import Flask, jsonify, render_template
import random
import os

app = Flask(__name__)

# Collection of jokes
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a fake noodle? An impasta!",
    "How does a penguin build its house? Igloos it together!",
    "Why did the math book look so sad? Because it had too many problems!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why couldn't the bicycle stand up by itself? It was two tired!",
    "What did one wall say to the other? I'll meet you at the corner!",
    "Why did the coffee file a police report? It got mugged!"
]

@app.route('/')
def home():
    """Home page with a random joke"""
    return render_template('index.html')

@app.route('/api/joke')
def get_joke():
    """API endpoint to get a random joke"""
    joke = random.choice(JOKES)
    return jsonify({
        'joke': joke,
        'total_jokes': len(JOKES)
    })

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'life_is_a_joke'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
