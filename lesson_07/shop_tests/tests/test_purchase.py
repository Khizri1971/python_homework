from pages.login_page import LoginPage


def test_purchase(browser):
    shop = LoginPage(browser).open()
    shop = shop.login("standard_user", "secret_sauce")

    shop.add_products_to_cart(
        "Sauce Labs Backpack",
        "Sauce Labs Bolt T-Shirt",
        "Sauce Labs Onesie",
    )
    cart = shop.open_cart()
    checkout = cart.open_checkout()
    checkout.fill_customer_info("Петр", "Прохоров", "629603")

    total = checkout.get_total()

    assert "58.29" in total
