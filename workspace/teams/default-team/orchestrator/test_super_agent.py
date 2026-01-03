#!/usr/bin/env python3
"""
SuperAgent Integration Test

This script tests the SuperAgent functionality including:
- Message envelope validation
- Incident lifecycle management
- Agent communication
- State machine transitions
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import urllib.request
import urllib.error

# Configuration
SUPER_AGENT_URL = "http://localhost:8080"


class SimpleResponse:
    """Lightweight response object providing the subset of the requests.Response API used in tests."""

    def __init__(self, status_code: int, text: str, content: bytes):
        self.status_code = status_code
        self.text = text
        self._content = content

    def json(self) -> Any:
        """Parse the response body as JSON, returning None if the body is empty."""
        if not self._content:
            return None
        return json.loads(self._content.decode("utf-8"))


class HttpSession:
    """Minimal HTTP session wrapper using urllib to emulate requests.Session for GET/POST."""

    def get(self, url: str, timeout: float = 10) -> SimpleResponse:
        return self._request("GET", url, data=None, headers=None, timeout=timeout)

    def post(self, url: str, json_data: Dict[str, Any] | None = None, timeout: float = 10) -> "SimpleResponse":
        data = None
        headers: Dict[str, str] | None = None
        if json_data is not None:
            data = json.dumps(json_data).encode("utf-8")
            headers = {"Content-Type": "application/json"}
        return self._request("POST", url, data=data, headers=headers, timeout=timeout)

    def _request(
        self,
        method: str,
        url: str,
        data: bytes | None,
        headers: Dict[str, str] | None,
        timeout: float = 10,
    ) -> SimpleResponse:
        request = urllib.request.Request(url, data=data, method=method)
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content = response.read()
                status_code = response.getcode()
        except urllib.error.HTTPError as e:
            content = e.read()
            status_code = e.code
        text = content.decode("utf-8") if content else ""
        return SimpleResponse(status_code=status_code, text=text, content=content)


class SuperAgentTester:
    def __init__(self, base_url: str = SUPER_AGENT_URL):
        self.base_url = base_url
        self.session = HttpSession()
    
    def generate_test_message(self, message_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a test message with proper envelope"""
        import uuid
        trace_id = f"mno-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4()}"
        
        return {
            "meta": {
                "trace_id": trace_id,
                "span_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source_agent": "test-client",
                "target_agent": "super-agent",
                "message_type": message_type,
                "schema_version": "v1.0.0"
            },
            "context": {
                "namespace": "machinenativeops",
                "namespace": "machinenativenops-system",
                "cluster": "test-cluster",
                "urgency": "P1"
            },
            "payload": payload
        }
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_readiness_check(self) -> bool:
        """Test readiness check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/ready")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Readiness check passed: {data}")
                return True
            else:
                print(f"❌ Readiness check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Readiness check error: {e}")
            return False
    
    def test_incident_signal(self) -> bool:
        """Test incident signal handling"""
        try:
            payload = {
                "incident_type": "config_validation_failed",
                "severity": "high",
                "affected_resources": ["configmap://test-config"],
                "metadata": {
                    "description": "Test configuration validation failure",
                    "source": "unit-test"
                }
            }
            
            message = self.generate_test_message("IncidentSignal", payload)
            response = self.session.post(f"{self.base_url}/message", json=message)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Incident signal processed: {data}")
                return data["processing_result"]["status"] == "created"
            else:
                print(f"❌ Incident signal failed: {response.status_code}, {response.text}")
                return False
        except Exception as e:
            print(f"❌ Incident signal error: {e}")
            return False
    
    def test_invalid_message(self) -> bool:
        """Test invalid message rejection"""
        try:
            invalid_message = {
                "meta": {
                    "source_agent": "test-client",
                    # Missing required fields
                },
                "context": {
                    "namespace": "machinenativenops-system"
                },
                "payload": {}
            }
            
            response = self.session.post(f"{self.base_url}/message", json=invalid_message)
            
            if response.status_code == 400:
                print("✅ Invalid message properly rejected")
                return True
            else:
                print(f"❌ Invalid message should be rejected: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Invalid message test error: {e}")
            return False
    
    def test_list_incidents(self) -> bool:
        """Test incident listing"""
        try:
            response = self.session.get(f"{self.base_url}/incidents")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Incidents listed: {data['count']} incidents")
                return True
            else:
                print(f"❌ List incidents failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ List incidents error: {e}")
            return False
    
    def test_metrics(self) -> bool:
        """Test metrics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/metrics")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Metrics retrieved: {data}")
                return True
            else:
                print(f"❌ Metrics failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Metrics error: {e}")
            return False
    
    def test_message_validation(self) -> bool:
        """Test message envelope validation"""
        try:
            # Test valid message
            valid_message = self.generate_test_message("IncidentSignal", {
                "incident_type": "test",
                "severity": "low"
            })
            
            response = self.session.post(f"{self.base_url}/message", json=valid_message)
            
            if response.status_code == 200:
                print("✅ Valid message accepted")
                return True
            else:
                print(f"❌ Valid message rejected: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Message validation error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🧪 Starting SuperAgent Integration Tests...")
        print("=" * 50)
        
        tests = {
            "Health Check": self.test_health_check,
            "Readiness Check": self.test_readiness_check,
            "Message Validation": self.test_message_validation,
            "Incident Signal": self.test_incident_signal,
            "Invalid Message": self.test_invalid_message,
            "List Incidents": self.test_list_incidents,
            "Metrics": self.test_metrics,
        }
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests.items():
            print(f"\n🔍 Running {test_name}...")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"Passed: {passed}/{total}")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        success_rate = (passed / total) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 SuperAgent tests PASSED!")
        else:
            print("⚠️  SuperAgent tests need attention")
        
        return results

def main():
    """Main test runner"""
    import sys
    
    # Allow custom URL from command line
    base_url = sys.argv[1] if len(sys.argv) > 1 else SUPER_AGENT_URL
    tester = SuperAgentTester(base_url)
    
    print(f"Testing SuperAgent at: {base_url}")
    print("Waiting for service to be ready...")
    
    # Wait a moment for service startup
    time.sleep(2)
    
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    success_rate = sum(1 for r in results.values() if r) / len(results)
    sys.exit(0 if success_rate >= 0.8 else 1)

if __name__ == "__main__":
    main()