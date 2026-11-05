from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_session_storage_auth():
    driver = webdriver.Chrome()

    driver.get("https://www.gitflic.ru/")

    user1 = driver.add_cookie({
        "name": "SESSION",
        "value": "OWIwYTE2ODEtNDk1Ny00MzEzLTk3YTYtYTJjNzE4YTBhNzI5",
        "domain": "gitflic.ru"
    })

    driver.add_cookie({
        "name": "cookiesAccepted",
        "value": "true",
        "domain": "gitflic.ru"
    })
    driver.refresh()
    driver.maximize_window()
    driver.get("https://gitflic.ru/user/user1_test")

    url_user1 = driver.current_url

    driver.delete_all_cookies()
    driver.refresh()

    user2 = driver.add_cookie({
        "name": "SESSION",
        "value": "OWIwYTE2ODEtNDk1Ny00MzEzLTk3YTYtYTJjNzE4YTBhNzI5",
        "domain": "gitflic.ru"
    })

    driver.add_cookie({
        "name": "cookiesAccepted",
        "value": "true",
        "domain": "gitflic.ru"
    })

    driver.refresh()

    driver.get("https://gitflic.ru/user/user2_test")

    url_user2 = driver.current_url

    assert url_user1 != url_user2

    driver.quit()
