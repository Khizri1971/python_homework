from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html"


class CalculatorPage:
    """Страница медленного калькулятора."""

    def __init__(self, driver):
        self.driver = driver
        self.delay_input = (By.CSS_SELECTOR, "#delay")
        self.screen = (By.CSS_SELECTOR, ".screen")
        self._button = "//span[text()='{}']"

    def open(self) -> "CalculatorPage":
        self.driver.get(URL)
        return self

    def set_delay(self, seconds: str):
        delay = self.driver.find_element(*self.delay_input)
        delay.clear()
        delay.send_keys(seconds)

    def press(self, *buttons: str):
        for button in buttons:
            self.driver.find_element(
                By.XPATH, self._button.format(button)
            ).click()

    def get_screen_text(self) -> str:
        screen = self.driver.find_element(*self.screen)
        return screen.text

    def wait_for_result(self, expected: str, timeout: int) -> bool:
        return WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element(self.screen, expected)
        )
