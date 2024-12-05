![example event parameter](https://github.com/solomongrad/foodgram/actions/workflows/main.yml/badge.svg)

![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Описание проекта 
Foodgram - сайт для ценителей вкусной еды.

На этом сайте вы сможете делиться своими рецептами со всем миром, а также просматривать чужие рецепты. При желании вы сможете добавить некоторые рецепты в корзину и перед походом в магазин вам будет достаточно скачать вашу корзину, тогда вам в удобном формате будет выдан список покупок. А если вам понравился рецепт, но вы пока не планируете его использовать, вы можете просто добавить его в избранное! Также вы можете подписываться на других пользователей и следить за тем, что они выкладывают.

У проекта доступна документация, для того, чтобы её посмотреть, клонируйте проект на свой компьютер и из директории infra, выполните команду:
```bash
docker compose up
```
##### и откройте страницу http://localhost/api/docs/

сайт работает на домене: https://foodgramfree.sytes.net/about

## Как запустить проект на удалённом сервере?

##### 1. Клонировать репозиторий.
```bash
git clone git@github.com:solomongrad/foodgram.git
```

##### 2. Проверить, установлен ли у вас docker
```bash
sudo systemctl status docker
```

##### 2.1. Установить докер, в случае его отсуствия
```bash
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

##### 3. Создать новую папку и файл на сервере
```bash
mkdir foodgram && cd foodgram && touch .env
```

##### 4. Заполнить .env на основе .env.example и скопировать на сервер файл docker-compose.production.yml

##### 5. Запустить проект.
```bash
sudo docker compose -f docker-compose.production.yml up -d
```

##### 6. Выполнить миграции, и создать на сервере теги и ингредиенты
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_tags
```

##### Также возможно всё это сделать с помощью Github Actions!

### Автор

[Куделин Роман](https://github.com/solomongrad)