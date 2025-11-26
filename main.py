#!/usr/bin/env python3
"""
AI-сортировщик файлов - Точка входа.
AI File Sorter - Entry point.

Учебный проект для практики в компании Texel.
Educational project for internship at Texel company.
"""

import argparse
import sys
import time
from typing import Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Заглушка для определения класса - используется object как базовый класс
    # чтобы класс FileHandler мог быть определен без ошибок, даже если watchdog не установлен.
    # Функциональность watchdog проверяется в runtime через WATCHDOG_AVAILABLE.
    FileSystemEventHandler = object
    Observer = None

import config
import utils
from file_organizer import FileOrganizer
from ai_renamer import AIRenamer
from duplicate_finder import DuplicateFinder


class FileHandler(FileSystemEventHandler):
    """
    Обработчик событий файловой системы для автоматического режима.
    File system event handler for automatic mode.
    """
    
    def __init__(self, organizer: FileOrganizer):
        self.organizer = organizer
        self.last_processed = {}
    
    def on_created(self, event):
        """Обработка создания нового файла."""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # Пропускаем скрытые и временные файлы
        if utils.is_hidden_file(file_path) or utils.is_temp_file(file_path):
            return
        
        # Задержка для завершения загрузки файла
        time.sleep(config.PROCESSING_DELAY)
        
        # Проверяем, не обработали ли мы этот файл недавно
        current_time = time.time()
        if file_path in self.last_processed:
            if current_time - self.last_processed[file_path] < 5:
                return
        
        self.last_processed[file_path] = current_time
        
        # Определяем категорию и перемещаем
        if utils.file_exists(file_path):
            category = self.organizer.categorize_file(file_path)
            self.organizer.move_file(file_path, category)


def show_menu():
    """
    Отображение интерактивного меню.
    Display interactive menu.
    """
    print("\n" + "=" * 50)
    print("🗂️  AI-СОРТИРОВЩИК ФАЙЛОВ")
    print("=" * 50)
    print(f"📁 Рабочая папка: {config.SOURCE_FOLDER}")
    print("-" * 50)
    print("1. Сортировать файлы по категориям")
    print("2. Найти дубликаты")
    print("3. Переименовать файлы (умное переименование)")
    print("4. Запустить автоматический режим (watchdog)")
    print("5. Показать конфигурацию")
    print("0. Выход")
    print("-" * 50)


def sort_files(source_folder: Optional[str] = None):
    """
    Выполнить сортировку файлов.
    Perform file sorting.
    """
    print("\n🔄 Начинаем сортировку файлов...")
    organizer = FileOrganizer(source_folder)
    results = organizer.organize_files()
    
    print("\n📊 Результаты сортировки:")
    print(f"   ✅ Отсортировано: {results['organized']}")
    print(f"   ❌ Ошибок: {results['errors']}")
    
    if results['details']:
        print("\n📝 Детали:")
        for detail in results['details'][:10]:  # Показываем первые 10
            print(f"   {detail}")
        if len(results['details']) > 10:
            print(f"   ... и ещё {len(results['details']) - 10} файлов")


def find_duplicates(source_folder: Optional[str] = None):
    """
    Найти дубликаты файлов.
    Find duplicate files.
    """
    print("\n🔍 Поиск дубликатов...")
    folder = source_folder or config.SOURCE_FOLDER
    finder = DuplicateFinder()
    report = finder.get_duplicates_report(folder)
    print("\n" + report)


def rename_files(source_folder: Optional[str] = None):
    """
    Переименовать файлы с помощью ИИ.
    Rename files using AI.
    """
    print("\n✏️  Умное переименование файлов...")
    folder = source_folder or config.SOURCE_FOLDER
    renamer = AIRenamer()
    results = renamer.batch_rename(folder)
    
    print("\n📊 Результаты переименования:")
    print(f"   ✅ Переименовано: {results['renamed']}")
    print(f"   ❌ Ошибок: {results['errors']}")
    
    if results['details']:
        print("\n📝 Детали:")
        for detail in results['details'][:10]:
            print(f"   {detail}")
        if len(results['details']) > 10:
            print(f"   ... и ещё {len(results['details']) - 10} файлов")


