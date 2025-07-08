#!/usr/bin/env python3
"""
Browser-based test for Squash Match Tracker
Tests the exact user workflow using Selenium to catch frontend issues
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BrowserWorkflowTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.driver = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome driver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            return False
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} {test_name}: {message}")
    
    def test_page_loading(self) -> bool:
        """Test that the page loads and is not stuck on loading screen"""
        print("\n🔍 Testing Page Loading...")
        
        try:
            self.driver.get(self.base_url)
            
            # Wait for page to load (max 15 seconds)
            WebDriverWait(self.driver, 15).until(
                lambda driver: "Loading your squash data..." not in driver.page_source
            )
            
            # Check if we can find the main elements
            try:
                new_session_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'New Session')]")
                self.log_test("Page Loading", True, "Page loaded successfully with New Session button")
                return True
            except NoSuchElementException:
                self.log_test("Page Loading", False, "Page loaded but New Session button not found")
                return False
                
        except TimeoutException:
            page_source = self.driver.page_source
            if "Loading your squash data..." in page_source:
                self.log_test("Page Loading", False, "Page stuck on loading screen")
            else:
                self.log_test("Page Loading", False, "Page load timeout")
            return False
        except Exception as e:
            self.log_test("Page Loading", False, f"Exception: {str(e)}")
            return False
    
    def test_session_creation_workflow(self) -> bool:
        """Test the complete session creation workflow"""
        print("\n🔍 Testing Session Creation Workflow...")
        
        try:
            # Step 1: Click New Session button
            new_session_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New Session')]"))
            )
            new_session_btn.click()
            self.log_test("Click New Session", True, "Successfully clicked New Session button")
            
            # Step 2: Wait for session creation page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Create New Session')] | //h2[contains(text(), 'Create New Session')]"))
            )
            self.log_test("Session Creation Page", True, "Session creation page loaded")
            
            # Step 3: Find and select players (checkboxes)
            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            if len(checkboxes) < 2:
                self.log_test("Find Player Checkboxes", False, f"Found only {len(checkboxes)} checkboxes, need at least 2")
                return False
            
            self.log_test("Find Player Checkboxes", True, f"Found {len(checkboxes)} player checkboxes")
            
            # Step 4: Select first 3 players (like in the screenshot)
            selected_count = 0
            for i, checkbox in enumerate(checkboxes[:3]):
                try:
                    if not checkbox.is_selected():
                        checkbox.click()
                        selected_count += 1
                        time.sleep(0.5)  # Small delay between clicks
                except Exception as e:
                    print(f"Warning: Could not click checkbox {i}: {e}")
            
            if selected_count < 2:
                self.log_test("Select Players", False, f"Only selected {selected_count} players, need at least 2")
                return False
            
            self.log_test("Select Players", True, f"Selected {selected_count} players")
            
            # Step 5: Find and click the create session button
            try:
                create_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Create Session with {selected_count} Players')]"))
                )
                
                # Get button text to verify it's correct
                button_text = create_btn.text
                self.log_test("Create Button Ready", True, f"Button text: '{button_text}'")
                
                # Click the create session button
                create_btn.click()
                self.log_test("Click Create Session", True, "Clicked create session button")
                
                # Step 6: Wait for navigation to session view or check for errors
                try:
                    # Wait for either session view or error message
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: (
                            "Session View" in driver.page_source or
                            "Match" in driver.page_source or
                            "Error" in driver.page_source or
                            "alert" in driver.page_source.lower()
                        )
                    )
                    
                    # Check what happened
                    page_source = self.driver.page_source
                    if "Session View" in page_source or "Match" in page_source:
                        self.log_test("Session Creation Success", True, "Successfully navigated to session view")
                        return True
                    else:
                        # Check browser console for errors
                        logs = self.driver.get_log('browser')
                        error_logs = [log for log in logs if log['level'] == 'SEVERE']
                        if error_logs:
                            error_msg = error_logs[-1]['message']
                            self.log_test("Session Creation Success", False, f"Browser error: {error_msg}")
                        else:
                            self.log_test("Session Creation Success", False, "Unknown error - session not created")
                        return False
                        
                except TimeoutException:
                    self.log_test("Session Creation Success", False, "Timeout waiting for session creation")
                    return False
                    
            except TimeoutException:
                self.log_test("Create Button Ready", False, "Create session button not found or not clickable")
                return False
                
        except Exception as e:
            self.log_test("Session Creation Workflow", False, f"Exception: {str(e)}")
            return False
    
    def test_console_errors(self) -> bool:
        """Check for JavaScript console errors"""
        print("\n🔍 Testing Console Errors...")
        
        try:
            logs = self.driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if errors:
                error_messages = [log['message'] for log in errors]
                self.log_test("Console Errors", False, f"Found {len(errors)} errors: {error_messages}")
                return False
            else:
                self.log_test("Console Errors", True, "No severe console errors found")
                return True
                
        except Exception as e:
            self.log_test("Console Errors", False, f"Could not check console: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all browser tests"""
        print("🚀 Starting Browser-Based Squash Tracker Tests")
        print(f"🎯 Testing URL: {self.base_url}")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        tests = [
            ("Page Loading", self.test_page_loading),
            ("Session Creation Workflow", self.test_session_creation_workflow),
            ("Console Errors", self.test_console_errors),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(f"{test_name} (Exception)", False, str(e))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 BROWSER TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL BROWSER TESTS PASSED! The frontend is working correctly.")
            return True
        else:
            print("💥 SOME BROWSER TESTS FAILED! Frontend issues detected.")
            return False
    
    def cleanup(self):
        """Clean up browser driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Main test runner"""
    if len(sys.argv) != 2:
        print("Usage: python test_browser_workflow.py <base_url>")
        print("Example: python test_browser_workflow.py https://58hpi8clmdd9.manus.space")
        sys.exit(1)
    
    base_url = sys.argv[1]
    tester = BrowserWorkflowTester(base_url)
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()

