# coverage run manage.py test -v 2
# coverage html
from django.contrib.auth import get_user_model
from django.test import TestCase
from openapi_tester import SchemaTester
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.test import (APIClient, APIRequestFactory, APITestCase,
                                 force_authenticate)

from .models import Ingredient, Recipe, Tag

User = get_user_model()
schema_tester = SchemaTester(schema_file_path="../../docs/openapi-schema.yml")


# setUp() Это встроенный метод Unittest, он автоматически вызывается перед запуском каждого test case:
# setUpClass() он вызывается лишь один раз, перед запуском всех test case класса.

class UsersTests(TestCase):
    def setUp(self):
        self.guest_client = APIClient()
        self.user1 = User.objects.create_user(username='Stas',
                                              email='stas@stas.ru',
                                              password='Qweqwe123123333')
        self.user2 = User.objects.create_user(username='Ivan',
                                              email='Ivan@Ivan.ru')
        self.user3 = User.objects.create_user(username='Nikolay',
                                              email='Nikolay@Nikolay.ru')
        self.superuser = User.objects.create_user(username='Pavel',
                                                  email='Pavel@Pavel.ru',
                                                  is_superuser=1, is_staff=1)
        self.authorized_client1 = APIClient()
        self.authorized_client2 = APIClient()
        self.authorized_client3 = APIClient()
        self.authorized_superuser = APIClient()
        self.authorized_client1.force_authenticate(self.user1)
        self.authorized_client2.force_authenticate(self.user2)
        self.authorized_client3.force_authenticate(self.user3)
        self.authorized_superuser.force_authenticate(self.superuser)

    # def test_api_page(self):
    #    response = self.guest_client.get('/api/')
    #    self.assertEqual(response.status_code, 200)

    # Профиль пользователя http://localhost/api/users/{id}/
    # Список пользователей
    def test_user_profile(self):
        fields = 'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed'
        response = self.authorized_client1.get('/api/users/')
        response_superuser = self.authorized_superuser.get('/api/users/')
        test_data = response.json()
        test_data_superuser = response_superuser.json()
        assert type(test_data) == dict, (
            'Проверьте, что при GET запросе на `/api/users/` возвращается словарь (dict)')
        assert type(test_data_superuser) == dict, (
            'Проверьте, что при GET запросе на `/api/users/` возвращается словарь (dict)')
        # assert len(test_data['results']) == User.objects.count(), ('Проверьте, что при GET запросе пользователя на `/api/users/` возвращается весь список пользователей')
        assert len(test_data_superuser['results']) == User.objects.count(), (
            'Проверьте, что при GET запросе администратора на `/api/users/` возвращается весь список пользователей')
        print(test_data)
        test_user = test_data['results'][0]
        print(test_user)
        for field in fields:
            assert field in test_user, (
                f'Поле `{field}` отсутствует в списоке полей `fields` сериализатора модели User')
        # print(test_data2)
        # print(test_data3)
        # print(test_data_superuser)
        # print(len(test_data_superuser['results']))
        # assert type(test_data_superuser) == list, (
        #    'Проверьте, что при GET запросе на `/api/v1/posts/` возвращается список'
        # )

    # Регистрация пользователя
    # POST http://localhost/api/users/
    def test_register_user(self):
        request = self.guest_client.post('/api/users/',
                                         {'email': 'vpupkin@yandex.ru'})
        assert type(request.json()) == dict, (
            'Проверьте, что при POST запросе на `/api/users/` возвращается словарь (dict)')
        assert request.status_code == 400, "Все поля для регистрации должны быть обязательны для заполнения"
        request = self.guest_client.post('/api/users/',
                                         {'email': 'vpupkin@yandex.ru',
                                          'username': 'vasyapupkin', })
        assert request.status_code == 400, "Все поля для регистрации должны быть обязательны для заполнения"
        request = self.guest_client.post('/api/users/',
                                         {'email': 'vpupkin@yandex.ru',
                                          'username': 'vasyapupkin',
                                          'password': 'Qwerty1233454'})
        assert request.status_code == 400, "Все поля для регистрации должны быть обязательны для заполнения"
        request = self.guest_client.post('/api/users/',
                                         {'email': 'vpupkin@yandex.ru',
                                          'username': 'vasyapupkin',
                                          'password': 'Qwerty1233454',
                                          'first_name': 'Вася'})
        assert request.status_code == 400, "Все поля для регистрации должны быть обязательны для заполнения"
        user_count = User.objects.count()
        request = self.guest_client.post('/api/users/',
                                         {'email': 'vpupkin@yandex.ru',
                                          'username': 'vasyapupkin',
                                          'password': 'Qwerty1233454',
                                          'first_name': 'Вася',
                                          'last_name': 'Пупкин'})
        assert request.status_code == 201, "Код успешной регистрации не верный"
        assert User.objects.count() == (
                user_count + 1), "Количество пользователей не верное"
        assert type(request.json()) == dict, (
            'Проверьте, что при POST запросе на `/api/users/` возвращается словарь (dict)')
        fields = ('email', 'username', 'first_name', 'last_name', 'id')
        for field in request.json():
            assert field in fields, "При запросе возвращаются не все поля"

    # Профиль пользователя
    # GET http://localhost/api/users/{id}/
    def test_get_user_profile(self):
        request = self.guest_client.get(f'/api/users/{self.user1.id}/')
        assert request.status_code == 401, "Не авторизованным пользователям запрещено смотреть профили пользователей"
        request = self.authorized_client1.get(
            f'/api/users/{User.objects.all().count}/')
        assert request.status_code == 404, "Такого пользователя не существует, должна возвращатся 404 ошибка"
        request = self.authorized_client1.get(f'/api/users/{self.user1.id}/')
        fields = (
            'email', 'username', 'first_name', 'last_name', 'id',
            'is_subscribed')
        for field in request.json():
            assert field in fields, "При запросе возвращаются не все поля"

    # Текущий пользователь
    # GET http://localhost/api/users/me/
    def test_get_user_me(self):
        request = self.guest_client.get('/api/users/me/')
        assert request.status_code == 401, "Не авторизованным пользователям запрещено смотреть профили пользователя"

        request = self.authorized_client1.get('/api/users/me/')
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'id', 'is_subscribed')
        for field in request.json():
            assert field in fields, "При запросе возвращаются не все поля"
        assert request.json()[
                   'username'] == 'Stas', "Возвращаемая почта не соответствует ожиданию"
        assert request.json()[
                   'email'] == 'stas@stas.ru', "Возвращаемая почта не соответствует ожиданию"

    # Изменение пароля
    # POST http://localhost/api/users/set_password/
    def test_user_set_password(self):
        url = '/api/users/set_password/'
        request = self.guest_client.post(url, {"new_password": "newpassword",
                                               "current_password": "oldpassword"})
        assert request.status_code == 401, "Не авторизованным пользователям запрещено менять пароль"

        passwd = 'Qweqwe123123333'
        test_user = User.objects.create_user(username='StasPassword',
                                             email='newtestuser@localhost.ru',
                                             password=passwd)
        test_authorized_client = APIClient()
        test_authorized_client.force_authenticate(test_user)

        request = test_authorized_client.post(url, {
            "new_password": "MyNewSuperPassw0rd"})
        assert request.status_code == 400, "Должна быть ошибка из за неправильно переданных полей"

        request = test_authorized_client.post(url,
                                              {"current_password": passwd})
        assert request.status_code == 400, "Должна быть ошибка из за неправильно переданных полей"

        request = test_authorized_client.post(url, {
            "new_password": "MyNewSuperPassw0rd", "current_password": passwd})
        assert request.status_code == 204, "Пароль должен быть изменен и возвращён 204 код"

    # Получить токен авторизации
    # POST http://localhost/api/auth/token/login/
    def test_get_token(self):
        url = '/api/auth/token/login/'
        request = self.guest_client.post(url, {"password": "RandomUser000",
                                               "email": "random@localhost.ru"})
        assert request.status_code == 400, "Такой пары логина и пароля не существует"

        request = self.guest_client.post(url, {'password': 'Qweqwe123123333',
                                               'email': 'stas@stas.ru'})
        assert request.status_code == 200, "Получение токена было успешно но что то пошло не так"
        assert 'auth_token' in request.json(), "Ошибка при получении токена"

    # Удаление токена
    # POST http://localhost/api/auth/token/logout/
    def test_delete_token(self):
        url = '/api/auth/token/logout/'
        request = self.guest_client.post(url)
        assert request.status_code == 401, "Пользователь не авторизован, должно возвращать код ошибки 401"

        request = self.authorized_client1.post(url)
        assert request.status_code == 204, "Токен должен быть удален и возвращать 204 код"


