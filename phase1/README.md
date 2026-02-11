# Phase 1: Revenue Agent System

## Overview

Phase 1 provides a comprehensive revenue tracking and monetization system built with Flask. It includes:

- **Stripe Payment Processing**: Complete payment flow with webhook support
- **Affiliate Tracking System**: Track referrals and calculate commissions
- **Content Monetization**: Manage content purchases and subscriptions
- **Services Marketplace**: List services and manage bookings
- **Revenue Dashboard**: Real-time analytics and reporting

## Features

### 1. Payment Processing
- Create and confirm payments via Stripe
- Webhook handling for payment events
- Refund processing
- Multiple currency support

### 2. Affiliate System
- Automatic affiliate code generation
- Referral tracking with cookies
- Commission calculation (configurable rate)
- Payout processing
- Detailed analytics per affiliate

### 3. Content Monetization
- One-time content purchases
- Subscription management (monthly/annual)
- Access control and expiration
- Subscription cancellation

### 4. Services Marketplace
- Service listing creation
- Category-based browsing
- Booking management
- Marketplace fee calculation
- Provider payout calculation

### 5. Revenue Dashboard
- Real-time revenue overview
- Daily revenue breakdown
- Revenue by source analysis
- Subscription metrics
- Top performers tracking
- Recent transaction history

## Quick Start

### Installation

```bash
cd phase1

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy environment file:
```bash
cp ../.env.example ../.env
```

2. Edit `.env` with your credentials:
```bash
STRIPE_API_KEY=sk_test_your_key
DATABASE_URL=postgresql://user:pass@localhost:5432/automation_db
SECRET_KEY=your_secret_key
```

### Initialize Database

```bash
python src/utils/init_db.py
```

### Start Server

```bash
./start.sh
```

Or manually:
```bash
python src/api/app.py
```

The API will be available at `http://localhost:5000`

## API Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

### Quick API Test

```bash
# Health check
curl http://localhost:5000/health

# API info
curl http://localhost:5000/

# Create payment intent
curl -X POST http://localhost:5000/api/payments/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "currency": "usd",
    "description": "Test payment",
    "user_id": 123
  }'
```

## Testing

### Run Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Architecture

### Database Models

- **Payment**: Payment transactions
- **Affiliate**: Affiliate accounts
- **AffiliateCommission**: Commission records
- **AffiliateReferral**: Referral tracking
- **ContentAccess**: Content purchase records
- **Subscription**: Subscription management
- **ServiceListing**: Marketplace services
- **ServiceBooking**: Service bookings
- **RevenueMetric**: Aggregated metrics

### API Structure

```
phase1/
├── src/
│   ├── api/
│   │   ├── app.py              # Main Flask application
│   │   ├── payments.py         # Payment endpoints
│   │   ├── affiliates.py       # Affiliate endpoints
│   │   ├── content.py          # Content endpoints
│   │   ├── marketplace.py      # Marketplace endpoints
│   │   └── dashboard.py        # Dashboard endpoints
│   ├── models/
│   │   └── revenue_models.py   # Database models
│   └── utils/
│       └── init_db.py          # Database initialization
├── tests/
│   └── test_basic.py           # Unit tests
├── requirements.txt            # Python dependencies
└── start.sh                    # Startup script
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | development |
| `API_PORT` | API port | 5000 |
| `DATABASE_URL` | PostgreSQL connection | sqlite:///revenue.db |
| `STRIPE_API_KEY` | Stripe secret key | Required |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | Required |
| `AFFILIATE_COMMISSION_RATE` | Commission rate (0-1) | 0.20 |
| `MARKETPLACE_FEE_PERCENTAGE` | Marketplace fee (0-1) | 0.15 |
| `CONTENT_ACCESS_DURATION` | Days of access | 365 |

## Integration with Other Phases

Phase 1 can be integrated with:

- **Phase 3**: Workflow orchestration for payment processing
- **Phase 4**: Event bus for payment notifications

Example event publishing:
```python
from phase4.src.event_bus.bus import EventBus

bus = EventBus()
await bus.publish('payment.completed', {
    'payment_id': payment.id,
    'amount': payment.amount,
    'user_id': payment.user_id
})
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file
2. **Stripe Webhooks**: Always verify signatures
3. **API Authentication**: Implement JWT/OAuth2 in production
4. **HTTPS**: Use SSL/TLS in production
5. **Rate Limiting**: Implement rate limiting for APIs
6. **Input Validation**: Validate all user inputs
7. **Database**: Use parameterized queries (SQLAlchemy handles this)

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions including:

- Docker deployment
- Heroku deployment
- AWS EC2 deployment
- Database migrations
- Monitoring setup
- Backup strategies

## Troubleshooting

### Common Issues

**Import errors when running app:**
```bash
# Make sure you're in the right directory and venv is activated
cd phase1
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
```

**Stripe webhook verification fails:**
- Use Stripe CLI for local testing: `stripe listen --forward-to localhost:5000/api/payments/webhook`
- Verify webhook secret matches Stripe dashboard

**Database connection fails:**
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL format: `postgresql://user:pass@host:port/dbname`

## Future Enhancements

- [ ] Add JWT authentication
- [ ] Implement rate limiting
- [ ] Add Redis caching
- [ ] Create admin dashboard UI
- [ ] Add email notifications
- [ ] Implement invoice generation
- [ ] Add tax calculation
- [ ] Multi-currency support
- [ ] Fraud detection
- [ ] Export reports (CSV, PDF)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

See main repository LICENSE file.

## Support

- Documentation: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- Deployment: [DEPLOYMENT.md](./DEPLOYMENT.md)
- Issues: GitHub Issues
