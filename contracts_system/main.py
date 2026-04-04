#!/usr/bin/env python3
"""
Основной скрипт для управления контрактами.
CLI интерфейс для аналитиков.

Использование:
    python main.py upload <файл> --version <версия> --description "Описание изменений"
    python main.py validate <файл>
    python main.py history <имя_файла>
    python main.py diff <имя_файла> <версия1> <версия2>
    python main.py report
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Добавляем текущую директорию в path для импорта
sys.path.insert(0, str(Path(__file__).parent))

from validator import ContractValidator, ValidationResult
from version_manager import VersionManager
from config import CONFIG

def parse_version(version_str: str) -> tuple:
    """Разбор строки версии в формате major.minor.patch"""
    parts = version_str.split('.')
    if len(parts) != 3:
        raise ValueError("Версия должна быть в формате X.Y.Z (например, 1.0.0)")
    return tuple(map(int, parts))

def auto_increment_version(latest_version: str) -> str:
    """Автоматическое увеличение версии"""
    if not latest_version:
        return "1.0.0"
    
    major, minor, patch = parse_version(latest_version)
    # Увеличиваем patch версию
    return f"{major}.{minor}.{patch + 1}"

def cmd_upload(args):
    """Загрузка и обработка нового файла"""
    validator = ContractValidator()
    version_mgr = VersionManager(base_dir=CONFIG.versions_dir)
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ Ошибка: Файл не найден: {file_path}")
        return 1
    
    filename = file_path.name
    
    # Валидация
    print(f"🔍 Валидация файла: {filename}")
    result = validator.validate_file(str(file_path))
    
    # Отчет о валидации
    if result.errors:
        print("\n❌ ОШИБКИ ВАЛИДАЦИИ:")
        for error in result.errors:
            print(f"   • {error}")
    
    if result.warnings:
        print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
        for warning in result.warnings:
            print(f"   • {warning}")
    
    if result.stats:
        print(f"\n📊 Статистика:")
        print(f"   Строк: {result.stats.get('total_rows', 0)}")
        print(f"   Колонок: {result.stats.get('total_columns', 0)}")
    
    if not result.is_valid:
        print("\n❌ Файл не прошел валидацию. Исправьте ошибки перед загрузкой.")
        return 1
    
    print("\n✅ Файл прошел валидацию!")
    
    # Определение версии
    if args.version:
        version = args.version
    else:
        latest = version_mgr.get_latest_version(filename)
        version = auto_increment_version(latest)
        print(f"📌 Автоматически назначена версия: {version}")
    
    # Сохранение версии
    description = args.description or f"Загрузка версии {version} от {datetime.now().strftime('%d.%m.%Y')}"
    
    validation_summary = {
        "is_valid": result.is_valid,
        "errors_count": len(result.errors),
        "warnings_count": len(result.warnings),
        "stats": result.stats
    }
    
    saved_path = version_mgr.save_new_version(
        source_file=str(file_path),
        filename=filename,
        version=version,
        change_description=description,
        validation_result=validation_summary
    )
    
    print(f"\n💾 Версия сохранена:")
    print(f"   Путь: {saved_path}")
    print(f"   Версия: {version}")
    print(f"   Описание: {description}")
    
    # Сравнение с предыдущей версией если есть
    previous_version = version_mgr.get_latest_version(filename)
    if previous_version and previous_version != version:
        print(f"\n🔄 Изменения относительно версии {previous_version}:")
        diff = version_mgr.get_version_diff(filename, previous_version, version)
        if "error" not in diff:
            if "added_count" in diff:
                print(f"   + Добавлено записей: {diff.get('added_count', 0)}")
                print(f"   - Удалено записей: {diff.get('removed_count', 0)}")
                print(f"   ~ Изменено записей: {diff.get('modified_count', 0)}")
                print(f"   = Без изменений: {diff.get('unchanged_count', 0)}")
            else:
                print(f"   Разница строк: {diff.get('difference', 0)}")
    
    return 0

def cmd_validate(args):
    """Только валидация файла"""
    validator = ContractValidator()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ Ошибка: Файл не найден: {file_path}")
        return 1
    
    print(f"🔍 Валидация файла: {file_path.name}")
    result = validator.validate_file(str(file_path))
    
    if result.errors:
        print("\n❌ ОШИБКИ:")
        for error in result.errors:
            print(f"   • {error}")
    
    if result.warnings:
        print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
        for warning in result.warnings:
            print(f"   • {warning}")
    
    if result.stats:
        print(f"\n📊 Статистика:")
        print(f"   Строк: {result.stats.get('total_rows', 0)}")
        print(f"   Колонок: {result.stats.get('total_columns', 0)}")
    
    if result.is_valid:
        print("\n✅ Файл корректен!")
        return 0
    else:
        print("\n❌ Файл содержит ошибки!")
        return 1

def cmd_history(args):
    """Показать историю версий файла"""
    version_mgr = VersionManager(base_dir=CONFIG.versions_dir)
    
    versions = version_mgr.get_all_versions(args.filename)
    
    if not versions:
        print(f"📁 История для файла '{args.filename}' не найдена")
        return 0
    
    print(f"📜 История версий файла: {args.filename}")
    print("=" * 60)
    
    for v in versions:
        status = "✅" if v.get('validation', {}).get('is_valid', False) else "❌"
        print(f"\n{status} Версия: {v['version']}")
        print(f"   Дата: {v['timestamp']}")
        print(f"   Описание: {v['change_description']}")
        print(f"   Файл: {v['file_path']}")
    
    return 0

def cmd_diff(args):
    """Сравнение двух версий"""
    version_mgr = VersionManager(base_dir=CONFIG.versions_dir)
    
    diff = version_mgr.get_version_diff(args.filename, args.version1, args.version2)
    
    if "error" in diff:
        print(f"❌ Ошибка: {diff['error']}")
        return 1
    
    print(f"🔄 Сравнение версий {args.version1} и {args.version2} файла {args.filename}")
    print("=" * 60)
    
    if "added_count" in diff:
        print(f"\n+ Добавлено записей: {diff['added_count']}")
        if diff.get('added_ids'):
            print(f"  ID: {', '.join(diff['added_ids'])}")
        
        print(f"- Удалено записей: {diff['removed_count']}")
        if diff.get('removed_ids'):
            print(f"  ID: {', '.join(diff['removed_ids'])}")
        
        print(f"~ Изменено записей: {diff['modified_count']}")
        if diff.get('modified_ids'):
            print(f"  ID: {', '.join(diff['modified_ids'])}")
        
        print(f"= Без изменений: {diff['unchanged_count']}")
    else:
        print(f"Строк в старой версии: {diff.get('old_rows', 0)}")
        print(f"Строк в новой версии: {diff.get('new_rows', 0)}")
        print(f"Разница: {diff.get('difference', 0)}")
    
    return 0

def cmd_report(args):
    """Генерация отчета по всем версиям"""
    version_mgr = VersionManager(base_dir=CONFIG.versions_dir)
    
    report_path = version_mgr.export_history_report()
    print(f"📄 Отчет сгенерирован: {report_path}")
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Система управления контрактами с животными",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s upload contracts.xlsx --version 1.0.0 --description "Первая версия"
  %(prog)s validate contracts.xlsx
  %(prog)s history contracts.xlsx
  %(prog)s diff contracts.xlsx 1.0.0 1.0.1
  %(prog)s report
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Команда upload
    upload_parser = subparsers.add_parser('upload', help='Загрузить новый файл')
    upload_parser.add_argument('file', help='Путь к Excel файлу')
    upload_parser.add_argument('--version', '-v', help='Версия (например, 1.0.0)')
    upload_parser.add_argument('--description', '-d', help='Описание изменений')
    upload_parser.set_defaults(func=cmd_upload)
    
    # Команда validate
    validate_parser = subparsers.add_parser('validate', help='Валидировать файл')
    validate_parser.add_argument('file', help='Путь к Excel файлу')
    validate_parser.set_defaults(func=cmd_validate)
    
    # Команда history
    history_parser = subparsers.add_parser('history', help='История версий')
    history_parser.add_argument('filename', help='Имя файла')
    history_parser.set_defaults(func=cmd_history)
    
    # Команда diff
    diff_parser = subparsers.add_parser('diff', help='Сравнить версии')
    diff_parser.add_argument('filename', help='Имя файла')
    diff_parser.add_argument('version1', help='Старая версия')
    diff_parser.add_argument('version2', help='Новая версия')
    diff_parser.set_defaults(func=cmd_diff)
    
    # Команда report
    report_parser = subparsers.add_parser('report', help='Отчет по всем версиям')
    report_parser.set_defaults(func=cmd_report)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())
