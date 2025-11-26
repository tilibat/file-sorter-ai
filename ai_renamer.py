"""
Модуль для ИИ-переименования файлов.
Module for AI-powered file renaming.
"""

import os
from datetime import datetime
from typing import Optional

import config
import utils


class AIRenamer:
    """
    Класс для умного переименования файлов.
    На первом этапе использует простую логику: дата + тип файла.
    В будущем может быть расширен для использования OpenAI API.
    
    Class for smart file renaming.
    Initially uses simple logic: date + file type.
    Can be extended to use OpenAI API in the future.
    """
    
    def __init__(self):
        """
        Инициализация переименователя.
        Initialize the renamer.
        """
        self.api_key = config.OPENAI_API_KEY
        self.use_ai = bool(self.api_key)
        
        if self.use_ai:
            utils.log_action("ИНИЦИАЛИЗАЦИЯ", "AIRenamer", "Режим ИИ включен")
        else:
            utils.log_action("ИНИЦИАЛИЗАЦИЯ", "AIRenamer", "Простой режим (без ИИ)")
    
    def suggest_name(self, file_path: str) -> str:
        """
        Предложить новое имя для файла.
        Suggest a new name for the file.
        
        На первом этапе использует формат: ДАТА_КАТЕГОРИЯ_оригинальное_имя
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Предложенное новое имя файла
        """
        if not utils.file_exists(file_path):
            utils.log_error("ПРЕДЛОЖЕНИЕ ИМЕНИ", file_path, "Файл не существует")
            return ""
        
        # Получаем информацию о файле
        original_name = utils.get_file_name(file_path)
        extension = utils.get_file_extension(file_path)
        category = self._get_category(file_path)
        date = utils.get_current_date()
        
        # Формируем новое имя
        if self.use_ai:
            # TODO: В будущем здесь будет вызов OpenAI API
            # для анализа содержимого файла и генерации умного имени
            new_name = self._generate_ai_name(file_path, original_name, category, date)
        else:
            # Простой режим: дата_категория_оригинальное_имя
            new_name = self._generate_simple_name(original_name, category, date)
        
        return f"{new_name}{extension}"
    
    def rename_file(self, old_path: str, new_name: str) -> Optional[str]:
        """
        Переименовать файл.
        Rename the file.
        
        Args:
            old_path: Текущий путь к файлу
            new_name: Новое имя файла
            
        Returns:
            Новый путь к файлу или None в случае ошибки
        """
        if not utils.file_exists(old_path):
            utils.log_error("ПЕРЕИМЕНОВАНИЕ", old_path, "Файл не существует")
            return None
        
        try:
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_name)
            
            # Проверяем, не существует ли уже файл с таким именем
            if utils.file_exists(new_path) and old_path != new_path:
                utils.log_error("ПЕРЕИМЕНОВАНИЕ", old_path, 
                              f"Файл {new_name} уже существует")
                return None
            
            os.rename(old_path, new_path)
            utils.log_action("ПЕРЕИМЕНОВАНИЕ", old_path, f"→ {new_path}")
            
            return new_path
            
        except OSError as e:
            utils.log_error("ПЕРЕИМЕНОВАНИЕ", old_path, str(e))
            return None
    
    def batch_rename(self, folder_path: str) -> dict:
        """
        Переименовать все файлы в папке.
        Rename all files in folder.
        
        Args:
            folder_path: Путь к папке
            
        Returns:
            Словарь с результатами
        """
        results = {
            "renamed": 0,
            "errors": 0,
            "details": []
        }
        
        if not utils.directory_exists(folder_path):
            utils.log_error("ПАКЕТНОЕ ПЕРЕИМЕНОВАНИЕ", folder_path, "Папка не существует")
            return results
        
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if not os.path.isfile(item_path):
                    continue
                
                if utils.is_hidden_file(item_path) or utils.is_temp_file(item_path):
                    continue
                
                # Предлагаем новое имя
                new_name = self.suggest_name(item_path)
                
                if new_name and new_name != item:
                    # Переименовываем
                    if self.rename_file(item_path, new_name):
                        results["renamed"] += 1
                        results["details"].append(f"✓ {item} → {new_name}")
                    else:
                        results["errors"] += 1
                        results["details"].append(f"✗ {item}")
        
        except OSError as e:
            utils.log_error("ПАКЕТНОЕ ПЕРЕИМЕНОВАНИЕ", folder_path, str(e))
        
        utils.log_action("ЗАВЕРШЕНО", folder_path, 
                        f"Переименовано: {results['renamed']}, ошибок: {results['errors']}")
        
        return results
    
    def _get_category(self, file_path: str) -> str:
        """
        Получить категорию файла по расширению.
        Get file category by extension.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Название категории
        """
        extension = utils.get_file_extension(file_path)
        
        for category, extensions in config.FILE_CATEGORIES.items():
            if extension in extensions:
                return category
        
        return 'Другое'
    
    def _generate_simple_name(self, original_name: str, category: str, date: str) -> str:
        """
        Генерация простого имени: дата_категория_оригинал.
        Generate simple name: date_category_original.
        
        Args:
            original_name: Оригинальное имя файла
            category: Категория файла
            date: Текущая дата
            
        Returns:
            Новое имя файла без расширения
        """
        # Очищаем имя категории (убираем кириллицу для совместимости)
        category_clean = self._transliterate(category)
        
        # Формируем новое имя
        return f"{date}_{category_clean}_{original_name}"
    
    def _generate_ai_name(self, file_path: str, original_name: str, 
                         category: str, date: str) -> str:
        """
        Генерация имени с помощью ИИ (заглушка для будущего расширения).
        Generate name using AI (stub for future extension).
        
        В будущем здесь будет:
        - Анализ содержимого изображений через GPT-4 Vision
        - Анализ текстовых документов
        - Генерация осмысленных имен
        
        Args:
            file_path: Путь к файлу
            original_name: Оригинальное имя файла
            category: Категория файла
            date: Текущая дата
            
        Returns:
            Новое имя файла без расширения
        """
        # TODO: Реализовать вызов OpenAI API
        # Пока используем простую логику
        return self._generate_simple_name(original_name, category, date)
    
    def _transliterate(self, text: str) -> str:
        """
        Транслитерация русского текста в латиницу.
        Transliterate Russian text to Latin.
        
        Args:
            text: Текст на русском
            
        Returns:
            Транслитерированный текст
        """
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
            'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
            'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
            'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K',
            'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
            'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts',
            'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
            'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        result = []
        for char in text:
            result.append(translit_dict.get(char, char))
        
        return ''.join(result)
