from datetime import datetime, timedelta
from collections import defaultdict

# Simple in-memory rate limiter for guests
guest_usage = defaultdict(lambda: {'count': 0, 'reset_time': datetime.utcnow() + timedelta(days=1)})

def check_guest_limit(ip_address):
    """Check if guest IP has reached daily limit (3 analyses)"""
    now = datetime.utcnow()
    user_data = guest_usage[ip_address]
    
    # Reset if past reset time
    if now > user_data['reset_time']:
        user_data['count'] = 0
        user_data['reset_time'] = now + timedelta(days=1)
    
    # Check limit
    if user_data['count'] >= 3:
        return False, 0
    
    return True, 3 - user_data['count']

def increment_guest_usage(ip_address):
    """Increment guest usage count"""
    guest_usage[ip_address]['count'] += 1
