import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    """Фикстура для инициализации и закрытия браузера Chrome"""
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")  # Открывать на весь экран

    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()
