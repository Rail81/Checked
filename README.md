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
