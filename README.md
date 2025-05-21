# Структура проекта

```text
├── bot/
│   ├── database.py          # Работа с базой данных
│   ├── Dockerfile           # Конфигурация Docker для сервиса бота
│   ├── models.py            # Модели данных
│   ├── requirements.txt     # Зависимости Python
│   └── telegram_bot.py      # Основная логика Telegram-бота

├── client/
│   ├── public/              # Статические файлы
│   │   └── favicon.ico      # Иконка сайта
│   ├── src/
│   │   ├── components/      # UI-компоненты интерфейса
│   │   ├── context/         # Контекст и аутентификация
│   │   ├── pages/           # Страницы приложения
│   │   ├── App.js           # Конфигурация маршрутов
│   │   └── index.js         # Точка входа клиентской части
│   ├── Dockerfile           # Сборка клиентского приложения
│   ├── package.json         # Конфигурация npm
│   └── package-lock.json    # Точные версии зависимостей

├── server/
│   ├── Dockerfile           # Сборка серверной части
│   ├── main.py              # Точка входа API-сервера
│   └── requirements.txt     # Python-зависимости сервера

└── docker-compose.yaml      # Оркестрация всех сервисов
```
Для запуска проекта выполните команду
```
docker compose up
```
