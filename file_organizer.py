"""
Модуль для организации и сортировки файлов по категориям.
Module for organizing and sorting files by categories.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

import config
import utils


class FileOrganizer:
    """
    Класс для организации файлов по папкам на основе их типа.
    Class for organizing files into folders based on their type.
    """
    
    def __init__(self, source_folder: Optional[str] = None):
        """
        Инициализация с путем к папке для сортировки.
        Initialize with path to folder for sorting.
        
        Args:
            source_folder: Путь к папке (по умолчанию из конфига)
        """
        self.source_folder = source_folder or config.SOURCE_FOLDER
        self.categories = config.FILE_CATEGORIES
        self.organized_count = 0
        self.error_count = 0
        
        utils.log_action("ИНИЦИАЛИЗАЦИЯ", self.source_folder, "FileOrganizer создан")
    
    def organize_files(self) -> dict:
        """
        Сортировка всех файлов в папке по категориям.
        Sort all files in folder by categories.
        
        Returns:
            Словарь с результатами: {"organized": count, "errors": count, "details": [...]}
        """
        if not utils.directory_exists(self.source_folder):
            utils.log_error("СОРТИРОВКА", self.source_folder, "Папка не существует")
            return {"organized": 0, "errors": 1, "details": ["Папка не существует"]}
        
        # Создаем папки для категорий
        self.create_category_folders()
        
        results = {
            "organized": 0,
            "errors": 0,
            "details": []
        }
        
        # Получаем список файлов в папке
        files = self._get_files_list()
        
        if not files:
            utils.log_action("СОРТИРОВКА", self.source_folder, "Нет файлов для сортировки")
            results["details"].append("Нет файлов для сортировки")
            return results
        
        utils.log_action("СОРТИРОВКА", self.source_folder, f"Найдено {len(files)} файлов")
        
        for file_path in files:
            try:
                # Пропускаем скрытые и временные файлы
                if utils.is_hidden_file(file_path) or utils.is_temp_file(file_path):
                    continue
                
                # Определяем категорию файла
                category = self.categorize_file(file_path)
                
                # Перемещаем файл
                if self.move_file(file_path, category):
                    results["organized"] += 1
                    file_name = utils.get_file_name_with_extension(file_path)
                    results["details"].append(f"✓ {file_name} → {category}")
                else:
                    results["errors"] += 1
                    
            except Exception as e:
                results["errors"] += 1
                utils.log_error("СОРТИРОВКА", file_path, str(e))
        
        utils.log_action("ЗАВЕРШЕНО", self.source_folder, 
                        f"Отсортировано: {results['organized']}, ошибок: {results['errors']}")
        
        return results
    
    def categorize_file(self, file_path: str) -> str:
        """
        Определение категории файла по его расширению.
        Determine file category by its extension.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Название категории
        """
        extension = utils.get_file_extension(file_path)
        
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        
        return 'Другое'
    
    def move_file(self, file_path: str, category: str) -> bool:
        """
        Перемещение файла в папку соответствующей категории.
        Move file to the corresponding category folder.
        
        Args:
            file_path: Путь к файлу
            category: Название категории
            
        Returns:
            True если перемещение успешно
        """
        try:
            # Создаем путь к папке категории
            category_folder = os.path.join(self.source_folder, category)
            utils.create_directory(category_folder)
            
            # Получаем имя файла
            file_name = utils.get_file_name_with_extension(file_path)
            
            # Создаем путь назначения
            destination = os.path.join(category_folder, file_name)
            
            # Если файл с таким именем уже существует, добавляем номер
            destination = self._get_unique_path(destination)
            
            # Перемещаем файл
            shutil.move(file_path, destination)
            
            utils.log_action("ПЕРЕМЕЩЕНИЕ", file_path, f"→ {destination}")
            return True
            
        except Exception as e:
            utils.log_error("ПЕРЕМЕЩЕНИЕ", file_path, str(e))
            return False
    
    def create_category_folders(self) -> None:
        """
        Создание папок для всех категорий.
        Create folders for all categories.
        """
        for category in self.categories.keys():
            folder_path = os.path.join(self.source_folder, category)
            if utils.create_directory(folder_path):
                utils.log_action("СОЗДАНИЕ ПАПКИ", folder_path, "")
    
    def _get_files_list(self) -> list:
        """
        Получение списка файлов в папке (без подпапок).
        Get list of files in folder (without subfolders).
        
        Returns:
            Список путей к файлам
        """
        files = []
        try:
            for item in os.listdir(self.source_folder):
                item_path = os.path.join(self.source_folder, item)
                if os.path.isfile(item_path):
                    files.append(item_path)
        except OSError as e:
            utils.log_error("ЧТЕНИЕ ПАПКИ", self.source_folder, str(e))
        
        return files
    
    def _get_unique_path(self, file_path: str) -> str:
        """
        Получение уникального пути (если файл уже существует, добавляем номер).
        Get unique path (add number if file already exists).
        
        Args:
            file_path: Исходный путь к файлу
            
        Returns:
            Уникальный путь к файлу
        """
        if not utils.file_exists(file_path):
            return file_path
        
        directory = os.path.dirname(file_path)
        name = utils.get_file_name(file_path)
        extension = utils.get_file_extension(file_path)
        
        counter = 1
        while True:
            new_name = f"{name}_{counter}{extension}"
            new_path = os.path.join(directory, new_name)
            if not utils.file_exists(new_path):
                return new_path
            counter += 1
