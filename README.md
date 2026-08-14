# DC Web Search

Модуль веб-поиска для demon-cry.

## Установка

```bash
pip install git+https://github.com/Mooncore-inc/dc-web-search.git
```

## Настройка

1. Добавить сервис SearXNG в ваш `docker-compose.yml`:

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    ports:
      - "8080:8080"
    volumes:
      - ./searxng:/etc/searxng:z
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
    restart: unless-stopped
```

2. Создать файл конфигурации `modules/web_search/config.json`:

```json
{
    "searxng_url": "http://localhost:8080"
}
```

3. Поднять SearXNG:

```bash
docker compose up -d
```
