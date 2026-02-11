# Asynchronous Automation Framework - Complete System

**Version:** 4.1.0  
**Updated:** February 11, 2026  
**Status:** Production-Ready

## Overview

This is a complete, end-to-end asynchronous automation framework spanning 4 phases:

1. **Phase 1**: Revenue Agent System (Flask API)
2. **Phase 2**: Auto-Recovery & Linear Task Progression
3. **Phase 3**: Advanced Workflow Orchestration (DAG, Scheduling)
4. **Phase 4**: Event-Driven Architecture & ML Optimization

## Quick Start

### Option 1: Start Revenue API (Phase 1)

```bash
# Clone the repository
git clone https://github.com/Garrettc123/asynchronous-automation-framework.git
cd asynchronous-automation-framework/phase1

# Set up environment
cp ../.env.example ../.env
# Edit .env with your Stripe keys and database configuration

# Start the API
./start.sh
```

The Revenue API will be available at `http://localhost:5000`

### Option 2: Deploy All Phases

```bash
# Run the unified deployment script
chmod +x deploy-all-phases.sh
./deploy-all-phases.sh

# Start the system
cd automation_framework
./start.sh
```

## Phase Overview

### Phase 1: Revenue Agent System
Complete revenue tracking and monetization system with:
- **Stripe Payment Processing**: Payment intents, webhooks, refunds
- **Affiliate Tracking**: Automatic referral tracking and commission calculation
- **Content Monetization**: Purchase management and subscription handling
- **Services Marketplace**: Service listings and booking management
- **Revenue Dashboard**: Real-time analytics and reporting

**Tech Stack**: Flask, SQLAlchemy, Stripe SDK, PostgreSQL

**Documentation**: [phase1/README.md](phase1/README.md) | [API Docs](phase1/API_DOCUMENTATION.md)

### Phase 3: Workflow Orchestration
Advanced workflow engine with:
- DAG-based task execution
- Priority-based scheduling
- Parallel and sequential task support

### Phase 4: Event-Driven Architecture
Enterprise event bus with:
- Publish/subscribe pattern
- ML-based optimization
- Async event processing

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Phase 1: Revenue Agent System (Flask API)         │
│  - Stripe Payments                                  │
│  - Affiliate Tracking                               │
│  - Content & Marketplace                            │
│  - Revenue Dashboard                                │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Phase 4: Event Bus & ML Optimization               │
│  - Event-driven notifications                       │
│  - Predictive analytics                             │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: Workflow Engine & Task Scheduler          │
│  - Payment workflow orchestration                   │
│  - Automated processing                             │
└─────────────────────────────────────────────────────┘
```

## API Endpoints

### Revenue API (Phase 1)

- **Payments**: `/api/payments` - Create, confirm, refund payments
- **Affiliates**: `/api/affiliates` - Track referrals, calculate commissions
- **Content**: `/api/content` - Manage purchases and subscriptions
- **Marketplace**: `/api/marketplace` - Service listings and bookings
- **Dashboard**: `/api/dashboard` - Revenue analytics and metrics

See [API Documentation](phase1/API_DOCUMENTATION.md) for complete reference.

## Environment Configuration

Required environment variables:

```bash
# Stripe Configuration
STRIPE_API_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/automation_db

# API Configuration
SECRET_KEY=your-secret-key
API_PORT=5000
```

## Testing

### Phase 1 Tests
```bash
cd phase1
source venv/bin/activate
pytest tests/ -v
```

## Deployment

See deployment guides:
- [Phase 1 Deployment Guide](phase1/DEPLOYMENT.md)
- Docker, Heroku, and AWS EC2 options available

## Documentation

- **Phase 1**: [README](phase1/README.md) | [API Docs](phase1/API_DOCUMENTATION.md) | [Deployment](phase1/DEPLOYMENT.md)
- **Architecture**: See phase-specific documentation

## Contributing

Contributions welcome! Please see individual phase documentation for details.

## License

MIT License - See LICENSE file for details.
