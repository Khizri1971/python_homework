from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.checkout_page import CheckoutPage


class CartPage:
    """Корзина: переход к оформлению заказа."""

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.checkout_button = (By.ID, "checkout")

    def open_checkout(self) -> CheckoutPage:
        self.wait.until(
            EC.element_to_be_clickable(self.checkout_button)
        ).click()
        return CheckoutPage(self.driver)
