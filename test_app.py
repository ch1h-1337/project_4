import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


class GameStoreUITest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.base_url = "http://localhost:5000"
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def test_home_page_loads(self):
        self.driver.get(self.base_url + "/")
        header = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertIn("Добро пожаловать", header.text)

        cards = self.driver.find_elements(By.CLASS_NAME, "card")
        self.assertGreaterEqual(len(cards), 1)

    def test_navigate_to_about(self):
        self.driver.get(self.base_url + "/")
        about_btn = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "О нас")))
        about_btn.click()
        time.sleep(1)
        self.assertIn("/about", self.driver.current_url)
        about_heading = self.driver.find_element(By.TAG_NAME, "h2")
        self.assertIn("О нашем магазине", about_heading.text)

    def test_register(self):
        self.driver.get(self.base_url + "/auth")

        username = f"user{int(time.time())}"
        password = "testpass123"

        # Регистрация
        reg_form = self.driver.find_element(By.ID, "registerForm")
        reg_form.find_element(By.NAME, "username").send_keys(username)
        reg_form.find_element(By.NAME, "password").send_keys(password)
        reg_form.find_element(By.TAG_NAME, "button").click()

        time.sleep(2)
        msg = self.driver.find_element(By.ID, "message").text
        self.assertIn("Регистрация успешна", msg)




if __name__ == "__main__":
    unittest.main()