class TagTests(TestCase):
    def setUp(self):
        self.guest_client = APIClient()

        self.tag1 = Tag.objects.create(name='Завтрак', color='#FFFFF1',
                                       slug='breakfast ')
        self.tag2 = Tag.objects.create(name='Обед', color='#FFFFF2',
                                       slug='lunch')
        self.tag3 = Tag.objects.create(name='Ужин', color='#FFFFF3',
                                       slug='dinner')

    # Cписок тегов
    # GET http://localhost/api/tags/
    def test_tags_list(self):
        url = '/api/tags/'
        request = self.guest_client.get(url)
        assert request.status_code == 200, "Теги должны возвращать 200 код"
        assert len(
            request.json()) == Tag.objects.count(), "Колличество тегов не верно"
        fields = 'id', 'name', 'color', 'slug'
        assert fields in request.json(), "Не все поля возвращаются в тегах"

    # Получение тега
    # GET http://localhost/api/tags/{id}/
    def test_tag_get(self):
        url = '/api/tags/'
        test_tag = Tag.objects.all()[0]
        request = self.guest_client.get(f'{url}{test_tag.id}/')
        assert request.status_code == 200, "Теги должны возвращать 200 код"
        fields = 'id', 'name', 'color', 'slug'
        assert len(request.json()) == len(
            fields), "Колличество полей тега не верно"
        for field in fields:
            assert field in request.json(), "Не все поля возвращаются в тегах"

        request = self.guest_client.get(f'{url}{Tag.objects.count() + 1}/')
        assert request.status_code == 404, "Тег не существует должен возвращать 404 код"

    # Проверка запрещенный запросов
    # POST, PUT, DELETE
    def test_tags_forbidden(self):
        url = '/api/tags/'
        request = self.guest_client.post(url)
        assert request.status_code != 200, "POST запрос для тегов должен должен быть разрешен только для администратора"

        url = '/api/tags/'
        test_tag = Tag.objects.all()[0]
        request = self.guest_client.get(f'{url}{test_tag.id}/')
        assert request.status_code != 200, "POST запрос для тегов должен должен быть разрешен только для администратора"


