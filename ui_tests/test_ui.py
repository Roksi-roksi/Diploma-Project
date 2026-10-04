from typing import Generator
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from pages import LoginPage, DashboardPage, ProjectBoardPage
import config


@pytest.fixture(scope="function")
def driver() -> Generator[WebDriver, None, None]:
    """Инициализирует чистый экземпляр браузера

    Chrome перед каждым автотестом.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    chrome_driver: WebDriver = webdriver.Chrome(
        service=service, options=options
    )
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture(scope="function")
def authenticated_dashboard(driver: WebDriver) -> DashboardPage:
    """Автоматически выполняет вход в систему перед началом тестов."""
    login_page = LoginPage(driver)
    dashboard_page = DashboardPage(driver)
    login_page.open()
    login_page.login(config.LOGIN, config.PASSWORD)
    dashboard_page.wait_for_load()
    return dashboard_page


@allure.feature("Интерфейс панели управления YouGile (UI)")
class TestYouGileUI:

    @allure.story("Авторизация пользователя")
    @allure.title("Успешный вход в систему с валидными учетными данными")
    @allure.description("Проверка процесса входа и редиректа на дашборд.")
    def test_ui_successful_login(self, driver: WebDriver) -> None:
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login(config.LOGIN, config.PASSWORD)
        dashboard_page = DashboardPage(driver)
        dashboard_page.wait_for_load()
        assert (
            "/team/" in driver.current_url
            or "workspace" in driver.current_url
        )

    @allure.story("Управление проектами")
    @allure.title("Создание нового проекта с названием 'вин'")
    @allure.description("Проверка успешного создания"
                        " проекта и его отображения.")
    def test_ui_create_project_diploma(
        self, authenticated_dashboard: DashboardPage
    ) -> None:
        dashboard_page: DashboardPage = authenticated_dashboard
        project_name: str = "вин"
        dashboard_page.create_project(project_name)
        assert dashboard_page.is_project_visible(
            project_name
        ), f"Проект '{project_name}' не появился"

    @allure.story("Управление проектами")
    @allure.title("Переход на внутреннюю страницу созданного проекта")
    @allure.description(
        "Проверка открытия внутренней доски задач проекта на холсте."
    )
    def test_ui_navigate_to_project(
        self, authenticated_dashboard: DashboardPage, driver: WebDriver
    ) -> None:
        dashboard_page: DashboardPage = authenticated_dashboard
        board_page = ProjectBoardPage(driver)
        project_name: str = "диплом-переход"
        with allure.step(
            f"Подготовка данных: Создание проекта '{project_name}'"
        ):
            dashboard_page.create_project(project_name)
            dashboard_page.wait_for_load()
        dashboard_page.open_project(project_name)
        board_page.wait_for_board_load()
        assert board_page.find_element(
            board_page.BOARD_CANVAS
        ).is_displayed(), "Холст доски не отобразился"

    @allure.story("Управление задачами")
    @allure.title(
        "Добавление новой задачи 'написать автотесты' через клавишу Enter"
    )
    @allure.description("Проверка создания задач на доске проекта.")
    def test_ui_add_task_to_column(
        self, authenticated_dashboard: DashboardPage, driver: WebDriver
    ) -> None:
        dashboard_page: DashboardPage = authenticated_dashboard
        board_page = ProjectBoardPage(driver)
        project_name: str = "диплом-задачи"
        task_name: str = "написать автотесты"
        with allure.step(
            f"Подготовка данных: Создание проекта '{project_name}'"
        ):
            dashboard_page.create_project(project_name)
            dashboard_page.wait_for_load()
        dashboard_page.open_project(project_name)
        board_page.wait_for_board_load()
        board_page.add_task(task_name)
        assert board_page.is_task_visible(
            task_name
        ), \
            f"Задача '{task_name}' не появилась на доске"
