"""
Integration tests for API endpoints
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from phase1.src.api.app import app as flask_app

@pytest.fixture
def app():
    """Create test Flask application"""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return flask_app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_index_route(client):
    """Test the index route"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['service'] == 'Revenue Tracking API'
    assert data['version'] == '1.0.0'
    assert 'endpoints' in data

def test_health_route(client):
    """Test the health check route"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_create_payment_intent_missing_data(client):
    """Test payment intent creation with missing data"""
    response = client.post('/api/payments/create-payment-intent',
                           json={})
    # Should handle gracefully even with missing data
    assert response.status_code in [200, 400]

def test_list_payments(client):
    """Test listing payments"""
    response = client.get('/api/payments/list?user_id=123')
    assert response.status_code == 200
    data = response.get_json()
    assert 'payments' in data
    assert 'total' in data

def test_affiliate_stats(client):
    """Test getting affiliate stats"""
    response = client.get('/api/affiliates/stats/TESTCODE')
    assert response.status_code == 200
    data = response.get_json()
    assert 'affiliate_code' in data
    assert 'total_referrals' in data
    assert 'total_earnings' in data

def test_check_content_access(client):
    """Test checking content access"""
    response = client.get('/api/content/check-access?user_id=123&content_id=course-101')
    assert response.status_code == 200
    data = response.get_json()
    assert 'has_access' in data

def test_list_services(client):
    """Test listing marketplace services"""
    response = client.get('/api/marketplace/services/list')
    assert response.status_code == 200
    data = response.get_json()
    assert 'services' in data
    assert 'total' in data

def test_dashboard_overview(client):
    """Test dashboard overview endpoint"""
    response = client.get('/api/dashboard/overview?days=30')
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_revenue' in data
    assert 'period_days' in data

def test_revenue_by_day(client):
    """Test revenue by day endpoint"""
    response = client.get('/api/dashboard/revenue-by-day?days=7')
    assert response.status_code == 200
    data = response.get_json()
    assert 'daily_revenue' in data
    assert isinstance(data['daily_revenue'], list)

def test_revenue_by_source(client):
    """Test revenue by source endpoint"""
    response = client.get('/api/dashboard/revenue-by-source')
    assert response.status_code == 200
    data = response.get_json()
    assert 'payments' in data
    assert 'subscriptions' in data
    assert 'marketplace' in data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
