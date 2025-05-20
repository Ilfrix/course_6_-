FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y gcc libpq-dev musl-dev
# ставим пакеты
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./telegram_bot.py"]