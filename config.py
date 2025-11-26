"""
Конфигурация приложения AI-сортировщика файлов.
Configuration for the AI file sorter application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# ============================================
# ПУТИ К ПАПКАМ / FOLDER PATHS
# ============================================

# Папка для сортировки (по умолчанию Downloads)
SOURCE_FOLDER = os.getenv('SOURCE_FOLDER') or str(Path.home() / 'Downloads')

# ============================================
# НАСТРОЙКИ ИИ / AI SETTINGS
# ============================================

# API ключ OpenAI (опционально)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# ============================================
# РЕЖИМ ОТЛАДКИ / DEBUG MODE
# ============================================

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ============================================
# КАТЕГОРИИ ФАЙЛОВ / FILE CATEGORIES
# ============================================

# Словарь категорий и соответствующих расширений
# Dictionary of categories and their file extensions
FILE_CATEGORIES = {
    'Изображения': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.raw'],
    'Документы': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
    'Видео': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.3gp'],
    'Аудио': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
    'Архивы': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tar.gz', '.tar.bz2'],
    'Программы': ['.exe', '.msi', '.dmg', '.deb', '.rpm', '.app', '.apk'],
    'Код': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.ts', '.json', '.xml', '.yaml', '.yml'],
    'Шрифты': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
    'Другое': []  # Для файлов, не подходящих под другие категории
}

# ============================================
# ПРАВИЛА ПЕРЕИМЕНОВАНИЯ / RENAMING RULES
# ============================================

# Формат даты для переименования файлов
DATE_FORMAT = '%Y-%m-%d'

# Формат времени для переименования файлов
TIME_FORMAT = '%H-%M-%S'

# Шаблон для переименования: {date}_{type}_{original}
# Template for renaming: {date}_{type}_{original}
RENAME_TEMPLATE = '{date}_{category}_{original}'

# ============================================
# НАСТРОЙКИ WATCHDOG / WATCHDOG SETTINGS
# ============================================

# Интервал проверки изменений в секундах
WATCH_INTERVAL = 1

# Задержка перед обработкой файла (чтобы дождаться завершения загрузки)
PROCESSING_DELAY = 2

# ============================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ / LOGGING SETTINGS
# ============================================

# Уровень логирования
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'

# Формат логов
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
