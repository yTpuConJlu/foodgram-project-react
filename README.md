# praktikum_new_diplom
![example workflow](https://github.com/yTpuConJlu/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Foodgram - «Продуктовый помощник»
Это онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект использует базу данных PostgreSQL. Проект запускается в трёх контейнерах (nginx, PostgreSQL и Django) (контейнер frontend используется лишь для подготовки файлов) через docker-compose на сервере. Образ с проектом загружается на Docker Hub.

## Cтек технологий:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

# Системные требования
- выделенный linux Ubuntu сервер
- внешний IP адрес
- зарегистрировнное доменное имя
- nginx 
- docker
- docker compose



Клонируйте репозиторий<br/>

git clone https://github.com/yTpuConJlu/foodgram-project-react.git

Создайте файл .env в директории infra и заполните его данными по этому 
образцу:

DB_ENGINE=django.db.backends.postgresql<br/>
DB_NAME=foodgram<br/>
POSTGRES_USER=foodgram<br/>
POSTGRES_PASSWORD=foodgram<br/>
DB_HOST=db # название сервиса (контейнера)<br/>
DB_PORT=5432<br/>
SECRET_KEY=c014k!^brz&9mz_%n1u(@@o9h6k3t*f$l!tk36u3(2nyi7aseq

скопируйте папку /infra/<br/>
scp -r infra/* di@<you server ip>:/home/< username >/foodgram/<br/>
<br/>

подключитесь к серверу через ssh и перейдите в каталог<br/>
/home/< username >/foodgram/infra/<br/>
<br/>
запустите установку и сборку контейнеров<br/>
docker compose up -d<br/>

Выполните миграции в контейнере созданном их образа foodgram:

docker-compose exec -T < CONTAINER ID > python manage.py migrate<br/>

Создайте суперпользователя

docker ps<br/>

docker exec -it < CONTAINER ID > bash <br/>

python manage.py createsuperuser<br/>

Загрузите статические файлы в контейнере созданном из образа foodgram:

docker-compose exec -T < CONTAINER ID > python manage.py collectstatic --no-input


## Сайт:

ytpu-conjlu.servebeer.com 51.250.94.102

доступ к админке:

login: banderolfromacer@yandex.ru
password: Admin

Автор backend сервисов
[Илья Щербаков](https://github.com/yTpuConJlu)

Автор frontend сервисов
[Yandex Praktikum](https://github.com/yandex-praktikum)