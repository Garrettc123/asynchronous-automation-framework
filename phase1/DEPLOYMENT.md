# Deployment Configuration Guide

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)
- Stripe account

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/Garrettc123/asynchronous-automation-framework.git
cd asynchronous-automation-framework
```

### 2. Set Up Virtual Environment

```bash
cd phase1
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp ../.env.example ../.env

# Edit with your configuration
nano ../.env
```

**Required configurations:**
- `STRIPE_API_KEY`: Get from Stripe Dashboard → Developers → API Keys
- `STRIPE_WEBHOOK_SECRET`: Get from Stripe Dashboard → Webhooks
- `DATABASE_URL`: Your PostgreSQL connection string
- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`

### 5. Initialize Database

```bash
# Create database
createdb automation_db

# Initialize tables
python src/utils/init_db.py
```

### 6. Run Development Server

```bash
python src/api/app.py
```

The API will be available at `http://localhost:5000`

## Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Test Stripe Integration

1. Use Stripe test mode keys
2. Test cards: `4242 4242 4242 4242` (success), `4000 0000 0000 0002` (decline)
3. Use Stripe CLI for webhook testing:

```bash
stripe listen --forward-to localhost:5000/api/payments/webhook
```

## Production Deployment

### Option 1: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY phase1/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY phase1/ .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.api.app:app"]
```

Build and run:

```bash
docker build -t revenue-api .
docker run -p 5000:5000 --env-file .env revenue-api
```

### Option 2: Heroku Deployment

1. Create `Procfile`:

```
web: gunicorn --chdir phase1 src.api.app:app
```

2. Create `runtime.txt`:

```
python-3.10.12
```

3. Deploy:

```bash
heroku create your-app-name
heroku config:set STRIPE_API_KEY=your_key
heroku config:set DATABASE_URL=your_db_url
git push heroku main
```

### Option 3: AWS EC2 Deployment

1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:

```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx -y
```

4. Clone and setup:

```bash
git clone your-repo
cd asynchronous-automation-framework/phase1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

5. Configure Nginx reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. Create systemd service:

```ini
[Unit]
Description=Revenue API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/asynchronous-automation-framework/phase1
Environment="PATH=/home/ubuntu/asynchronous-automation-framework/phase1/venv/bin"
ExecStart=/home/ubuntu/asynchronous-automation-framework/phase1/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 src.api.app:app

[Install]
WantedBy=multi-user.target
```

7. Start service:

```bash
sudo systemctl enable revenue-api
sudo systemctl start revenue-api
```

## Database Migrations

When you modify models:

```bash
# Generate migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:5000/health
```

### Logging

Logs are written to stdout. Configure log aggregation:

- CloudWatch (AWS)
- Papertrail
- Datadog
- Sentry for error tracking

### Metrics

Integrate Prometheus/Grafana for monitoring:

- Request rate
- Response times
- Error rates
- Payment success rates

## Security Checklist

- [ ] Change `SECRET_KEY` to random value
- [ ] Use environment variables, never commit secrets
- [ ] Enable HTTPS (SSL/TLS certificates)
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Set up Stripe webhook signature verification
- [ ] Use strong database passwords
- [ ] Enable database SSL connections
- [ ] Implement proper authentication (JWT/OAuth2)
- [ ] Regular security updates
- [ ] Backup database regularly

## Stripe Configuration

### Set Up Webhook

1. Go to Stripe Dashboard → Webhooks
2. Click "Add endpoint"
3. URL: `https://your-domain.com/api/payments/webhook`
4. Events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
   - `customer.subscription.created`
   - `customer.subscription.deleted`

### Test Mode vs Live Mode

- Development: Use test keys (starts with `sk_test_`)
- Production: Use live keys (starts with `sk_live_`)

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple instances behind load balancer
- Use Redis for session storage
- Implement database connection pooling

### Database Optimization

- Add indexes on frequently queried fields
- Use database read replicas
- Implement caching layer (Redis)

### Background Jobs

For long-running tasks (commission calculations, reporting):

- Use Celery + Redis/RabbitMQ
- Process webhooks asynchronously

## Backup and Recovery

### Database Backups

```bash
# Backup
pg_dump automation_db > backup.sql

# Restore
psql automation_db < backup.sql
```

### Automated Backups

Set up daily automated backups:
- AWS RDS automated backups
- Cron job for PostgreSQL
- Cloud storage (S3, Google Cloud Storage)

## Troubleshooting

### Common Issues

**Issue**: Stripe webhook fails
- Verify webhook secret matches Stripe dashboard
- Check signature verification
- Review logs for error details

**Issue**: Database connection fails
- Check DATABASE_URL format
- Verify PostgreSQL is running
- Check firewall rules

**Issue**: CORS errors
- Configure Flask-CORS properly
- Add allowed origins to configuration

## Support

For issues or questions:
- GitHub Issues: https://github.com/Garrettc123/asynchronous-automation-framework/issues
- Documentation: See API_DOCUMENTATION.md
