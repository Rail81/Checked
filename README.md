# Система управления документами с уведомлениями в Telegram

Система для управления документами с функцией уведомления сотрудников через Telegram бота. Позволяет загружать документы, отслеживать их прочтение сотрудниками и получать статистику.

## Основные возможности

### Веб-интерфейс
- Загрузка и управление документами
- Фильтрация документов по отделам и типам
- Просмотр статистики ознакомления с документами
- Выгрузка статистики в Excel
- Управление сотрудниками и отделами
- Отображение прогресса ознакомления с документами

### Telegram бот
- Регистрация сотрудников
- Уведомления о новых документах
- Подтверждение ознакомления через QR-код
- Просмотр статистики и списка непрочитанных документов
- Команды:
  - `/start` - Начало работы/регистрация
  - `/stats` - Личная статистика
  - `/unread` - Непрочитанные документы
  - `/help` - Справка

## Инструкция по развертыванию на VPS Debian 12

### 1. Подготовка сервера

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка необходимых пакетов
apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx git -y
```

### 2. Клонирование репозитория

```bash
# Клонирование проекта
git clone https://github.com/Rail81/Checked.git
cd Checked
```

### 3. Настройка базы данных PostgreSQL

```bash
# Вход в PostgreSQL
su - postgres -c "psql"

# В консоли PostgreSQL выполните:
CREATE DATABASE your_database_name;
CREATE USER your_user_name WITH PASSWORD 'your_password';
ALTER ROLE your_user_name SET client_encoding TO 'utf8';
ALTER ROLE your_user_name SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_user_name SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_user_name;
\q
```

### 4. Настройка виртуального окружения и установка зависимостей

```bash
# Создание и активация виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 5. Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта:

```bash
# Пример содержимого .env файла
DATABASE_URL=postgresql://your_user_name:your_password@localhost/your_database_name
SECRET_KEY=your_secret_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### 6. Инициализация базы данных

```bash
# Применение миграций
flask db upgrade
```

### 7. Настройка Nginx

Создайте файл конфигурации Nginx:

```bash
nano /etc/nginx/sites-available/docmanagement

# Добавьте следующую конфигурацию:
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Создание символической ссылки
ln -s /etc/nginx/sites-available/docmanagement /etc/nginx/sites-enabled
```

### 8. Настройка systemd для автозапуска

Создайте файлы службы для приложения и бота:

```bash
# Для основного приложения
nano /etc/systemd/system/docmanagement.service

[Unit]
Description=Document Management System
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/Checked
Environment="PATH=/path/to/Checked/venv/bin"
ExecStart=/path/to/Checked/venv/bin/python app.py

[Install]
WantedBy=multi-user.target

# Для Telegram бота
nano /etc/systemd/system/docmanagement-bot.service

[Unit]
Description=Document Management System Bot
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/Checked
Environment="PATH=/path/to/Checked/venv/bin"
ExecStart=/path/to/Checked/venv/bin/python bot.py

[Install]
WantedBy=multi-user.target
```

### 9. Запуск служб

```bash
# Перезапуск Nginx
systemctl restart nginx

# Включение и запуск служб
systemctl enable docmanagement
systemctl start docmanagement
systemctl enable docmanagement-bot
systemctl start docmanagement-bot
```

### 10. Настройка брандмауэра

```bash
# Разрешение входящего трафика для веб-сервера
ufw allow 'Nginx Full'
ufw enable
```

### Проверка работоспособности

После выполнения всех шагов, ваше приложение должно быть доступно по адресу:
`http://your_domain_or_IP`

### Примечания по безопасности

1. Измените пароли и токены на безопасные значения
2. Настройте SSL/TLS сертификат для HTTPS
3. Регулярно обновляйте систему и зависимости
4. Создайте резервные копии базы данных

### Устранение неполадок

1. Проверьте логи приложения:
```bash
journalctl -u docmanagement
journalctl -u docmanagement-bot
```

2. Проверьте статус служб:
```bash
systemctl status docmanagement
systemctl status docmanagement-bot
```

3. Проверьте логи Nginx:
```bash
tail -f /var/log/nginx/error.log
```

## Установка на VPS (Debian 12)

### 1. Подготовка сервера

```bash
# Обновление системы
apt update
apt upgrade -y

# Установка необходимых пакетов
apt install -y python3-pip python3-venv postgresql nginx supervisor git

# Установка дополнительных зависимостей для работы с изображениями и QR-кодами
apt install -y libzbar0 python3-pil
```

### 2. Настройка PostgreSQL

```bash
# Создание базы данных и пользователя
sudo -u postgres psql -c "CREATE DATABASE doc_management;"
sudo -u postgres psql -c "CREATE USER doc_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE doc_management TO doc_user;"
```

### 3. Установка приложения

```bash
# Клонирование репозитория
git clone https://github.com/your-username/document-management-system.git
cd document-management-system

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 4. Настройка конфигурации

Создайте файл `.env`:
```bash
echo "DATABASE_URL=postgresql://doc_user:your_password@localhost/doc_management
SECRET_KEY=your-very-secret-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token" > .env
```

### 5. Настройка Supervisor

Создайте файл `/etc/supervisor/conf.d/docmanagement.conf`:
```ini
[program:docmanagement_web]
command=/path/to/venv/bin/python app.py
directory=/path/to/document-management-system
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/docmanagement_web.err.log
stdout_logfile=/var/log/docmanagement_web.out.log

[program:docmanagement_bot]
command=/path/to/venv/bin/python bot.py
directory=/path/to/document-management-system
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/docmanagement_bot.err.log
stdout_logfile=/var/log/docmanagement_bot.out.log
```

### 6. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/docmanagement`:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/document-management-system/static;
    }

    location /uploads {
        alias /path/to/document-management-system/uploads;
    }
}
```

```bash
# Активация конфигурации
ln -s /etc/nginx/sites-available/docmanagement /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 7. Запуск системы

```bash
# Перезапуск Supervisor для запуска приложения и бота
supervisorctl reread
supervisorctl update
supervisorctl start docmanagement_web
supervisorctl start docmanagement_bot
```

## Структура базы данных

### Таблицы
- `сотрудник` - информация о сотрудниках
- `документ` - загруженные документы
- `прочтение_документа` - записи об ознакомлении с документами
- `отдел` - структура отделов
- `организация` - информация об организациях

## Безопасность

- Аутентификация пользователей через веб-интерфейс
- Разграничение прав доступа (администратор/сотрудник)
- Защита от несанкционированного доступа к документам
- Безопасное хранение паролей
- Проверка подлинности через Telegram

## Мониторинг и логирование

- Логирование действий пользователей
- Отслеживание ошибок в работе бота
- Мониторинг статуса системы через Supervisor
- Логи nginx для веб-запросов

## Рекомендации по использованию

1. Регулярно делайте резервные копии базы данных
2. Следите за свободным местом на диске
3. Проверяйте логи на наличие ошибок
4. Обновляйте систему и зависимости

## Требования к системе

- Python 3.8+
- PostgreSQL 12+
- Nginx
- Минимум 1GB RAM
- 10GB свободного места на диске

## Поддержка

При возникновении проблем:
1. Проверьте логи приложения и бота
2. Убедитесь в правильности настроек в .env
3. Проверьте подключение к базе данных
4. Проверьте права доступа к файлам

## Обновление системы

```bash
# Остановка приложения
supervisorctl stop docmanagement_web
supervisorctl stop docmanagement_bot

# Обновление кода
git pull

# Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt

# Запуск приложения
supervisorctl start docmanagement_web
supervisorctl start docmanagement_bot
