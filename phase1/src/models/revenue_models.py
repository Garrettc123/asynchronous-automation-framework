"""
Database models for revenue tracking system
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    EXPIRED = "expired"

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    stripe_payment_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    affiliate_commission = relationship("AffiliateCommission", back_populates="payment", uselist=False)

class AffiliateCommission(Base):
    __tablename__ = 'affiliate_commissions'
    
    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey('affiliates.id'), nullable=False)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    commission_amount = Column(Float, nullable=False)
    commission_rate = Column(Float, nullable=False)
    status = Column(String(50), default='pending')
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    affiliate = relationship("Affiliate", back_populates="commissions")
    payment = relationship("Payment", back_populates="affiliate_commission")

class Affiliate(Base):
    __tablename__ = 'affiliates'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    affiliate_code = Column(String(50), unique=True, nullable=False)
    commission_rate = Column(Float, default=0.20)
    total_earnings = Column(Float, default=0.0)
    total_referrals = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    commissions = relationship("AffiliateCommission", back_populates="affiliate")
    referrals = relationship("AffiliateReferral", back_populates="affiliate")

class AffiliateReferral(Base):
    __tablename__ = 'affiliate_referrals'
    
    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey('affiliates.id'), nullable=False)
    referred_user_id = Column(Integer, nullable=False)
    referral_code = Column(String(50), nullable=False)
    conversion_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    affiliate = relationship("Affiliate", back_populates="referrals")

class ContentAccess(Base):
    __tablename__ = 'content_access'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    content_id = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)  # course, video, article, etc.
    purchase_price = Column(Float, nullable=False)
    access_granted_at = Column(DateTime, default=datetime.utcnow)
    access_expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    payment_id = Column(Integer, ForeignKey('payments.id'))
    
    def is_expired(self):
        if self.access_expires_at:
            return datetime.utcnow() > self.access_expires_at
        return False

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    stripe_subscription_id = Column(String(255), unique=True)
    plan_name = Column(String(100), nullable=False)
    plan_price = Column(Float, nullable=False)
    billing_period = Column(String(50), default='monthly')  # monthly, annual
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ServiceListing(Base):
    __tablename__ = 'service_listings'
    
    id = Column(Integer, primary_key=True)
    provider_user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("ServiceBooking", back_populates="service")

class ServiceBooking(Base):
    __tablename__ = 'service_bookings'
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service_listings.id'), nullable=False)
    buyer_user_id = Column(Integer, nullable=False)
    payment_id = Column(Integer, ForeignKey('payments.id'))
    booking_status = Column(String(50), default='pending')  # pending, confirmed, completed, cancelled
    scheduled_date = Column(DateTime, nullable=True)
    marketplace_fee = Column(Float)
    provider_payout = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = relationship("ServiceListing", back_populates="bookings")

class RevenueMetric(Base):
    __tablename__ = 'revenue_metrics'
    
    id = Column(Integer, primary_key=True)
    metric_date = Column(DateTime, nullable=False)
    total_revenue = Column(Float, default=0.0)
    payment_revenue = Column(Float, default=0.0)
    subscription_revenue = Column(Float, default=0.0)
    marketplace_revenue = Column(Float, default=0.0)
    content_revenue = Column(Float, default=0.0)
    affiliate_commissions_paid = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    active_subscriptions = Column(Integer, default=0)
    new_customers = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
