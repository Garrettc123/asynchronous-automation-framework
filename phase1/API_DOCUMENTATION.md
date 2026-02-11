# Revenue Tracking API Documentation

## Overview

The Revenue Tracking API provides comprehensive endpoints for managing payments, affiliate tracking, content monetization, services marketplace, and revenue analytics.

**Base URL**: `http://localhost:5000/api`

**Version**: 1.0.0

## Authentication

Currently, the API uses simple user_id based authentication. In production, implement proper JWT or OAuth2 authentication.

## Environment Configuration

Create a `.env` file based on `.env.example` with your configuration:

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env
```

### Required Environment Variables

- `STRIPE_API_KEY`: Your Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook signing secret
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key for sessions

## API Endpoints

### 1. Payments API (`/api/payments`)

#### Create Payment Intent

Creates a Stripe Payment Intent for processing payments.

**Endpoint**: `POST /api/payments/create-payment-intent`

**Request Body**:
```json
{
  "amount": 5000,
  "currency": "usd",
  "description": "Purchase of premium course",
  "user_id": 123,
  "affiliate_code": "ABC123XY"
}
```

**Response**:
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx",
  "status": "success"
}
```

#### Confirm Payment

Confirms a payment and records it in the database.

**Endpoint**: `POST /api/payments/confirm-payment`

**Request Body**:
```json
{
  "payment_intent_id": "pi_xxx"
}
```

**Response**:
```json
{
  "status": "success",
  "payment_id": "pi_xxx",
  "amount": 50.00,
  "currency": "usd"
}
```

#### List Payments

Retrieves all payments for a user.

**Endpoint**: `GET /api/payments/list?user_id=123`

**Response**:
```json
{
  "payments": [
    {
      "id": 1,
      "stripe_payment_id": "pi_xxx",
      "amount": 50.00,
      "status": "completed",
      "created_at": "2026-02-11T14:30:00Z"
    }
  ],
  "total": 1
}
```

#### Refund Payment

Processes a refund for a payment.

**Endpoint**: `POST /api/payments/refund`

**Request Body**:
```json
{
  "payment_intent_id": "pi_xxx",
  "amount": 5000
}
```

#### Stripe Webhook

Handles Stripe webhook events (payment success, failures, refunds).

**Endpoint**: `POST /api/payments/webhook`

