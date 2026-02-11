"""
Integration example: Phase 1 (Revenue) with Phase 4 (Event Bus)

This demonstrates how payment events can trigger workflow automation
through the event bus system.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from phase4.src.event_bus.bus import EventBus

class RevenueEventHandler:
    """Handles revenue-related events from Phase 1"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up event handlers for revenue events"""
        self.event_bus.subscribe('payment.completed', self.on_payment_completed)
        self.event_bus.subscribe('payment.failed', self.on_payment_failed)
        self.event_bus.subscribe('subscription.created', self.on_subscription_created)
        self.event_bus.subscribe('subscription.cancelled', self.on_subscription_cancelled)
        self.event_bus.subscribe('affiliate.commission_earned', self.on_commission_earned)
    
    async def on_payment_completed(self, payload: dict):
        """Handle successful payment"""
        print(f"✅ Payment completed: ${payload.get('amount')} from user {payload.get('user_id')}")
        
        # Check if there's an affiliate code
        if payload.get('affiliate_code'):
            await self.event_bus.publish('affiliate.commission_earned', {
                'payment_id': payload.get('payment_id'),
                'affiliate_code': payload.get('affiliate_code'),
                'amount': payload.get('amount')
            })
    
    async def on_payment_failed(self, payload: dict):
        """Handle failed payment"""
        print(f"❌ Payment failed for user {payload.get('user_id')}")
    
    async def on_subscription_created(self, payload: dict):
        """Handle new subscription"""
        print(f"🎉 New subscription: {payload.get('plan_name')} for user {payload.get('user_id')}")
    
    async def on_subscription_cancelled(self, payload: dict):
        """Handle subscription cancellation"""
        print(f"⚠️  Subscription cancelled for user {payload.get('user_id')}")
    
    async def on_commission_earned(self, payload: dict):
        """Handle affiliate commission earned"""
        print(f"💰 Commission earned: Affiliate {payload.get('affiliate_code')}")

async def simulate_payment_flow():
    """Simulate a payment flow with events"""
    event_bus = EventBus()
    await event_bus.start()
    revenue_handler = RevenueEventHandler(event_bus)
    
    print("\n" + "="*60)
    print("   REVENUE EVENT FLOW SIMULATION")
    print("="*60 + "\n")
    
    print("1. Simulating payment with affiliate referral...")
    await event_bus.publish('payment.completed', {
        'payment_id': 'pay_123',
        'user_id': 1001,
        'amount': 99.99,
        'affiliate_code': 'ABC123XY'
    })
    await asyncio.sleep(0.5)
    
    print("\n" + "="*60)
    print("   Event flow simulation complete!")
    print("="*60 + "\n")

if __name__ == '__main__':
    asyncio.run(simulate_payment_flow())
