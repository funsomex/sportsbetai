import requests
import sys
import json
from datetime import datetime

class SportsBetAITester:
    def __init__(self, base_url="https://smart-wager-ai-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   Response: {response_data}")
                except:
                    pass
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Raw Response: {response.text[:200]}")
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "error": response.text[:200]
                })

            return success, response.json() if response.content and success else {}

        except Exception as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": f"Network error: {str(e)}"
            })
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "", 200)

    def test_register(self):
        """Test user registration"""
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data = {
            "name": "Test User",
            "email": test_email,
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response.get('user', {})
            print(f"   ✓ Token received and stored")
            return True
        return False

    def test_login(self):
        """Test user login"""
        if not self.user_data:
            return False
            
        login_data = {
            "email": self.user_data['email'],
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        return success and 'access_token' in response

    def test_auth_me(self):
        """Test get current user"""
        return self.run_test("Get Current User", "GET", "auth/me", 200)[0]

    def test_sports(self):
        """Test sports endpoints"""
        return self.run_test("Get Sports", "GET", "sports", 200)[0]

    def test_matches(self):
        """Test matches endpoints"""
        success1 = self.run_test("Get Matches", "GET", "matches", 200)[0]
        success2 = self.run_test("Get Live Matches", "GET", "matches/live", 200)[0]
        success3 = self.run_test("Get Football Matches", "GET", "matches?sport=football", 200)[0]
        return success1 and success2 and success3

    def test_value_bets(self):
        """Test value bets endpoints"""
        success1 = self.run_test("Get Value Bets", "GET", "value-bets", 200)[0]
        success2 = self.run_test("Get Top Value Bets", "GET", "value-bets/top", 200)[0]
        success3 = self.run_test("Get Filtered Value Bets", "GET", "value-bets?min_value=5&sport=football", 200)[0]
        return success1 and success2 and success3

    def test_odds_comparison(self):
        """Test odds comparison"""
        # Generate a test match ID
        test_match_id = "test-match-123"
        return self.run_test("Odds Comparison", "GET", f"odds/compare/{test_match_id}", 200)[0]

    def test_parlays(self):
        """Test parlays endpoints"""
        # Create a parlay - proper format
        parlay_data = {
            "selections": [
                {
                    "match_id": "test1",
                    "selection": "Home",
                    "odds": 2.0
                },
                {
                    "match_id": "test2", 
                    "selection": "Away",
                    "odds": 1.5
                }
            ],
            "name": "Test Parlay",
            "stake": 10.0
        }
        
        success1, create_response = self.run_test("Create Parlay", "POST", "parlays", 200, parlay_data)
        success2 = self.run_test("Get Parlays", "GET", "parlays", 200)[0]
        
        # If parlay was created, test deletion
        if success1 and create_response.get('id'):
            parlay_id = create_response['id']
            success3 = self.run_test("Delete Parlay", "DELETE", f"parlays/{parlay_id}", 200)[0]
            return success1 and success2 and success3
            
        return success1 and success2

    def test_predictions_and_stats(self):
        """Test predictions and stats endpoints"""
        # Create a prediction
        prediction_data = {
            "match_id": "test-match",
            "prediction_type": "1x2",
            "selection": "Home",
            "odds": 2.0,
            "stake": 10.0
        }
        
        success1 = self.run_test("Save Prediction", "POST", "predictions", 200, prediction_data)[0]
        success2 = self.run_test("Get Predictions", "GET", "predictions", 200)[0]
        success3 = self.run_test("Get User Stats", "GET", "stats", 200)[0]
        
        return success1 and success2 and success3

    def test_ai_analysis(self):
        """Test AI analysis endpoint"""
        analysis_data = {
            "match_id": "test-match-ai",
            "analysis_type": "general"
        }
        
        return self.run_test("AI Analysis", "POST", "ai/analyze", 200, analysis_data)[0]

    def test_telegram_endpoints(self):
        """Test Telegram endpoints"""
        # Setup telegram
        setup_data = {"chat_id": "123456789"}
        success1 = self.run_test("Setup Telegram", "POST", "telegram/setup", 200, setup_data)[0]
        
        # Test telegram (this will fail if bot token is invalid, but endpoint should respond)
        success2 = self.run_test("Test Telegram", "POST", "telegram/test", 400)[0]  # Expecting 400 due to invalid chat_id
        
        return success1

    def test_leagues(self):
        """Test leagues endpoint"""
        return self.run_test("Get Football Leagues", "GET", "leagues/football", 200)[0]

def main():
    print("🚀 Starting SportsBetAI Backend API Tests\n")
    print("=" * 60)
    
    tester = SportsBetAITester()
    
    # Test sequence
    test_results = {
        "Health Check": tester.test_health_check(),
        "User Registration": tester.test_register(),
        "User Login": tester.test_login(), 
        "Auth Me": tester.test_auth_me(),
        "Sports": tester.test_sports(),
        "Matches": tester.test_matches(),
        "Value Bets": tester.test_value_bets(),
        "Odds Comparison": tester.test_odds_comparison(),
        "Parlays": tester.test_parlays(),
        "Predictions & Stats": tester.test_predictions_and_stats(),
        "AI Analysis": tester.test_ai_analysis(),
        "Telegram": tester.test_telegram_endpoints(),
        "Leagues": tester.test_leagues()
    }

    print(f"\n{'=' * 60}")
    print(f"📊 TEST RESULTS SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Tests: {tester.tests_run}")
    print(f"Passed: {tester.tests_passed}")
    print(f"Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")

    print(f"\n📋 FEATURE STATUS:")
    for feature, status in test_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {feature}")

    if tester.failed_tests:
        print(f"\n🚨 FAILED TESTS DETAILS:")
        for fail in tester.failed_tests:
            print(f"  ❌ {fail['test']}")
            print(f"     Endpoint: {fail['endpoint']}")
            if 'expected' in fail:
                print(f"     Expected: {fail['expected']}, Got: {fail['actual']}")
            print(f"     Error: {fail['error']}")
            print()

    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())