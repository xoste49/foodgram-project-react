# Foodgram
[![DRF Workflow](https://github.com/xoste49/foodgram-project-react/actions/workflows/foodgram__workflow.yml/badge.svg?branch=master)](https://github.com/xoste49/foodgram-project-react/actions/workflows/foodgram__workflow.yml) <br/>
Приложение на Django Rest Framework «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

[Пример развернутого проекта](http://51.250.19.69/)
### Шаблон наполнения env-файла
```
DEBUG=0 # указываем, включение или отключение отладки
SECRET_KEY=topsecretcode # Секретный ключ в настройках Django, сгенерировать можно здесь https://djecrety.ir/
DJANGO_ALLOWED_HOSTS=* # Список строк, представляющих имена хостов/доменов, которые может обслуживать этот сайт Django.
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
POSTGRES_DB=foodgram # имя базы данных
SQL_HOST=db # название сервиса (контейнера)
SQL_PORT=5432  # порт для подключения к БД
STATIC_URL=static/django/ # Ссылка до статики backend django 
```

### Quick Start from Docker
Описание команд для запуска приложения в Docker контейнерах
```
git clone https://github.com/xoste49/foodgram-project-react
cd foodgram-project-react/infra/
touch .env
nano .env # заполняем по шаблоны выше
sudo docker-compose -f docker-compose-release.yml up -d
# Сбор статики
sudo docker-compose exec web python manage.py collectstatic --no-input
# Создание миграций
sudo docker-compose exec web python manage.py makemigrations
sudo docker-compose exec web python manage.py migrate
# Перезапускаем контейнеры
sudo docker-compose restart
# Создаём администратора
sudo docker-compose exec web python manage.py createsuperuser
```

### Contact me
GitHub - [@xoste49](https://github.com/xoste49)<br/>
Telegram - https://t.me/xoste49