**Events Handled**:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.refunded`

### 2. Affiliates API (`/api/affiliates`)

#### Register Affiliate

Registers a new affiliate and generates a unique affiliate code.

**Endpoint**: `POST /api/affiliates/register`

**Request Body**:
```json
{
  "user_id": 123
}
```

**Response**:
```json
{
  "status": "success",
  "affiliate_code": "ABC123XY",
  "commission_rate": 0.20,
  "referral_link": "https://yourdomain.com/ref/ABC123XY"
}
```

#### Track Referral

Tracks a new referral from an affiliate link.

**Endpoint**: `POST /api/affiliates/track-referral`

**Request Body**:
```json
{
  "affiliate_code": "ABC123XY",
  "referred_user_id": 456
}
```

#### Calculate Commission

Calculates and records commission for a purchase.

**Endpoint**: `POST /api/affiliates/calculate-commission`

**Request Body**:
```json
{
  "payment_id": 1,
  "affiliate_code": "ABC123XY",
  "amount": 100.00
}
```

**Response**:
```json
{
  "status": "success",
  "commission_amount": 20.00,
  "commission_rate": 0.20
}
```

#### Get Affiliate Stats

Retrieves statistics for an affiliate.

**Endpoint**: `GET /api/affiliates/stats/ABC123XY`

**Response**:
```json
{
  "affiliate_code": "ABC123XY",
  "total_referrals": 25,
  "total_earnings": 500.00,
  "pending_commissions": 100.00,
  "paid_commissions": 400.00,
  "commission_rate": 0.20,
  "is_active": true,
  "member_since": "2026-01-01T00:00:00Z"
}
```

#### Get Commissions

Retrieves commission history for an affiliate.

**Endpoint**: `GET /api/affiliates/commissions/ABC123XY`

**Response**:
```json
{
  "commissions": [
    {
      "id": 1,
      "amount": 20.00,
      "status": "paid",
      "created_at": "2026-02-10T10:00:00Z"
    }
  ],
  "total_earned": 500.00,
  "total_pending": 100.00
}
```

#### Process Payout

Processes payout for affiliate commissions.

**Endpoint**: `POST /api/affiliates/payout`

**Request Body**:
```json
{
  "affiliate_code": "ABC123XY",
  "amount": 100.00
}
```

### 3. Content Monetization API (`/api/content`)

#### Purchase Content

Grants access to content after purchase.

**Endpoint**: `POST /api/content/purchase`

**Request Body**:
```json
{
  "user_id": 123,
  "content_id": "course-101",
  "content_type": "course",
  "price": 99.99,
  "payment_id": 1
}
```

**Response**:
```json
{
  "status": "success",
  "content_id": "course-101",
  "access_granted": true,
  "expires_at": "2027-02-11T14:30:00Z"
}
```

#### Check Content Access

Checks if a user has access to specific content.

**Endpoint**: `GET /api/content/check-access?user_id=123&content_id=course-101`

**Response**:
```json
{
  "has_access": true,
  "expires_at": "2027-02-11T14:30:00Z",
  "content_type": "course"
}
```

#### Create Subscription

Creates a new subscription for a user.

**Endpoint**: `POST /api/content/subscriptions/create`

**Request Body**:
```json
{
  "user_id": 123,
  "plan_name": "premium",
  "plan_price": 29.99,
  "billing_period": "monthly"
}
```

**Response**:
```json
{
  "status": "success",
  "subscription_id": "sub_123",
  "plan_name": "premium",
  "next_billing_date": "2026-03-11T14:30:00Z"
}
```

#### Get User Subscription

Retrieves a user's active subscription.

**Endpoint**: `GET /api/content/subscriptions/123`

#### Cancel Subscription

Cancels a user's subscription.

**Endpoint**: `POST /api/content/subscriptions/cancel`

**Request Body**:
```json
{
  "subscription_id": "sub_xxx"
}
```

#### List User Content

Lists all content purchases for a user.

**Endpoint**: `GET /api/content/list?user_id=123`

### 4. Services Marketplace API (`/api/marketplace`)

#### Create Service Listing

Creates a new service listing in the marketplace.

**Endpoint**: `POST /api/marketplace/services/create`

**Request Body**:
```json
{
  "provider_user_id": 123,
  "title": "Web Development Consulting",
  "description": "Expert web development services",
  "category": "consulting",
  "price": 150.00,
  "currency": "USD"
}
```

**Response**:
```json
{
  "status": "success",
  "service_id": "srv_123",
  "title": "Web Development Consulting",
  "price": 150.00
}
```

#### List Services

Lists all active service listings.

**Endpoint**: `GET /api/marketplace/services/list?category=consulting`

**Response**:
```json
{
  "services": [
    {
      "service_id": "srv_123",
      "title": "Web Development Consulting",
      "price": 150.00,
      "category": "consulting"
    }
  ],
  "total": 1
}
```

#### Get Service Details

Gets details of a specific service.

**Endpoint**: `GET /api/marketplace/services/srv_123`

#### Create Booking

Books a service.

**Endpoint**: `POST /api/marketplace/bookings/create`

**Request Body**:
```json
{
  "service_id": "srv_123",
  "buyer_user_id": 456,
  "scheduled_date": "2026-02-15T10:00:00Z",
  "payment_id": 1,
  "price": 150.00
}
```

**Response**:
```json
{
  "status": "success",
  "booking_id": "book_123",
  "marketplace_fee": 22.50,
  "provider_payout": 127.50
}
```

#### Confirm Booking

Confirms a service booking.

**Endpoint**: `POST /api/marketplace/bookings/book_123/confirm`

#### Complete Booking

Marks a booking as completed.

**Endpoint**: `POST /api/marketplace/bookings/book_123/complete`

#### Get User Bookings

Gets all bookings for a user.

**Endpoint**: `GET /api/marketplace/bookings/user/123?role=buyer`

### 5. Revenue Dashboard API (`/api/dashboard`)

#### Get Dashboard Overview

Retrieves high-level revenue metrics.

**Endpoint**: `GET /api/dashboard/overview?days=30`

**Response**:
```json
{
  "period_days": 30,
  "total_revenue": 15000.00,
  "payment_revenue": 8000.00,
  "subscription_revenue": 4000.00,
  "marketplace_revenue": 2000.00,
  "content_revenue": 1000.00,
  "affiliate_commissions_paid": 500.00,
  "total_transactions": 150,
  "active_subscriptions": 50,
  "new_customers": 25,
  "average_transaction_value": 100.00
}
```

#### Get Revenue by Day

Gets daily revenue breakdown.

**Endpoint**: `GET /api/dashboard/revenue-by-day?days=30`

**Response**:
```json
{
  "daily_revenue": [
    {
      "date": "2026-02-11",
      "total_revenue": 500.00,
      "payment_revenue": 300.00,
      "subscription_revenue": 150.00,
      "marketplace_revenue": 50.00,
      "transaction_count": 10
    }
  ],
  "period_start": "2026-01-12",
  "period_end": "2026-02-11"
}
```

#### Get Revenue by Source

Gets revenue breakdown by source.

**Endpoint**: `GET /api/dashboard/revenue-by-source`

**Response**:
```json
{
  "payments": {
    "amount": 8000.00,
    "percentage": 53.3,
    "count": 80
  },
  "subscriptions": {
    "amount": 4000.00,
    "percentage": 26.7,
    "count": 50
  },
  "marketplace": {
    "amount": 2000.00,
    "percentage": 13.3,
    "count": 15
  },
  "content": {
    "amount": 1000.00,
    "percentage": 6.7,
    "count": 20
  }
}
```

#### Get Top Affiliates

Gets top performing affiliates.

**Endpoint**: `GET /api/dashboard/top-affiliates?limit=10`

#### Get Subscription Metrics

Gets subscription-related metrics.

**Endpoint**: `GET /api/dashboard/subscription-metrics`

**Response**:
```json
{
  "active_subscriptions": 50,
  "new_subscriptions_30d": 10,
  "cancelled_subscriptions_30d": 2,
  "churn_rate": 4.0,
  "monthly_recurring_revenue": 1500.00,
  "average_subscription_value": 30.00
}
```

#### Get Marketplace Metrics

Gets marketplace-related metrics.

**Endpoint**: `GET /api/dashboard/marketplace-metrics`

#### Get Recent Transactions

Gets recent transactions.

**Endpoint**: `GET /api/dashboard/recent-transactions?limit=20`

## Error Handling

All endpoints return standard error responses:

```json
{
  "error": "Error message description"
}
```

HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

Implement rate limiting in production to prevent abuse.

## Testing

Run tests:
```bash
cd phase1
pytest tests/ -v
```

## Deployment

See `DEPLOYMENT.md` for deployment instructions.
