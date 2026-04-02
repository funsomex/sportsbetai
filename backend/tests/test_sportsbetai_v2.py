"""
SportsBetAI Backend API Tests - Version 2.0
Tests for refactored modular architecture with new features:
- Bet of the Day widget
- Excel/PDF export
- Health check v2.0.0
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "test_new@test.com"
TEST_PASSWORD = "NuevaPass123"


class TestHealthAndBasics:
    """Health check and basic endpoint tests"""
    
    def test_health_check(self):
        """GET /api/health - should return healthy status and version 2.0.0"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        
        data = response.json()
        assert data["status"] == "healthy", "Status should be healthy"
        assert data["version"] == "2.0.0", f"Version should be 2.0.0, got {data.get('version')}"
        assert "timestamp" in data, "Should include timestamp"
        print(f"✓ Health check passed: version {data['version']}")
    
    def test_root_endpoint(self):
        """GET / - should return API info"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "SportsBetAI API"
        assert data["version"] == "2.0.0"
        print("✓ Root endpoint working")


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """POST /api/auth/login - should authenticate and return token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "token" in data, "Response should include token"
        assert "user" in data, "Response should include user"
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ Login successful for {TEST_EMAIL}")
        return data["token"]
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - should reject invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401, "Should return 401 for invalid credentials"
        print("✓ Invalid credentials rejected correctly")
    
    def test_get_current_user(self):
        """GET /api/auth/me - should return current user with valid token"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json()["token"]
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Get me failed: {response.text}"
        
        data = response.json()
        assert data["email"] == TEST_EMAIL
        print("✓ Get current user working")


class TestMatches:
    """Matches and sports data endpoint tests"""
    
    def test_get_matches(self):
        """GET /api/matches - should return matches with real or demo data"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=10")
        assert response.status_code == 200, f"Get matches failed: {response.text}"
        
        data = response.json()
        assert "matches" in data, "Response should include matches"
        assert "total" in data, "Response should include total"
        assert "source" in data, "Response should include source (real/demo)"
        assert data["source"] in ["real", "demo"], f"Source should be real or demo, got {data['source']}"
        print(f"✓ Matches endpoint working - source: {data['source']}, count: {len(data['matches'])}")
    
    def test_get_value_bets(self):
        """GET /api/value-bets - should return value bets"""
        response = requests.get(f"{BASE_URL}/api/value-bets")
        assert response.status_code == 200, f"Get value bets failed: {response.text}"
        
        data = response.json()
        assert "value_bets" in data, "Response should include value_bets"
        assert "source" in data, "Response should include source"
        print(f"✓ Value bets endpoint working - count: {len(data['value_bets'])}")
    
    def test_get_top_value_bets(self):
        """GET /api/value-bets/top - should return top value bets"""
        response = requests.get(f"{BASE_URL}/api/value-bets/top?limit=5")
        assert response.status_code == 200, f"Get top value bets failed: {response.text}"
        
        data = response.json()
        assert "value_bets" in data
        assert len(data["value_bets"]) <= 5, "Should return at most 5 value bets"
        print(f"✓ Top value bets endpoint working - count: {len(data['value_bets'])}")


class TestBetOfTheDay:
    """Bet of the Day widget endpoint tests - NEW FEATURE"""
    
    def test_get_bet_of_the_day(self):
        """GET /api/bet-of-the-day - should return best value bet with share links"""
        response = requests.get(f"{BASE_URL}/api/bet-of-the-day")
        assert response.status_code == 200, f"Get bet of the day failed: {response.text}"
        
        data = response.json()
        assert "source" in data, "Response should include source"
        assert "generated_at" in data, "Response should include generated_at timestamp"
        
        if data.get("bet"):
            bet = data["bet"]
            # Validate bet structure
            assert "match" in bet, "Bet should include match info"
            assert "selection" in bet, "Bet should include selection"
            assert "odds" in bet, "Bet should include odds"
            assert "value_percentage" in bet, "Bet should include value_percentage"
            assert "confidence" in bet, "Bet should include confidence"
            assert "bookmaker" in bet, "Bet should include bookmaker"
            
            # Validate share links
            assert "share" in data, "Response should include share links"
            share = data["share"]
            assert "text" in share, "Share should include text"
            assert "twitter_url" in share, "Share should include twitter_url"
            assert "whatsapp_url" in share, "Share should include whatsapp_url"
            assert "telegram_url" in share, "Share should include telegram_url"
            
            print(f"✓ Bet of the day: {bet['match']['home_team']} vs {bet['match']['away_team']}")
            print(f"  Selection: {bet['selection']} @ {bet['odds']}")
            print(f"  Value: +{bet['value_percentage']}%, Confidence: {bet['confidence']}%")
        else:
            print("✓ Bet of the day endpoint working (no bets available)")


