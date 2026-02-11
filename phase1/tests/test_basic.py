"""
Basic tests for the revenue API
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_import_models():
    """Test that models can be imported"""
    from phase1.src.models.revenue_models import (
        Payment, Affiliate, AffiliateCommission, AffiliateReferral,
        ContentAccess, Subscription, ServiceListing, ServiceBooking, RevenueMetric
    )
    assert Payment is not None
    assert Affiliate is not None

def test_payment_status_enum():
    """Test PaymentStatus enum"""
    from phase1.src.models.revenue_models import PaymentStatus
    assert PaymentStatus.PENDING.value == "pending"
    assert PaymentStatus.COMPLETED.value == "completed"
    assert PaymentStatus.FAILED.value == "failed"

def test_subscription_status_enum():
    """Test SubscriptionStatus enum"""
    from phase1.src.models.revenue_models import SubscriptionStatus
    assert SubscriptionStatus.ACTIVE.value == "active"
    assert SubscriptionStatus.CANCELLED.value == "cancelled"

def test_affiliate_code_generation():
    """Test affiliate code generation"""
    from phase1.src.api.affiliates import generate_affiliate_code
    code1 = generate_affiliate_code()
    code2 = generate_affiliate_code()
    
    assert len(code1) == 8
    assert len(code2) == 8
    assert code1 != code2  # Should be unique

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
