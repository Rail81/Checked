import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

class Config:
    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/doc_management')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Секретный ключ для сессий Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'ваш-секретный-ключ-по-умолчанию')
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Максимальный размер файла (16MB)
    
    # Настройки Telegram бота
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Поддерживаемые типы файлов
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'}