class TestStats:
    """Statistics endpoint tests"""
    
    def test_get_stats_authenticated(self):
        """GET /api/stats - should return user statistics"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json()["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Get stats failed: {response.text}"
        
        data = response.json()
        # Validate stats structure
        assert "total_predictions" in data, "Should include total_predictions"
        assert "won" in data, "Should include won"
        assert "lost" in data, "Should include lost"
        assert "pending" in data, "Should include pending"
        assert "win_rate" in data, "Should include win_rate"
        assert "roi" in data, "Should include roi"
        assert "total_profit" in data, "Should include total_profit"
        
        print(f"✓ Stats endpoint working - Win rate: {data['win_rate']}%, ROI: {data['roi']}%")
    
    def test_get_stats_unauthenticated(self):
        """GET /api/stats - should reject unauthenticated requests"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code in [401, 403], "Should reject unauthenticated request"
        print("✓ Stats endpoint correctly requires authentication")


class TestExport:
    """Export endpoints tests - NEW FEATURE"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Authentication failed")
    
    def test_export_excel(self, auth_token):
        """GET /api/export/excel - should download Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/export/excel",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Export Excel failed: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheet" in content_type or "excel" in content_type or "octet-stream" in content_type, \
            f"Should return Excel file, got content-type: {content_type}"
        
        # Check content disposition
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "sportsbetai_historial.xlsx" in content_disposition, \
            f"Should have correct filename, got: {content_disposition}"
        
        # Check file size
        assert len(response.content) > 0, "Excel file should not be empty"
        print(f"✓ Excel export working - file size: {len(response.content)} bytes")
    
    def test_export_pdf(self, auth_token):
        """GET /api/export/pdf - should download PDF file"""
        response = requests.get(
            f"{BASE_URL}/api/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Export PDF failed: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "pdf" in content_type or "octet-stream" in content_type, \
            f"Should return PDF file, got content-type: {content_type}"
        
        # Check content disposition
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "sportsbetai_reporte.pdf" in content_disposition, \
            f"Should have correct filename, got: {content_disposition}"
        
        # Check file size
        assert len(response.content) > 0, "PDF file should not be empty"
        print(f"✓ PDF export working - file size: {len(response.content)} bytes")
    
    def test_export_excel_unauthenticated(self):
        """GET /api/export/excel - should reject unauthenticated requests"""
        response = requests.get(f"{BASE_URL}/api/export/excel")
        assert response.status_code in [401, 403], "Should reject unauthenticated request"
        print("✓ Excel export correctly requires authentication")
    
    def test_export_pdf_unauthenticated(self):
        """GET /api/export/pdf - should reject unauthenticated requests"""
        response = requests.get(f"{BASE_URL}/api/export/pdf")
        assert response.status_code in [401, 403], "Should reject unauthenticated request"
        print("✓ PDF export correctly requires authentication")


class TestParlays:
    """Parlays endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Authentication failed")
    
    def test_get_parlays(self, auth_token):
        """GET /api/parlays - should return user parlays"""
        response = requests.get(
            f"{BASE_URL}/api/parlays",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get parlays failed: {response.text}"
        
        data = response.json()
        assert "parlays" in data, "Response should include parlays"
        print(f"✓ Parlays endpoint working - count: {len(data['parlays'])}")
    
    def test_get_parlay_stats(self, auth_token):
        """GET /api/parlays/stats - should return parlay statistics"""
        response = requests.get(
            f"{BASE_URL}/api/parlays/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get parlay stats failed: {response.text}"
        
        data = response.json()
        # Validate stats structure
        assert "total_parlays" in data or "won" in data, "Should include stats"
        print(f"✓ Parlay stats endpoint working")


class TestOddsComparison:
    """Odds comparison endpoint tests"""
    
    def test_compare_odds(self):
        """GET /api/odds/compare/{match_id} - should return odds comparison"""
        # First get a match ID
        matches_response = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if matches_response.status_code == 200 and matches_response.json().get("matches"):
            match_id = matches_response.json()["matches"][0]["id"]
            
            response = requests.get(f"{BASE_URL}/api/odds/compare/{match_id}")
            assert response.status_code == 200, f"Compare odds failed: {response.text}"
            
            data = response.json()
            assert "match" in data, "Response should include match"
            assert "odds_comparison" in data, "Response should include odds_comparison"
            assert "best_odds" in data, "Response should include best_odds"
            print(f"✓ Odds comparison working for match: {data['match']['home_team']} vs {data['match']['away_team']}")
        else:
            print("⚠ Skipping odds comparison test - no matches available")


class TestCacheStats:
    """Cache statistics endpoint tests"""
    
    def test_get_cache_stats(self):
        """GET /api/matches/cache-stats - should return cache statistics"""
        response = requests.get(f"{BASE_URL}/api/matches/cache-stats")
        assert response.status_code == 200, f"Get cache stats failed: {response.text}"
        
        data = response.json()
        print(f"✓ Cache stats endpoint working: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
