# Установка базового образа Python
FROM python:3.8-slim

# Установка зависимостей
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Копирование исходного кода в контейнер
COPY . /app

# Запуск скрипта main.py
CMD ["python", "main.py"]