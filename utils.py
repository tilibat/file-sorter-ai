"""
Вспомогательные функции для AI-сортировщика файлов.
Utility functions for the AI file sorter.
"""

import os
import logging
from datetime import datetime
from pathlib import Path

import config

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def get_file_size(file_path: str) -> int:
    """
    Получить размер файла в байтах.
    Get file size in bytes.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Размер файла в байтах
    """
    try:
        return os.path.getsize(file_path)
    except OSError as e:
        logger.error(f"Ошибка получения размера файла {file_path}: {e}")
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Форматировать размер файла в читаемый вид.
    Format file size to human-readable format.
    
    Args:
        size_bytes: Размер в байтах
        
    Returns:
        Отформатированная строка (например, "1.5 MB")
    """
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} ПБ"


def get_current_date() -> str:
    """
    Получить текущую дату в формате из конфигурации.
    Get current date in the format from config.
    
    Returns:
        Отформатированная дата
    """
    return datetime.now().strftime(config.DATE_FORMAT)


def get_current_time() -> str:
    """
    Получить текущее время в формате из конфигурации.
    Get current time in the format from config.
    
    Returns:
        Отформатированное время
    """
    return datetime.now().strftime(config.TIME_FORMAT)


def get_current_datetime() -> str:
    """
    Получить текущие дату и время.
    Get current date and time.
    
    Returns:
        Отформатированные дата и время
    """
    return f"{get_current_date()}_{get_current_time()}"


def file_exists(file_path: str) -> bool:
    """
    Проверить существование файла.
    Check if file exists.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        True если файл существует, иначе False
    """
    return os.path.isfile(file_path)


def directory_exists(dir_path: str) -> bool:
    """
    Проверить существование директории.
    Check if directory exists.
    
    Args:
        dir_path: Путь к директории
        
    Returns:
        True если директория существует, иначе False
    """
    return os.path.isdir(dir_path)


def create_directory(dir_path: str) -> bool:
    """
    Создать директорию если она не существует.
    Create directory if it doesn't exist.
    
    Args:
        dir_path: Путь к директории
        
    Returns:
        True если директория создана или уже существует
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Ошибка создания директории {dir_path}: {e}")
        return False


def get_file_extension(file_path: str) -> str:
    """
    Получить расширение файла в нижнем регистре.
    Get file extension in lowercase.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Расширение файла (например, ".txt")
    """
    return Path(file_path).suffix.lower()


def get_file_name(file_path: str) -> str:
    """
    Получить имя файла без расширения.
    Get file name without extension.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Имя файла без расширения
    """
    return Path(file_path).stem


def get_file_name_with_extension(file_path: str) -> str:
    """
    Получить полное имя файла с расширением.
    Get full file name with extension.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Полное имя файла
    """
    return Path(file_path).name


def log_action(action: str, file_path: str, details: str = "") -> None:
    """
    Записать действие в лог.
    Log an action.
    
    Args:
        action: Тип действия (например, "ПЕРЕМЕЩЕНИЕ", "ПЕРЕИМЕНОВАНИЕ")
        file_path: Путь к файлу
        details: Дополнительные детали
    """
    message = f"[{action}] {file_path}"
    if details:
        message += f" | {details}"
    logger.info(message)


def log_error(action: str, file_path: str, error: str) -> None:
    """
    Записать ошибку в лог.
    Log an error.
    
    Args:
        action: Тип действия
        file_path: Путь к файлу
        error: Описание ошибки
    """
    logger.error(f"[ОШИБКА {action}] {file_path} | {error}")


def is_hidden_file(file_path: str) -> bool:
    """
    Проверить, является ли файл скрытым.
    Check if file is hidden.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        True если файл скрытый
    """
    return Path(file_path).name.startswith('.')


def is_temp_file(file_path: str) -> bool:
    """
    Проверить, является ли файл временным.
    Check if file is temporary.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        True если файл временный
    """
    temp_extensions = ['.tmp', '.temp', '.crdownload', '.part', '.partial']
    return get_file_extension(file_path) in temp_extensions
