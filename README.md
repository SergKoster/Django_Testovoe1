# Barter Platform

Монолитное веб-приложение на Django для организации обмена вещами между пользователями.

## 🚀 Технологический стек

- **Язык:** Python 3.12.8
- **Фреймворк:** Django 5.2.1 
- **База данных:** PostgreSQL  
- **Шаблонизация:** Django Templates  
- **Формы & Валидация:** Django Forms  
- **Хранение изображений:** Django ImageField + Pillow  
- **Авторизация:** `django.contrib.auth` + сообщения `django.contrib.messages`  
- **Тестирование:** `django.test.TestCase`  
- **Админ-панель:** `django.contrib.admin`

## 📦 Установка и запуск

### 1. Клонируем репозиторий
```bash
git clone https://github.com/your-org/django-barter-platform.git
cd django-barter-platform
```
### 2. Создаем виртуальное окружение и устанавливаем зависимости

```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Переменные окружения

Создайте файл `.env` в корне проекта, на основе примера `.env.example`:

```dotenv
SECRET_KEY=super_puper_secret_key
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password228
POSTGRES_DB=barter_platform_database
POSTGRES_HOST=db
```

### 4. Настройка базы и миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Создание суперпользователя

```bash
python manage.py createsuperuser
# Введите username, email и пароль
```

### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

Откройте в браузере [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## ✅ Тестирование

```bash
# Запуск всех тестов
python manage.py test
```
