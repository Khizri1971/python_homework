from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CheckoutPage:
    """Оформление заказа: данные покупателя и итоговая сумма."""

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.first_name = (By.ID, "first-name")
        self.last_name = (By.ID, "last-name")
        self.postal_code = (By.ID, "postal-code")
        self.continue_button = (By.ID, "continue")
        self.total_label = (By.CSS_SELECTOR, ".summary_total_label")

    def fill_customer_info(self, first_name: str, last_name: str, postal_code: str):
        self.wait.until(
            EC.visibility_of_element_located(self.first_name)
        ).send_keys(first_name)
        self.driver.find_element(*self.last_name).send_keys(last_name)
        self.driver.find_element(*self.postal_code).send_keys(postal_code)
        self.wait.until(
            EC.element_to_be_clickable(self.continue_button)
        ).click()

    def get_total(self) -> str:
        total = self.wait.until(
            EC.visibility_of_element_located(self.total_label)
        )
        return total.text
