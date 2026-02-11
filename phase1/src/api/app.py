"""
Main Flask application for revenue tracking system
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///revenue.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STRIPE_API_KEY'] = os.getenv('STRIPE_API_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET')

# Initialize database
db = SQLAlchemy(app)

# Import and register blueprints
from phase1.src.api.payments import payments_bp
from phase1.src.api.affiliates import affiliates_bp
from phase1.src.api.content import content_bp
from phase1.src.api.marketplace import marketplace_bp
from phase1.src.api.dashboard import dashboard_bp

app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(affiliates_bp, url_prefix='/api/affiliates')
app.register_blueprint(content_bp, url_prefix='/api/content')
app.register_blueprint(marketplace_bp, url_prefix='/api/marketplace')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

@app.route('/')
def index():
    return jsonify({
        'service': 'Revenue Tracking API',
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'payments': '/api/payments',
            'affiliates': '/api/affiliates',
            'content': '/api/content',
            'marketplace': '/api/marketplace',
            'dashboard': '/api/dashboard'
        }
    })

@app.route('/health')
def health():
    from datetime import datetime
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'True') == 'True'
    app.run(host=os.getenv('API_HOST', '0.0.0.0'), port=port, debug=debug)
