"""
AgentCore Gateway Deployment Script
Use this to register and deploy services to AgentCore
"""

import requests
import json
from agentcore_services import AGENTCORE_SERVICES, SERVICE_METADATA

class AgentCoreDeployer:
    def __init__(self, agentcore_url: str, api_key: str):
        self.base_url = agentcore_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def register_service(self, service_name: str, service_func, metadata: dict):
        """Register a service with AgentCore Gateway"""
        
        registration_payload = {
            "service_name": service_name,
            "metadata": metadata,
            "endpoint_url": f"{self.base_url}/services/{service_name}",
            "method": "POST",
            "authentication": "bearer_token"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/services/register",
                headers=self.headers,
                json=registration_payload
            )
            
            if response.status_code == 200:
                print(f"✅ Service '{service_name}' registered successfully")
                return True
            else:
                print(f"❌ Failed to register '{service_name}': {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering '{service_name}': {e}")
            return False
    
    def deploy_all_services(self):
        """Deploy all Daily Ritual services to AgentCore"""
        
        print("🚀 Starting AgentCore deployment...")
        
        success_count = 0
        total_services = len(AGENTCORE_SERVICES)
        
        for service_name, service_func in AGENTCORE_SERVICES.items():
            metadata = SERVICE_METADATA.get(service_name, {})
            
            if self.register_service(service_name, service_func, metadata):
                success_count += 1
        
        print(f"\n📊 Deployment Summary:")
        print(f"✅ Successfully deployed: {success_count}/{total_services} services")
        
        if success_count == total_services:
            print("🎉 All services deployed successfully!")
        else:
            print("⚠️ Some services failed to deploy. Check logs above.")
        
        return success_count == total_services
    
    def test_service(self, service_name: str, test_payload: dict):
        """Test a deployed service"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/services/{service_name}/invoke",
                headers=self.headers,
                json=test_payload
            )
            
            if response.status_code == 200:
                print(f"✅ Service '{service_name}' test successful")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Service '{service_name}' test failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing '{service_name}': {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Configure your AgentCore Gateway details
    AGENTCORE_URL = "https://your-agentcore-gateway.com"  # Replace with actual URL
    API_KEY = "your-api-key-here"  # Replace with actual API key
    
    # Initialize deployer
    deployer = AgentCoreDeployer(AGENTCORE_URL, API_KEY)
    
    # Deploy all services
    deployer.deploy_all_services()
    
    # Test services (optional)
    print("\n🧪 Testing deployed services...")
    
    # Test location service
    deployer.test_service("daily_ritual_location", {
        "ip_address": "8.8.8.8"
    })
    
    # Test weather service  
    deployer.test_service("daily_ritual_weather", {
        "city": "New York"
    })
    
    # Test agent service
    deployer.test_service("daily_ritual_agent", {
        "mood": "happy",
        "location": "New York",
        "weather": "sunny, 25°C",
        "activity": "work"
    })