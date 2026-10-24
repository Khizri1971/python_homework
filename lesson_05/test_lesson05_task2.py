from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def test_form_submission():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    base_url = "https://httpbin.qa-territory.online/forms/post"
    driver.get(base_url)
    name_input = driver.find_element(By.NAME, "custname")
    name_input.send_keys("Khizri")
    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
    submit_button.click()
    current_url = driver.current_url
    assert current_url != base_url, f"URL не изменился: {current_url}"
    driver.quit()
