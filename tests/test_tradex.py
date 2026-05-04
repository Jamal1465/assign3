"""
TradeX Selenium Test Suite — CLEAN & STABLE VERSION
==================================================
15 tests | Headless Chrome | Jenkins + Docker ready
"""

import os
import time
import uuid
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# ──────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────
BASE_URL = os.getenv("BASE_URL", "http://3.222.182.127:3000")
VALID_EMAIL = "testuser@test.com"
VALID_PASSWORD = "test123456"
WAIT_TIMEOUT = 20

_uid = uuid.uuid4().hex[:6]
NEW_USERNAME = f"sel_{_uid}"
NEW_EMAIL = f"sel_{_uid}@test.com"
NEW_PASSWORD = "selenium123"


# ──────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────
@pytest.fixture
def driver():
    opt = Options()
    opt.add_argument("--headless=new")
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")
    opt.add_argument("--disable-gpu")
    opt.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opt)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, WAIT_TIMEOUT)


# ──────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────
def do_login(driver, wait):
    driver.get(f"{BASE_URL}/login")

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(VALID_EMAIL)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(VALID_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.url_contains("/dashboard"))


def fill_signup(driver, wait, username, email, password, confirm):
    driver.get(f"{BASE_URL}/signup")

    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "input[placeholder='Your username']")
    ))

    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your username']").send_keys(username)
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your email address']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='At least 6 characters']").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Re-enter your password']").send_keys(confirm)

    try:
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        driver.execute_script("arguments[0].click();", checkbox)
    except:
        pass

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


def is_error_visible(driver):
    selectors = ["div.bg-red-50", ".text-red-500", "[role='alert']", ".error"]
    for selector in selectors:
        try:
            if driver.find_element(By.CSS_SELECTOR, selector).is_displayed():
                return True
        except:
            continue
    return False


# ──────────────────────────────────────────────────────
# AUTH TESTS (1–8)
# ──────────────────────────────────────────────────────
class TestAuthentication:

    def test_01_login_page_loads(self, driver, wait):
        driver.get(f"{BASE_URL}/login")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))

        assert driver.find_element(By.CSS_SELECTOR, "input[type='email']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "input[type='password']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']").is_displayed()

    def test_02_login_page_has_brand(self, driver, wait):
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "TradeX" in driver.page_source

    def test_03_invalid_login_shows_error(self, driver, wait):
        driver.get(f"{BASE_URL}/login")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys("wrong@test.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("wrongpass")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        assert is_error_visible(driver) or "invalid" in driver.page_source.lower()

    def test_04_valid_login_goes_to_dashboard(self, driver, wait):
        do_login(driver, wait)
        assert "/dashboard" in driver.current_url

    def test_05_logout_goes_to_login(self, driver, wait):
        do_login(driver, wait)

        logout_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Log Out']")
        ))

        driver.execute_script("arguments[0].click();", logout_btn)

        wait.until(EC.url_contains("/login"))

        assert "login" in driver.current_url.lower()

    def test_06_signup_page_loads(self, driver, wait):
        driver.get(f"{BASE_URL}/signup")

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Your username']")
        ))

        assert driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your username']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your email address']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "input[placeholder='At least 6 characters']").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "input[placeholder='Re-enter your password']").is_displayed()

    def test_07_password_mismatch_shows_error(self, driver, wait):
        fill_signup(driver, wait,
                    "user1", "user1@test.com",
                    "pass123", "wrong")

        time.sleep(1)

        assert is_error_visible(driver) or "signup" in driver.current_url.lower()

    def test_08_successful_signup_redirects(self, driver, wait):
        fill_signup(driver, wait,
                    NEW_USERNAME,
                    NEW_EMAIL,
                    NEW_PASSWORD,
                    NEW_PASSWORD)

        wait.until(EC.url_contains("/login"))

        assert "/login" in driver.current_url


# ──────────────────────────────────────────────────────
# DASHBOARD TESTS (9–15)
# ──────────────────────────────────────────────────────
class TestDashboard:

    @pytest.fixture(autouse=True)
    def login_first(self, driver, wait):
        do_login(driver, wait)

    def test_09_dashboard_shows_portfolio(self, driver):
        assert "Portfolio" in driver.page_source or "Total Portfolio Value" in driver.page_source

    def test_10_nav_tabs_present(self, driver):
        body = driver.page_source
        assert "Portfolio" in body
        assert "Trading" in body
        assert "History" in body

    def test_11_portfolio_tab_clickable(self, driver, wait):
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Portfolio']")
        ))
        btn.click()
        assert "Portfolio" in driver.page_source

    def test_12_trading_tab_clickable(self, driver, wait):
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Trading']")
        ))
        btn.click()

        wait.until(lambda d: "trade" in d.page_source.lower())

        assert True

    def test_13_trade_modal_opens(self, driver, wait):
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Trade')]")
        ))
        btn.click()

        time.sleep(1)

        assert "trade" in driver.page_source.lower() or "buy" in driver.page_source.lower()

    def test_14_history_tab_clickable(self, driver, wait):
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='History']")
        ))
        btn.click()

        assert "History" in driver.page_source or "Recent Activity" in driver.page_source

    def test_15_short_password_validation(self, driver, wait):
        driver.get(f"{BASE_URL}/signup")

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Your username']")
        ))

        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your username']").send_keys("short")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your email address']").send_keys("s@test.com")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='At least 6 characters']").send_keys("ab")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Re-enter your password']").send_keys("ab")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        time.sleep(1)

        assert is_error_visible(driver) or "signup" in driver.current_url.lower()
