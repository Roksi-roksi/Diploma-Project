from typing import Generator
import pytest
import allure
import requests
import config


@pytest.fixture(scope="function")
def auth_token() -> str:
    """Фикстура возвращает готовый токен из конфигурационного файла."""
    assert (
        hasattr(config, "USER_TOKEN") and config.USER_TOKEN
    ), "Пожалуйста, добавьте существующий токен в config.py как USER_TOKEN"
    return str(config.USER_TOKEN)


@pytest.fixture(scope="function")
def created_project_id(auth_token: str) -> Generator[str, None, None]:
    """Фикстура создает проект перед тестом и гарантированно удаляет его после."""
    url: str = f"{config.API_URL}/projects"
    headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}
    payload: dict[str, str] = {"title": "Temporary Autotest Project"}

    response: requests.Response = requests.post(
        url, json=payload, headers=headers
    )
    assert (
        response.status_code == 201
    ), f"Не удалось создать проект для фикстуры: {response.text}"
    project_id: str = response.json()["id"]

    yield project_id

    delete_url: str = f"{config.API_URL}/projects/{project_id}"
    requests.delete(delete_url, headers=headers)

@pytest.mark.api
@allure.feature("Панель управления проектами YouGile (API)")
class TestYouGileAPI:

    @allure.story("Управление проектами")
    @allure.title("Позитивный тест получения информации о проекте по ID")
    @allure.description(
        "Тест проверяет корректность получения метаданных существующего проекта по его уникальному ID.\n\n"
        "Шаги теста:\n"
        "1. Создание временного проекта через фикстуру.\n"
        "2. Отправка GET-запроса на эндпоинт /projects/{id} с валидным Bearer-токеном.\n"
        "3. Проверка соответствия ID в ответе исходному проекту.\n"
        "Ожидаемый результат: Код ответа 200 OK, тело ответа содержит валидные поля id и title."
    )
    def test_api_get_project_by_id(
        self, auth_token: str, created_project_id: str
    ) -> None:
        """Проверка успешного получения данных существующего проекта по его ID."""
        url: str = f"{config.API_URL}/projects/{created_project_id}"
        headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}

        response: requests.Response = requests.get(url, headers=headers)

        assert (
            response.status_code == 200
        ), f"Не удалось получить проект: {response.text}"
        assert (
            response.json().get("id") == created_project_id
        ), "ID в ответе не совпадает с запрашиваемым"
        assert (
            "title" in response.json()
        ), "Ответ сервера не содержит название проекта"

    @allure.story("Управление проектами")
    @allure.title("Позитивный тест на изменение названия проекта (PUT)")
    @allure.description(
        "Тест проверяет возможность частичного редактирования данных проекта методом PUT.\n\n"
        "Шаги теста:\n"
        "1. Отправка PUT-запроса на URL созданного ранее проекта.\n"
        "2. Передача новой строки 'Updated Project Title via Autotest' в свойстве 'title'.\n"
        "Ожидаемый результат: Код ответа 200 OK, подтверждение успешного изменения названия в структуру ответа."
    )
    def test_api_update_project_title(
        self, auth_token: str, created_project_id: str
    ) -> None:
        """Проверка успешного обновления названия существующего проекта через метод PUT."""
        url: str = f"{config.API_URL}/projects/{created_project_id}"
        headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}

        new_title: str = "Updated Project Title via Autotest"
        payload: dict[str, str] = {"title": new_title}

        response: requests.Response = requests.put(
            url, json=payload, headers=headers
        )

        assert (
            response.status_code == 200
        ), (
            f"Не удалось изменить проект: "
            f"{response.text}"
        )
        assert (
            response.json().get("title") == new_title
            or "id" in response.json()
        ), (
            f"Ответ сервера не содержит подтверждения изменений: "
            f"{response.text}"
        )


    @allure.story("Авторизация")
    @allure.title("Негативный тест авторизации"
                  " с лишним полем в JSON-схеме")
    @allure.description(
        "Тест проверяет строгую валидацию входной схемы"
        " запроса (JSON-схемы) сервером.\n\n"
        "Шаги теста:\n"
        "1. Отправка POST-запроса на получение"
        " списка компаний /auth/companies.\n"
        "2. Передача избыточного параметра"
        " 'companyId' в теле запроса.\n"
        "Ожидаемый результат: Код ответа 400 Bad Request,"
        " сообщение об ошибке валидации:"
        " 'property companyId should not exist'."
    )
    def test_api_auth_with_extra_property(self) -> None:
        """Проверка валидации схемы: запрос
         отклоняется, если передано лишнее поле companyId."""
        url: str = f"{config.API_URL}/auth/companies"
        payload: dict[str, str] = {
            "login": config.LOGIN,
            "password": config.PASSWORD,
            "companyId": config.COMPANY_ID,
        }
        response: requests.Response = requests.post(url, json=payload)

        assert response.status_code == 400
        assert (
            "property companyId should not exist" in response.json()["message"]
        )

    @allure.story("Авторизация")
    @allure.title("Негативный тест доступа к"
                  " ресурсам с невалидным токеном")
    @allure.description(
        "Тест проверяет политику безопасности и"
        " защиту API-интерфейсов от неавторизованного доступа.\n\n"
        "Шаги теста:\n"
        "1. Отправка GET-запроса на получение"
        " списка проектов /projects.\n"
        "2. Передача в заголовке Authorization"
        " заведомо сломанного/несуществующего токена.\n"
        "Ожидаемый результат: Код ответа 401"
        " Unauthorized, доступ заблокирован."
    )
    def test_api_get_projects_unauthorized(self) -> None:
        """Проверка генерации ошибки 401 Unauthorized
         при использовании невалидного токена."""
        url: str = f"{config.API_URL}/projects"
        headers: dict[str, str] = {
            "Authorization": "Bearer invalid_or_expired_token_12345"
        }

        response: requests.Response = requests.get(url, headers=headers)

        assert (
            response.status_code == 401
        ), f"Ожидался код 401, но получен {response.status_code}"

    @allure.story("Управление проектами")
    @allure.title("Позитивный тест создания"
                  " нового проекта (POST)")
    @allure.description(
        "Тест проверяет возможность успешного"
        " создания проекта"
        " в системе YouGile через API.\n\n"
        "Шаги теста:\n"
        "1. Отправка POST-запроса на эндпоинт /projects"
        " с валидным Bearer-токеном.\n"
        "2. Передача обязательного параметра 'title'"
        " со значением 'New Diploma Project'.\n"
        "3. Проверка статус-кода ответа и структуры"
        " JSON (наличие id созданного проекта).\n"
        "Ожидаемый результат: Код ответа 201 Created,"
        " в теле ответа возвращается сгенерированный ID проекта."
    )
    def test_api_create_project_successful(self, auth_token: str) -> None:
        """Проверка успешного создания нового
         проекта через метод POST."""
        url: str = f"{config.API_URL}/projects"
        headers: dict[str, str] = {"Authorization":
                                       f"Bearer {auth_token}"}

        project_title: str = "New Diploma Project"
        payload: dict[str, str] = {"title": project_title}

        response: requests.Response = requests.post(
            url, json=payload, headers=headers
        )

        assert (
                response.status_code == 201
        ), (f"Не удалось создать проект. Ответ сервера:"
            f" {response.text}")

        response_data: dict = response.json()
        assert (
                "id" in response_data
        ), (f"Ответ сервера не содержит 'id'"
            f" созданного проекта: {response.text}")

        project_id: str = response_data["id"]
        delete_url: str = f"{config.API_URL}/projects/{project_id}"
        requests.delete(delete_url, headers=headers)

    @allure.story("Управление компаниями")
    @allure.title("Позитивный тест получения деталей компании по ID")
    @allure.description(
        "Тест проверяет корректность получения метаданных "
        "существующей компании по её уникальному ID.\n\n"
        "Шаги теста:\n"
        "1. Отправка GET-запроса на эндпоинт /api-v2/companies/{id} "
        "с валидным Bearer-токеном.\n"
        "2. Проверка соответствия статус-кода ответа (200 OK).\n"
        "3. Валидация структуры ответа: наличие обязательных "
        "полей id, title и timestamp.\n"
        "Ожидаемый результат: Код ответа 200 OK, тело ответа "
        "содержит корректные данные запрашиваемой компании."
    )
    def test_api_get_company_details_successful(self, auth_token: str) -> None:
        """Проверка успешного получения данных существующей компании."""
        url: str = f"{config.API_URL}/companies/{config.COMPANY_ID}"
        headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}

        response: requests.Response = requests.get(url, headers=headers)

        assert response.status_code == 200, (
            f"Не удалось получить детали компании. Ответ: {response.text}"
        )

        response_data: dict = response.json()

        assert response_data.get("id") == config.COMPANY_ID, (
            "ID в ответе не совпадает с запрашиваемым ID компании"
        )

        assert "title" in response_data, (
            "Ответ сервера не содержит название компании (title)"
        )

        assert "timestamp" in response_data, (
            "Ответ сервера не содержит временную метку (timestamp)"
        )

