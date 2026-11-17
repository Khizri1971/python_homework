from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.inventory_page import MainShopPage

URL = "https://www.saucedemo.com/"


class LoginPage:
    """Страница авторизации."""

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.input_login = (By.ID, "user-name")
        self.input_password = (By.ID, "password")
        self.button_login = (By.ID, "login-button")

    def open(self) -> "LoginPage":
        self.driver.get(URL)
        return self

    def login(self, username: str, password: str) -> MainShopPage:
        self.wait.until(
            EC.visibility_of_element_located(self.input_login)
        ).send_keys(username)
        self.wait.until(
            EC.visibility_of_element_located(self.input_password)
        ).send_keys(password)
        self.wait.until(
            EC.element_to_be_clickable(self.button_login)
        ).click()
        return MainShopPage(self.driver)
