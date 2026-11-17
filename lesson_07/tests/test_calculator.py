from lesson_07.pages import CalculatorPage


def test_calc(browser):
    calculator = CalculatorPage(browser).open()
    calculator.set_delay("45")
    calculator.press("7", "+", "8", "=")

    assert calculator.wait_for_result("15", timeout=45)
