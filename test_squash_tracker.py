#!/usr/bin/env python3
"""
Comprehensive automated tests for Squash Match Tracker
Tests all core functionality to ensure everything works correctly
"""

import requests
import json
import time
import sys
from typing import Dict, List, Optional

class SquashTrackerTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.test_results = []
        self.created_players = []
        self.created_sessions = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} {test_name}: {message}")
        
    def test_app_loading(self) -> bool:
        """Test A: Application Loading & Basic Functionality"""
        print("\n🔍 Testing Application Loading...")
        
        try:
            # Test main page loads
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code != 200:
                self.log_test("App Loading", False, f"Main page returned {response.status_code}")
                return False
                
            # Check if it's not stuck on loading screen
            if "Loading your squash data..." in response.text and len(response.text) < 1000:
                self.log_test("App Loading", False, "App stuck on loading screen")
                return False
                
            self.log_test("App Loading", True, "Main page loads correctly")
            return True
            
        except Exception as e:
            self.log_test("App Loading", False, f"Exception: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test H: Data Persistence & API"""
        print("\n🔍 Testing API Endpoints...")
        
        endpoints = [
            ("GET /api/players", "players"),
            ("GET /api/sessions", "sessions"), 
            ("GET /api/leaderboard", "leaderboard"),
            ("GET /api/highlights", "highlights")
        ]
        
        all_passed = True
        
        for endpoint_name, endpoint in endpoints:
            try:
                response = self.session.get(f"{self.api_base}/{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(endpoint_name, True, f"Returns {len(data) if isinstance(data, list) else 'valid'} items")
                else:
                    self.log_test(endpoint_name, False, f"Status {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}")
                all_passed = False
                
        return all_passed
    
    def test_player_management(self) -> bool:
        """Test B: Player Management"""
        print("\n🔍 Testing Player Management...")
        
        # Test adding a new player
        test_player_name = f"TestPlayer_{int(time.time())}"
        
        try:
            response = self.session.post(
                f"{self.api_base}/players",
                json={"name": test_player_name},
                timeout=5
            )
            
            if response.status_code == 200 or response.status_code == 201:
                player_data = response.json()
                self.created_players.append(player_data['id'])
                self.log_test("Add Player", True, f"Created player {test_player_name}")
                
                # Verify player appears in list
                players_response = self.session.get(f"{self.api_base}/players")
                if players_response.status_code == 200:
                    players = players_response.json()
                    if any(p['name'] == test_player_name for p in players):
                        self.log_test("Player in List", True, "New player appears in list")
                        return True
                    else:
                        self.log_test("Player in List", False, "New player not found in list")
                        return False
                else:
                    self.log_test("Player in List", False, f"Failed to fetch players: {players_response.status_code}")
                    return False
            else:
                self.log_test("Add Player", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add Player", False, f"Exception: {str(e)}")
            return False
    
    def test_frontend_simulation(self) -> bool:
        """Test K: Frontend Simulation - Test the exact workflow a user would follow"""
        print("\n🔍 Testing Frontend Simulation...")
        
        try:
            # Step 1: Load main page (simulating user opening the app)
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                self.log_test("Frontend - Load Main Page", False, f"Status {response.status_code}")
                return False
            
            # Step 2: Get players (simulating the app loading players)
            response = self.session.get(f"{self.api_base}/players")
            if response.status_code != 200:
                self.log_test("Frontend - Load Players", False, f"Status {response.status_code}")
                return False
            
            players = response.json()
            if len(players) < 2:
                self.log_test("Frontend - Sufficient Players", False, f"Need 2+ players, found {len(players)}")
                return False
            
            # Step 3: Simulate user selecting players and creating session
            selected_players = [players[0]['id'], players[1]['id']]
            
            # This is the exact request the frontend makes
            session_request = {
                "player_ids": selected_players
            }
            
            response = self.session.post(
                f"{self.api_base}/sessions",
                json=session_request,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                session = response.json()
                self.created_sessions.append(session['id'])
                self.log_test("Frontend - Session Creation", True, f"Frontend workflow successful: session {session['id']}")
                return True
            else:
                self.log_test("Frontend - Session Creation", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Frontend - Session Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_session_creation(self) -> bool:
        """Test C: Session Creation (CRITICAL)"""
        print("\n🔍 Testing Session Creation (CRITICAL TEST)...")
        
        # First get available players
        try:
            players_response = self.session.get(f"{self.api_base}/players")
            if players_response.status_code != 200:
                self.log_test("Session Creation - Get Players", False, f"Failed to get players: {players_response.status_code}")
                return False
                
            players = players_response.json()
            if len(players) < 2:
                self.log_test("Session Creation - Player Count", False, f"Need at least 2 players, found {len(players)}")
                return False
                
            # Select first 2 players
            selected_players = [players[0]['id'], players[1]['id']]
            self.log_test("Session Creation - Player Selection", True, f"Selected players {selected_players}")
            
            # Test session creation
            session_data = {"player_ids": selected_players}
            response = self.session.post(
                f"{self.api_base}/sessions",
                json=session_data,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                session = response.json()
                self.created_sessions.append(session['id'])
                
                # Verify session has matches
                if 'matches' in session and len(session['matches']) > 0:
                    self.log_test("Session Creation", True, f"Created session {session['id']} with {len(session['matches'])} matches")
                    
                    # Verify session appears in sessions list
                    sessions_response = self.session.get(f"{self.api_base}/sessions")
                    if sessions_response.status_code == 200:
                        sessions = sessions_response.json()
                        if any(s['id'] == session['id'] for s in sessions):
                            self.log_test("Session in List", True, "New session appears in sessions list")
                            return True
                        else:
                            self.log_test("Session in List", False, "New session not found in sessions list")
                            return False
                    else:
                        self.log_test("Session in List", False, f"Failed to fetch sessions: {sessions_response.status_code}")
                        return False
                else:
                    self.log_test("Session Creation", False, "Session created but has no matches")
                    return False
            else:
                error_text = response.text
                self.log_test("Session Creation", False, f"Status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Session Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_match_management(self) -> bool:
        """Test D: Session View & Match Management"""
        print("\n🔍 Testing Match Management...")
        
        if not self.created_sessions:
            self.log_test("Match Management", False, "No sessions available for testing")
            return False
            
        session_id = self.created_sessions[0]
        
        try:
            # Get session details
            response = self.session.get(f"{self.api_base}/sessions/{session_id}")
            if response.status_code != 200:
                self.log_test("Get Session Details", False, f"Status {response.status_code}")
                return False
                
            session = response.json()
            if not session.get('matches'):
                self.log_test("Session Has Matches", False, "Session has no matches")
                return False
                
            match = session['matches'][0]
            match_id = match['id']
            
            # Test match score update
            score_data = {
                "player1_score": 11,
                "player2_score": 9
            }
            
            response = self.session.put(
                f"{self.api_base}/matches/{match_id}",
                json=score_data,
                timeout=5
            )
            
            if response.status_code == 200:
                try:
                    updated_match = response.json()
                    if updated_match.get('player1_score') == 11 and updated_match.get('player2_score') == 9:
                        self.log_test("Match Score Update", True, f"Updated match {match_id} scores")
                        
                        # Check if ELO changes are present
                        if 'elo_changes' in updated_match:
                            self.log_test("ELO Calculation", True, "ELO changes calculated")
                            return True
                        else:
                            self.log_test("ELO Calculation", False, "No ELO changes in response")
                            return False
                    else:
                        self.log_test("Match Score Update", False, "Scores not updated correctly")
                        return False
                except ValueError as json_error:
                    self.log_test("Match Score Update", False, f"Invalid JSON response: {response.text[:100]}")
                    return False
            else:
                self.log_test("Match Score Update", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Match Management", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_functionality(self) -> bool:
        """Test F: Delete Functionality"""
        print("\n🔍 Testing Delete Functionality...")
        
        if not self.created_sessions:
            self.log_test("Delete Functionality", False, "No sessions available for testing")
            return False
            
        session_id = self.created_sessions[0]
        
        try:
            # Test session deletion
            response = self.session.delete(f"{self.api_base}/sessions/{session_id}")
            
            if response.status_code == 200:
                self.log_test("Delete Session", True, f"Deleted session {session_id}")
                
                # Verify session is removed from list
                sessions_response = self.session.get(f"{self.api_base}/sessions")
                if sessions_response.status_code == 200:
                    sessions = sessions_response.json()
                    if not any(s['id'] == session_id for s in sessions):
                        self.log_test("Session Removed from List", True, "Deleted session no longer in list")
                        self.created_sessions.remove(session_id)
                        return True
                    else:
                        self.log_test("Session Removed from List", False, "Deleted session still in list")
                        return False
                else:
                    self.log_test("Session Removed from List", False, f"Failed to fetch sessions: {sessions_response.status_code}")
                    return False
            else:
                self.log_test("Delete Session", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Functionality", False, f"Exception: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test sessions
        for session_id in self.created_sessions[:]:
            try:
                response = self.session.delete(f"{self.api_base}/sessions/{session_id}")
                if response.status_code == 200:
                    print(f"✅ Deleted test session {session_id}")
                    self.created_sessions.remove(session_id)
                else:
                    print(f"⚠️ Failed to delete test session {session_id}")
            except Exception as e:
                print(f"⚠️ Error deleting session {session_id}: {e}")
        
        # Note: We don't delete test players as they might be useful to keep
        if self.created_players:
            print(f"ℹ️ Keeping {len(self.created_players)} test players for future use")
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        print("🚀 Starting Comprehensive Squash Tracker Tests")
        print(f"🎯 Testing URL: {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("Application Loading", self.test_app_loading),
            ("API Endpoints", self.test_api_endpoints),
            ("Player Management", self.test_player_management),
            ("Frontend Simulation", self.test_frontend_simulation),
            ("Session Creation (CRITICAL)", self.test_session_creation),
            ("Match Management", self.test_match_management),
            ("Delete Functionality", self.test_delete_functionality),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(f"{test_name} (Exception)", False, str(e))
        
        # Cleanup
        self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! The squash tracker is working correctly.")
            return True
        else:
            print("💥 SOME TESTS FAILED! Issues need to be fixed.")
            return False

def main():
    """Main test runner"""
    if len(sys.argv) != 2:
        print("Usage: python test_squash_tracker.py <base_url>")
        print("Example: python test_squash_tracker.py https://kkh7ikcgm1l0.manus.space")
        sys.exit(1)
    
    base_url = sys.argv[1]
    tester = SquashTrackerTester(base_url)
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

