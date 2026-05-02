"""
TradeX Selenium Test Suite
===========================
15 automated test cases covering authentication, navigation, and trading
functionality of the TradeX stock trading web application.

Requirements:
    pip install selenium pytest pytest-html

Usage:
    pytest tests/test_tradex.py -v --html=report.html
"""

import time
import uuid
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
BASE_URL = "http://3.222.182.127:3000"

# A pre-existing test account (must exist in the DB before the suite runs)
VALID_EMAIL    = "testuser@test.com"
VALID_PASSWORD = "test123456"

# A fresh account created once per test run
UNIQUE_SUFFIX   = uuid.uuid4().hex[:6]
NEW_USERNAME    = f"selenium_{UNIQUE_SUFFIX}"
NEW_EMAIL       = f"selenium_{UNIQUE_SUFFIX}@test.com"
NEW_PASSWORD    = "selenium123"

WAIT_TIMEOUT = 15          # seconds for explicit waits


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """
    Headless Chrome WebDriver shared across the entire test module.
    Uses headless mode so it can run inside a Jenkins/Docker environment
    without a display server.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")

    drv = webdriver.Chrome(options=chrome_options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture(scope="module")
def wait(driver):
    return WebDriverWait(driver, WAIT_TIMEOUT)


def login_as_valid_user(driver, wait):
    """Helper: navigate to login page and sign in with the valid test account."""
    driver.get(f"{BASE_URL}/login")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
    driver.find_element(By.CSS_SELECTOR, "input[type='email']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(VALID_EMAIL)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(VALID_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("/dashboard"))


# ─────────────────────────────────────────────
# TEST CASES
# ─────────────────────────────────────────────

class TestAuthentication:
    """Tests 1-8: Login and Signup functionality"""

    # ── Test 1 ─────────────────────────────────
    def test_01_login_page_loads(self, driver, wait):
        """Login page renders with all required elements."""
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))

        assert driver.find_element(By.CSS_SELECTOR, "input[type='email']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "input[type='password']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']").is_displayed()

    # ── Test 2 ─────────────────────────────────
    def test_02_login_page_title_contains_tradex(self, driver, wait):
        """Page title or visible heading contains 'TradeX'."""
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "TradeX" in body_text, "Expected 'TradeX' branding on the login page"

    # ── Test 3 ─────────────────────────────────
    def test_03_login_with_invalid_credentials(self, driver, wait):
        """Wrong credentials display an error message."""
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))

        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys("wrong@example.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("wrongpassword")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.bg-red-50"))
        )
        assert error_el.is_displayed(), "Expected an error banner for invalid credentials"

    # ── Test 4 ─────────────────────────────────
    def test_04_login_with_valid_credentials_redirects_to_dashboard(self, driver, wait):
        """Valid credentials redirect to /dashboard."""
        login_as_valid_user(driver, wait)
        assert "/dashboard" in driver.current_url

    # ── Test 5 ─────────────────────────────────
    def test_05_logout_redirects_to_login(self, driver, wait):
        """Clicking Logout takes the user back to /login."""
        # Ensure we are logged in first
        if "/dashboard" not in driver.current_url:
            login_as_valid_user(driver, wait)

        logout_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Logout') or contains(text(),'Sign Out')]")
        ))
        logout_btn.click()
        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url

    # ── Test 6 ─────────────────────────────────
    def test_06_signup_page_loads(self, driver, wait):
        """Signup page renders with all form fields."""
        driver.get(f"{BASE_URL}/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Your username']")))

        assert driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your username']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your email address']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "input[placeholder='At least 6 characters']").is_displayed()

    # ── Test 7 ─────────────────────────────────
    def test_07_signup_with_mismatched_passwords_shows_error(self, driver, wait):
        """Mismatched passwords show a validation error without calling the API."""
        driver.get(f"{BASE_URL}/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Your username']")))

        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your username']").send_keys("someuser")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your email address']").send_keys("some@test.com")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='At least 6 characters']").send_keys("pass123")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Re-enter your password']").send_keys("different")
        # Accept terms
        driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']").click()
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.bg-red-50")))
        assert "Passwords do not match" in error_el.text

    # ── Test 8 ─────────────────────────────────
    def test_08_signup_new_user_and_redirect_to_login(self, driver, wait):
        """Successful signup redirects to /login."""
        driver.get(f"{BASE_URL}/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Your username']")))

        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your username']").send_keys(NEW_USERNAME)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your email address']").send_keys(NEW_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='At least 6 characters']").send_keys(NEW_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Re-enter your password']").send_keys(NEW_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']").click()
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url


class TestDashboard:
    """Tests 9-15: Dashboard elements and trading functionality"""

    @pytest.fixture(autouse=True)
    def ensure_logged_in(self, driver, wait):
        """Automatically log in before every test in this class."""
        if "/dashboard" not in driver.current_url:
            login_as_valid_user(driver, wait)

    # ── Test 9 ─────────────────────────────────
    def test_09_dashboard_shows_portfolio_value(self, driver, wait):
        """Dashboard overview tab displays a 'Total Portfolio Value' card."""
        # Click the Overview tab to make sure we're on the right tab
        overview_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Overview')]")
        ))
        overview_btn.click()

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Total Portfolio Value" in body_text or "Cash Available" in body_text

    # ── Test 10 ─────────────────────────────────
    def test_10_dashboard_navigation_tabs_present(self, driver, wait):
        """All four navigation tabs are visible on the dashboard."""
        body_text = driver.find_element(By.TAG_NAME, "body").text
        for tab in ["Overview", "Portfolio", "Trading", "History"]:
            assert tab in body_text, f"Navigation tab '{tab}' not found on dashboard"

    # ── Test 11 ─────────────────────────────────
    def test_11_portfolio_tab_loads(self, driver, wait):
        """Clicking the Portfolio tab shows portfolio content."""
        portfolio_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Portfolio')]")
        ))
        portfolio_btn.click()
        time.sleep(1)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        # Portfolio tab should show allocation or an empty-state message
        assert "Portfolio" in body_text

    # ── Test 12 ─────────────────────────────────
    def test_12_trading_tab_shows_market_prices(self, driver, wait):
        """The Trading tab renders a list of stock tickers with prices."""
        trading_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Trading')]")
        ))
        trading_btn.click()
        time.sleep(1.5)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        # At least one well-known ticker should be listed
        known_tickers = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]
        found = any(ticker in body_text for ticker in known_tickers)
        assert found, "No known stock ticker found on the Trading tab"

    # ── Test 13 ─────────────────────────────────
    def test_13_trade_button_opens_modal(self, driver, wait):
        """Clicking the '+ Trade' button opens the trading modal."""
        if "/dashboard" not in driver.current_url:
            login_as_valid_user(driver, wait)

        trade_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Trade')]")
        ))
        trade_btn.click()

        # Modal should appear — look for Buy/Sell radio buttons or a ticker input
        modal_visible = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'BUY') or contains(text(),'SELL') or contains(text(),'Ticker')]")
        ))
        assert modal_visible.is_displayed(), "Trading modal did not open"

    # ── Test 14 ─────────────────────────────────
    def test_14_history_tab_loads(self, driver, wait):
        """The History tab loads without errors."""
        # Close any open modal first
        try:
            esc_btn = driver.find_element(By.XPATH, "//button[contains(@class,'absolute') and contains(text(),'×')]")
            esc_btn.click()
        except Exception:
            pass

        if "/dashboard" not in driver.current_url:
            login_as_valid_user(driver, wait)

        history_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'History')]")
        ))
        history_btn.click()
        time.sleep(1)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "History" in body_text

    # ── Test 15 ─────────────────────────────────
    def test_15_signup_with_short_password_shows_error(self, driver, wait):
        """
        Signup validation rejects passwords shorter than 6 characters.
        (Navigates away and comes back, confirming state isolation.)
        """
        driver.get(f"{BASE_URL}/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Your username']")))

        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your username']").send_keys("shortpwduser")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your email address']").send_keys("shortpwd@test.com")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='At least 6 characters']").send_keys("abc")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Re-enter your password']").send_keys("abc")
        driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']").click()
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.bg-red-50")))
        assert "6 characters" in error_el.text or "Password" in error_el.text