def watch_folder(source_folder: Optional[str] = None):
    """
    Запустить автоматический режим отслеживания.
    Start automatic watch mode.
    """
    if not WATCHDOG_AVAILABLE:
        print("\n❌ Ошибка: библиотека watchdog не установлена!")
        print("   Установите её командой: pip install watchdog")
        return
    
    folder = source_folder or config.SOURCE_FOLDER
    
    if not utils.directory_exists(folder):
        print(f"\n❌ Ошибка: папка {folder} не существует!")
        return
    
    print(f"\n👁️  Запуск автоматического режима...")
    print(f"   Отслеживаемая папка: {folder}")
    print("   Нажмите Ctrl+C для остановки\n")
    
    organizer = FileOrganizer(folder)
    organizer.create_category_folders()
    
    event_handler = FileHandler(organizer)
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(config.WATCH_INTERVAL)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n⏹️  Автоматический режим остановлен.")
    
    observer.join()


def show_config():
    """
    Показать текущую конфигурацию.
    Show current configuration.
    """
    print("\n⚙️  ТЕКУЩАЯ КОНФИГУРАЦИЯ")
    print("=" * 50)
    print(f"Рабочая папка: {config.SOURCE_FOLDER}")
    print(f"Режим отладки: {'Включен' if config.DEBUG else 'Выключен'}")
    print(f"OpenAI API: {'Настроен' if config.OPENAI_API_KEY else 'Не настроен'}")
    print(f"\nФормат даты: {config.DATE_FORMAT}")
    print(f"Интервал watchdog: {config.WATCH_INTERVAL} сек")
    print(f"Задержка обработки: {config.PROCESSING_DELAY} сек")
    
    print("\n📂 КАТЕГОРИИ ФАЙЛОВ:")
    for category, extensions in config.FILE_CATEGORIES.items():
        ext_str = ', '.join(extensions[:5])
        if len(extensions) > 5:
            ext_str += f" (+{len(extensions) - 5})"
        print(f"   {category}: {ext_str}")


def interactive_mode():
    """
    Интерактивный режим работы программы.
    Interactive mode of the program.
    """
    while True:
        show_menu()
        
        try:
            choice = input("\nВыберите действие (0-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 До свидания!")
            break
        
        if choice == '1':
            sort_files()
        elif choice == '2':
            find_duplicates()
        elif choice == '3':
            rename_files()
        elif choice == '4':
            watch_folder()
        elif choice == '5':
            show_config()
        elif choice == '0':
            print("\n👋 До свидания!")
            break
        else:
            print("\n❌ Неверный выбор. Попробуйте ещё раз.")
        
        input("\nНажмите Enter для продолжения...")


def main():
    """
    Главная функция - точка входа в программу.
    Main function - entry point of the program.
    """
    parser = argparse.ArgumentParser(
        description='🗂️ AI-сортировщик файлов - умная организация файлов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  python main.py                     # Интерактивный режим
  python main.py --sort              # Разовая сортировка
  python main.py --watch             # Автоматический режим
  python main.py --find-duplicates   # Поиск дубликатов
  python main.py --rename            # Умное переименование
  python main.py --folder ~/Desktop  # Указать другую папку

Проект для учебной практики в компании Texel.
        '''
    )
    
    parser.add_argument(
        '--sort', '-s',
        action='store_true',
        help='Выполнить разовую сортировку файлов'
    )
    
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Запустить автоматический режим отслеживания'
    )
    
    parser.add_argument(
        '--find-duplicates', '-d',
        action='store_true',
        help='Найти дубликаты файлов'
    )
    
    parser.add_argument(
        '--rename', '-r',
        action='store_true',
        help='Переименовать файлы (умное переименование)'
    )
    
    parser.add_argument(
        '--folder', '-f',
        type=str,
        default=None,
        help='Путь к папке для обработки (по умолчанию ~/Downloads)'
    )
    
    parser.add_argument(
        '--config', '-c',
        action='store_true',
        help='Показать текущую конфигурацию'
    )
    
    args = parser.parse_args()
    
    # Проверяем, указаны ли какие-либо команды
    if args.config:
        show_config()
    elif args.sort:
        sort_files(args.folder)
    elif args.watch:
        watch_folder(args.folder)
    elif args.find_duplicates:
        find_duplicates(args.folder)
    elif args.rename:
        rename_files(args.folder)
    else:
        # Если команды не указаны - запускаем интерактивный режим
        interactive_mode()


if __name__ == '__main__':
    main()
