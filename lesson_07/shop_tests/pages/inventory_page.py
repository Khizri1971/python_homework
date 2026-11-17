from pages.cart_page import CartPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MainShopPage:
    """Каталог товаров: добавление в корзину и переход в корзину."""

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.products = {
            "Sauce Labs Backpack": (By.ID, "add-to-cart-sauce-labs-backpack"),
            "Sauce Labs Bolt T-Shirt": (By.ID, "add-to-cart-sauce-labs-bolt-t-shirt"),
            "Sauce Labs Onesie": (By.ID, "add-to-cart-sauce-labs-onesie"),
        }
        self.cart_link = (By.CSS_SELECTOR, ".shopping_cart_container a")

    def add_product_to_cart(self, product_name: str):
        locator = self.products[product_name]
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def add_products_to_cart(self, *product_names: str):
        for name in product_names:
            self.add_product_to_cart(name)

    def open_cart(self) -> "CartPage":
        self.wait.until(
            EC.element_to_be_clickable(self.cart_link)
        ).click()
        return CartPage(self.driver)
