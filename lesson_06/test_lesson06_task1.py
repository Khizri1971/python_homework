from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_dynamic_loading():
    driver = webdriver.Chrome()

    try:

        driver.get("https://the-internet.herokuapp.com/dynamic_loading/2")

        wait = WebDriverWait(driver, 10)

        start_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#start button")))
        start_button.click()

        hello_world_element = wait.until(EC.visibility_of_element_located((By.ID, "finish")))

        driver.save_screenshot("screenshot_hello_world.png")
        print("Скриншот сохранён как screenshot_hello_world.png")

        assert hello_world_element.text == "Hello World!", f"Ожидался текст 'Hello World!', но получен: '{hello_world_element.text}'"
        print("Проверка текста прошла успешно!")

    finally:

        driver.quit()
