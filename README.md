<h1 align="center">Twittly</h1>
<p align="center">
<img src="./readme_assets/image.jpeg" width="25%"> 
<h2 align="center">Сервис микроблогов</h2>

## Описание
Twittly — это приложение, где вы делитесь мыслями, новостями и моментами 
из жизни, подписываетесь на интересных людей и обсуждаете их посты.

## Стек
- **Backend**: FastAPI, SQLAlchemy (async), PostgreSQL
- **Frontend**: Vue.js (статика), nginx
- **Инфраструктура**: Docker, docker-compose

## Функциональность
- [ ] Регистрация по `api-key`
- [ ] Просмотр профиля (своего и чужого)
- [ ] Подписка/отписка
- [ ] Создание/удаление твитов
- [ ] Лента твитов (свои + подписки)
- [ ] Лайки
- [ ] Загрузка медиа

## Запуск
### Prod
```bash
docker-compose up -d --build
```

### Dev
```bash
 docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

## Документация Swagger
http://localhost:8000/docs#/


## Отчёты (тесты, линтеры, покрытие)

Чтобы сгенерировать отчёты, выполните из папки server/:
```bash
mkdir -p tests/reports && \
pytest tests/ \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=html:tests/reports/coverage \
  -v | tee tests/reports/pytest.txt ; \
flake8 app/ --output-file tests/reports/flake8.txt ; \
mypy app/ > tests/reports/mypy.txt 2>&1
```

