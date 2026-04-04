#!/usr/bin/env python3
"""
Changelog Manager - Автоматизированное ведение changelog продукта

Этот скрипт позволяет:
1. Добавлять новые записи в changelog (вы предоставляете текст)
2. Генерировать финальный CHANGELOG.md для публикации пользователям
3. Вести историю изменений по версиям

Использование:
    python changelog_manager.py add <version> --message "Ваш текст изменения"
    python changelog_manager.py generate  # Генерирует финальный CHANGELOG.md
    python changelog_manager.py show      # Показать текущий changelog
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path


class ChangelogManager:
    def __init__(self, changelog_file="changelog.json", output_file="CHANGELOG.md"):
        self.changelog_file = Path(changelog_file)
        self.output_file = Path(output_file)
        self.data = self._load_changelog()

    def _load_changelog(self):
        """Загружает существующий changelog или создает новый"""
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "project": "arch-labs",
                "versions": []
            }

    def _save_changelog(self):
        """Сохраняет changelog в файл"""
        with open(self.changelog_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_entry(self, version, message, entry_type="added"):
        """
        Добавляет новую запись в changelog
        
        Args:
            version: Номер версии (например, "1.0.0", "2.1.3")
            message: Текст изменения (который вы предоставляете)
            entry_type: Тип изменения (added, changed, deprecated, removed, fixed, security)
        """
        # Проверяем, существует ли уже такая версия
        version_entry = None
        for v in self.data["versions"]:
            if v["version"] == version:
                version_entry = v
                break

        if not version_entry:
            # Создаем новую версию
            version_entry = {
                "version": version,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "changes": {
                    "added": [],
                    "changed": [],
                    "deprecated": [],
                    "removed": [],
                    "fixed": [],
                    "security": []
                }
            }
            self.data["versions"].insert(0, version_entry)

        # Добавляем запись в соответствующую категорию
        if entry_type not in version_entry["changes"]:
            version_entry["changes"][entry_type] = []
        
        version_entry["changes"][entry_type].append({
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        self._save_changelog()
        print(f"✓ Запись добавлена в версию {version}")
        return True

    def generate_markdown(self):
        """Генерирует файл CHANGELOG.md в формате Keep a Changelog"""
        md_content = [
            "# Changelog",
            "",
            "Все заметные изменения в проекте будут документироваться в этом файле.",
            "",
            "Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),",
            "и этот проект придерживается [Семантического Версионирования](https://semver.org/lang/ru/).",
            ""
        ]

        # Сортируем версии (новые сверху)
        sorted_versions = sorted(
            self.data["versions"],
            key=lambda x: [int(p) if p.isdigit() else p for p in x["version"].split(".")],
            reverse=True
        )

        for version_data in sorted_versions:
            version = version_data["version"]
            date = version_data["date"]
            changes = version_data["changes"]

            md_content.append(f"## [{version}] - {date}")
            md_content.append("")

            # Категории изменений на русском
            categories = {
                "added": "### Добавлено",
                "changed": "### Изменено",
                "deprecated": "### Устарело",
                "removed": "### Удалено",
                "fixed": "### Исправлено",
                "security": "### Безопасность"
            }

            has_changes = False
            for key, title in categories.items():
                if key in changes and changes[key]:
                    has_changes = True
                    md_content.append(title)
                    for change in changes[key]:
                        md_content.append(f"- {change['message']}")
                    md_content.append("")

            if not has_changes:
                md_content.append("*Нет значимых изменений*")
                md_content.append("")

            md_content.append(f"[{version}]: https://github.com/your-org/arch-labs/releases/tag/{version}")
            md_content.append("")

        # Записываем в файл
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))

        print(f"✓ CHANGELOG.md успешно сгенерирован")
        return True

    def show_changelog(self):
        """Отображает текущий changelog в консоли"""
        if not self.data["versions"]:
            print("Changelog пуст")
            return

        print(f"\n{'='*60}")
        print(f"Changelog проекта: {self.data.get('project', 'Unknown')}")
        print(f"{'='*60}\n")

        for version_data in self.data["versions"]:
            print(f"Версия {version_data['version']} от {version_data['date']}")
            print("-" * 40)
            
            for category, changes in version_data["changes"].items():
                if changes:
                    print(f"  {category.upper()}:")
                    for change in changes:
                        print(f"    • {change['message']}")
            print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    manager = ChangelogManager()
    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 4:
            print("Использование: python changelog_manager.py add <version> --message \"Текст\" [--type added|changed|fixed|...]")
            sys.exit(1)
        
        version = sys.argv[2]
        message = None
        entry_type = "added"
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--message" and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                entry_type = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        if not message:
            print("Ошибка: необходимо указать --message")
            sys.exit(1)
        
        manager.add_entry(version, message, entry_type)

    elif command == "generate":
        manager.generate_markdown()

    elif command == "show":
        manager.show_changelog()

    else:
        print(f"Неизвестная команда: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