# Ингредиенты
class IngredientTests(TestCase):
    def setUp(self):
        self.guest_client = APIClient()

        self.ingredient1 = Ingredient.objects.create(
            name='Ингредиент 1', measurement_unit='кг'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Ингредиент 2', measurement_unit='л'
        )
        self.ingredient3 = Ingredient.objects.create(
            name='3 Ингредиент', measurement_unit='мм'
        )

    # Список ингредиентов
    # GET http://localhost/api/ingredients/
    def test_ingredients_list(self):
        url = '/api/ingredients/'
        request = self.guest_client.get(url)
        assert request.status_code == 200, "Ингредиенты должны возвращать 200 код"
        assert len(
            request.json()) == Ingredient.objects.count(), "Колличество ингредиентов не верно"
        fields = 'id', 'name', 'measurement_unit'
        for field in fields:
            assert field in request.json()[
                0], "Не все поля возвращаются в ингредиентах"

        names = 'Ингредиент', '3 Ин'
        for name in names:
            request = self.guest_client.get(f'{url}?name={name}')
            assert request.status_code == 200, "Поиск по частичному вхождению в начале названия ингредиента возвращать 200 код"
            assert len(request.json()) == Ingredient.objects.filter(
                name__startswith=name).count(), "Поиск по частичному вхождению в начале названия: Колличество ингредиентов по не верно"


# Рецепты
class RecipeTests(TestCase):
    def setUp(self):
        self.guest_client = APIClient()
        self.user1 = User.objects.create_user(username='Stas',
                                              email='stas@stas.ru',
                                              password='Qweqwe123123333')
        self.user2 = User.objects.create_user(username='Ivan',
                                              email='Ivan@Ivan.ru')

        self.ingredient1 = Ingredient.objects.create(
            name='Ингредиент 1', measurement_unit='кг'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Ингредиент 2', measurement_unit='л'
        )
        self.ingredient3 = Ingredient.objects.create(
            name='3 Ингредиент', measurement_unit='мм'
        )

        self.recipe1 = Recipe.objects.create(
            author=self.user1,
            name='Рецепт 1', text='Текст Рецепта 1', cooking_time=1,
            image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
        )
        self.recipe1.ingredients.add(self.ingredient1)
        self.recipe1.ingredients.add(self.ingredient2)

    # Список рецептов
    # GET http://localhost/api/recipes/
    def test_recipes_list(self):
        url = '/api/recipes/'
        request = self.guest_client.get(url)
        assert request.status_code == 200, "Рецепты должны возвращать 200 код"
        print(f'Recipe.objects.count(): {Recipe.objects.count()}')
        test_obj = Recipe.objects.all()[0]
        print(f'Recipe.objects.all(): {test_obj}')
        assert request.json()[
                   'count'] == Recipe.objects.count(), "Колличество рецептов не верно"
        fields = 'id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        print(request.json()['results'][0])
        for field in fields:
            assert field in request.json()['results'][
                0], f'Поле {field} не возвращается в рецептах'


# Избранное
class BaseAPITestCase(APITestCase):
    """ Base test class for api views including schema validation """

    @staticmethod
    def assertResponse(response: Response, **kwargs) -> None:
        """ helper to run validate_response and pass kwargs to it """
        schema_tester.validate_response(response=response, **kwargs)


class MyAPITests(BaseAPITestCase):
    def test_some_view(self):
        response = self.client.get('api/recipes/')
        print(response)
        print(response.headers)
        #schema_tester.validate_response(response=response)
        #self.assertResponse(response)
