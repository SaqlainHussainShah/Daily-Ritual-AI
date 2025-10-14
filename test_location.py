import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.location_service import get_location_from_ip

# Test with different IPs
test_ips = [
    "127.0.0.1",  # localhost
    "8.8.8.8",    # Google DNS (will show US location)
    "1.1.1.1",    # Cloudflare DNS
    None          # None case
]

for ip in test_ips:
    print(f"Testing IP: {ip}")
    result = get_location_from_ip(ip)
    print(f"Result: {result}")
    print("-" * 40)