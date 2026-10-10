import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Базовый класс для всех страниц, содержащий общие методы работы."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver: WebDriver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, 20)

    def find_element(self, locator: tuple[str, str]) -> WebElement:
        """Ожидает видимости элемента на странице и возвращает его."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator: tuple[str, str]) -> None:
        """Ожидает кликабельности элемента и совершает по нему клик."""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator: tuple[str, str], text: str) -> None:
        """Ожидает видимости поля, очищает его и заполняет текстом."""
        element: WebElement = self.find_element(locator)
        element.clear()
        element.send_keys(text)


class LoginPage(BasePage):
    """Страница авторизации в веб-приложении YouGile."""

    HEADER_LOGIN_BUTTON = (
        By.XPATH,
        "//a[contains(@class, 'login') or contains(text(), 'Войти')] | "
        "//button[contains(text(), 'Войти')]",
    )
    EMAIL_INPUT = (By.XPATH, "//input[@type='email' or @placeholder='E-mail']")
    PASSWORD_INPUT = (
        By.XPATH,
        "//input[@type='password' or @placeholder='Пароль']",
    )
    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[contains(text(), 'Войти') "
        "and not(contains(@class, 'header'))]",
    )

    @allure.step("Открыть стартовую страницу YouGile и перейти к форме входа")
    def open(self) -> None:
        self.driver.get("https://yougile.com")
        self.click(self.HEADER_LOGIN_BUTTON)
        self.find_element(self.EMAIL_INPUT)

    @allure.step("Авторизоваться под пользователем")
    def login(self, email: str, password: str) -> None:
        self.type(self.EMAIL_INPUT, email)
        password_field: WebElement = self.find_element(self.PASSWORD_INPUT)
        password_field.clear()
        password_field.send_keys(password)

        try:
            submit_btn: WebElement = self.find_element(self.SUBMIT_BUTTON)
            self.driver.execute_script("arguments[0].click();", submit_btn)
        except Exception:
            password_field.send_keys(Keys.ENTER)


class DashboardPage(BasePage):
    """Главная страница рабочего пространства
    и управление проектами."""

    WORKSPACE_LAYOUT = (
        By.XPATH,
        "//*[contains(text(), 'Мой профиль') "
        "or contains(text(), 'Мои задачи') "
        "or contains(@id, 'app')]",
    )
    MY_COMPANY_TAB = (
        By.XPATH,
        "//*[contains(@class, 'sidebar') or contains(@class, 'menu')]"
        "//*[contains(text(), 'Моя компания')] | //*[text()='Моя компания']",
    )
    CREATE_PROJECT_BUTTON = (
        By.XPATH,
        "//*[contains(text(), 'Добавить проект')]",
    )
    PROJECT_WITH_TASKS_OPTION = (
        By.XPATH,
        "//*[contains(text(), 'Проект с задачами')]",
    )
    PROJECT_TITLE_INPUT = (
        By.XPATH,
        "//input[@type='text' and (contains(@placeholder, 'название') "
        "or @name='title')]",
    )
    SUBMIT_PROJECT_BUTTON = (
        By.XPATH,
        "//*[contains(text(), 'Добавить проект с задачами') "
        "or text()='Добавить проект с задачами']",
    )

    @allure.step("Ожидание полной загрузки главного дашборда")
    def wait_for_load(self) -> None:
        self.find_element(self.WORKSPACE_LAYOUT)

    @allure.step("Создать новый проект с названием '{title}'")
    def create_project(self, title: str) -> None:
        self.click(self.MY_COMPANY_TAB)
        self.click(self.CREATE_PROJECT_BUTTON)
        self.click(self.PROJECT_WITH_TASKS_OPTION)
        self.type(self.PROJECT_TITLE_INPUT, title)

        submit_btn = self.find_element(self.SUBMIT_PROJECT_BUTTON)
        try:
            self.wait.until(
                EC.element_to_be_clickable(self.SUBMIT_PROJECT_BUTTON)
            ).click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", submit_btn)

    @allure.step("Открыть проект с названием '{title}'")
    def open_project(self, title: str) -> None:
        project_locator = (
            By.XPATH,
            f"//*[text()='{title}' or contains(text(), '{title}')]",
        )
        self.click(project_locator)

    @allure.step("Проверить отображение проекта '{title}' в списке")
    def is_project_visible(self, title: str) -> bool:
        project_locator = (By.XPATH, f"//*[contains(text(), '{title}')]")
        return self.find_element(project_locator).is_displayed()


class ProjectBoardPage(BasePage):
    """Страница работы внутри доски выбранного проекта."""

    BOARD_CANVAS = (
        By.XPATH,
        "//*[contains(@class, 'board') or contains(@class, 'column') "
        "or contains(@id, 'app')]",
    )
    ADD_TASK_BUTTON = (
        By.XPATH,
        "//*[contains(@class, 'add-task')"
        " or contains(@class, 'create-task') "
        "or contains(text(), 'Добавить задачу')"
        " or contains(text(), 'Создать задачу')]",
    )
    TASK_INPUT = (
        By.XPATH,
        "//textarea[contains(@class, 'task')"
        " or contains(@placeholder, 'задач')] | "
        "//input[contains(@class, 'new-task')"
        " or contains(@placeholder, 'задач')] | "
        "//*[contains(@class, 'input')"
        " or @focused]//textarea",
    )

    @allure.step("Ожидание прогрузки доски проекта")
    def wait_for_board_load(self) -> None:
        self.find_element(self.BOARD_CANVAS)

    @allure.step("Добавить задачу '{title}' в колонку")
    def add_task(self, title: str) -> None:
        self.wait.until(EC.element_to_be_clickable
                        (self.ADD_TASK_BUTTON)).click()

        task_field = self.wait.until(
            EC.visibility_of_element_located(self.TASK_INPUT),
            message="Текстовое поле ввода новой задачи не"
                    " появилось после клика 'Добавить задачу'",
        )

        task_field.clear()
        task_field.send_keys(title)
        task_field.send_keys(Keys.ENTER)

    @allure.step("Проверить наличие задачи '{title}' на доске")
    def is_task_visible(self, title: str) -> bool:
        task_locator = (By.XPATH, f"//*[contains(text(), '{title}')]")
        return self.find_element(task_locator).is_displayed()