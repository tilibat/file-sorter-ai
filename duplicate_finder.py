"""
Модуль для поиска дубликатов файлов.
Module for finding duplicate files.
"""

import os
import hashlib
from collections import defaultdict
from typing import Dict, List, Optional

import utils


class DuplicateFinder:
    """
    Класс для поиска файлов-дубликатов на основе хеша содержимого.
    Class for finding duplicate files based on content hash.
    """
    
    # Размер блока для чтения файла (64 KB)
    BLOCK_SIZE = 65536
    
    def __init__(self):
        """
        Инициализация поиска дубликатов.
        Initialize duplicate finder.
        """
        utils.log_action("ИНИЦИАЛИЗАЦИЯ", "DuplicateFinder", "Создан")
    
    def find_duplicates(self, folder: str, recursive: bool = True) -> Dict[str, List[str]]:
        """
        Найти все дубликаты файлов в папке.
        Find all duplicate files in folder.
        
        Args:
            folder: Путь к папке для поиска
            recursive: Искать в подпапках (по умолчанию True)
            
        Returns:
            Словарь {hash: [список путей к файлам с этим хешем]}
            Возвращаются только хеши с более чем одним файлом
        """
        if not utils.directory_exists(folder):
            utils.log_error("ПОИСК ДУБЛИКАТОВ", folder, "Папка не существует")
            return {}
        
        utils.log_action("ПОИСК ДУБЛИКАТОВ", folder, 
                        f"Рекурсивный: {'Да' if recursive else 'Нет'}")
        
        # Группируем файлы по размеру (предварительная фильтрация)
        size_groups = self._group_by_size(folder, recursive)
        
        # Проверяем хеши только для файлов одинакового размера
        duplicates = self._find_hash_duplicates(size_groups)
        
        # Выводим статистику
        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        utils.log_action("ЗАВЕРШЕНО", folder, 
                        f"Найдено {len(duplicates)} групп дубликатов ({total_duplicates} лишних файлов)")
        
        return duplicates
    
    def calculate_hash(self, file_path: str) -> Optional[str]:
        """
        Вычислить SHA-256 хеш файла.
        Calculate SHA-256 hash of file.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Хеш файла в виде строки или None при ошибке
        """
        if not utils.file_exists(file_path):
            return None
        
        try:
            sha256_hash = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                for block in iter(lambda: f.read(self.BLOCK_SIZE), b''):
                    sha256_hash.update(block)
            
            return sha256_hash.hexdigest()
            
        except (IOError, OSError) as e:
            utils.log_error("ХЕШИРОВАНИЕ", file_path, str(e))
            return None
    
    def get_duplicates_report(self, folder: str, recursive: bool = True) -> str:
        """
        Получить текстовый отчет о дубликатах.
        Get text report about duplicates.
        
        Args:
            folder: Путь к папке
            recursive: Искать в подпапках
            
        Returns:
            Текстовый отчет
        """
        duplicates = self.find_duplicates(folder, recursive)
        
        if not duplicates:
            return "Дубликаты не найдены."
        
        lines = ["=" * 50, "ОТЧЕТ О ДУБЛИКАТАХ", "=" * 50, ""]
        
        total_wasted = 0
        group_num = 1
        
        for file_hash, files in duplicates.items():
            # Размер одного файла
            file_size = utils.get_file_size(files[0])
            # Размер лишних копий
            wasted = file_size * (len(files) - 1)
            total_wasted += wasted
            
            lines.append(f"Группа {group_num} ({len(files)} файлов, "
                        f"лишний объем: {utils.format_file_size(wasted)}):")
            lines.append(f"  Хеш: {file_hash[:16]}...")
            
            for i, file_path in enumerate(files):
                prefix = "  [ОРИГИНАЛ]" if i == 0 else "  [ДУБЛИКАТ]"
                lines.append(f"{prefix} {file_path}")
            
            lines.append("")
            group_num += 1
        
        lines.append("-" * 50)
        lines.append(f"Всего групп дубликатов: {len(duplicates)}")
        lines.append(f"Общий лишний объем: {utils.format_file_size(total_wasted)}")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def delete_duplicates(self, folder: str, keep_first: bool = True, 
                         dry_run: bool = True) -> Dict[str, int]:
        """
        Удалить файлы-дубликаты.
        Delete duplicate files.
        
        Args:
            folder: Путь к папке
            keep_first: Оставить первый файл из группы (по умолчанию True)
            dry_run: Только показать что будет удалено, не удалять (по умолчанию True)
            
        Returns:
            Словарь с результатами {"deleted": count, "freed_space": bytes}
        """
        duplicates = self.find_duplicates(folder)
        
        results = {
            "deleted": 0,
            "freed_space": 0
        }
        
        for file_hash, files in duplicates.items():
            # Определяем какие файлы удалять
            files_to_delete = files[1:] if keep_first else files
            
            for file_path in files_to_delete:
                file_size = utils.get_file_size(file_path)
                
                if dry_run:
                    utils.log_action("БУДЕТ УДАЛЕНО", file_path, 
                                   utils.format_file_size(file_size))
                else:
                    try:
                        os.remove(file_path)
                        utils.log_action("УДАЛЕНО", file_path, 
                                       utils.format_file_size(file_size))
                        results["deleted"] += 1
                        results["freed_space"] += file_size
                    except OSError as e:
                        utils.log_error("УДАЛЕНИЕ", file_path, str(e))
        
        return results
    
    def _group_by_size(self, folder: str, recursive: bool) -> Dict[int, List[str]]:
        """
        Группировка файлов по размеру.
        Group files by size.
        
        Args:
            folder: Путь к папке
            recursive: Искать в подпапках
            
        Returns:
            Словарь {размер: [список путей]}
        """
        size_groups = defaultdict(list)
        
        if recursive:
            for root, dirs, files in os.walk(folder):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    if utils.is_hidden_file(file_path):
                        continue
                    file_size = utils.get_file_size(file_path)
                    if file_size > 0:  # Пропускаем пустые файлы
                        size_groups[file_size].append(file_path)
        else:
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path) and not utils.is_hidden_file(file_path):
                    file_size = utils.get_file_size(file_path)
                    if file_size > 0:
                        size_groups[file_size].append(file_path)
        
        # Оставляем только группы с более чем одним файлом
        return {size: files for size, files in size_groups.items() if len(files) > 1}
    
    def _find_hash_duplicates(self, size_groups: Dict[int, List[str]]) -> Dict[str, List[str]]:
        """
        Поиск дубликатов по хешу среди файлов одинакового размера.
        Find duplicates by hash among files of the same size.
        
        Args:
            size_groups: Словарь {размер: [список путей]}
            
        Returns:
            Словарь {hash: [список путей]}
        """
        hash_groups = defaultdict(list)
        
        for size, files in size_groups.items():
            for file_path in files:
                file_hash = self.calculate_hash(file_path)
                if file_hash:
                    hash_groups[file_hash].append(file_path)
        
        # Оставляем только группы с более чем одним файлом
        return {h: files for h, files in hash_groups.items() if len(files) > 1}
