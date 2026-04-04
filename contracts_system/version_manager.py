"""
Менеджер версий файлов контрактов.
Отвечает за сохранение, нумерацию версий и историю изменений.
"""

import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

class VersionManager:
    def __init__(self, base_dir: str = "versions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.base_dir / "version_history.json"
        self._load_history()

    def _load_history(self):
        """Загрузка истории версий"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = {"files": {}}

    def _save_history(self):
        """Сохранение истории версий"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def get_latest_version(self, filename: str) -> Optional[str]:
        """Получение последней версии файла"""
        if filename in self.history["files"]:
            versions = self.history["files"][filename]["versions"]
            if versions:
                return versions[-1]["version"]
        return None

    def get_all_versions(self, filename: str) -> List[Dict]:
        """Получение всех версий файла"""
        if filename in self.history["files"]:
            return self.history["files"][filename]["versions"]
        return []

    def save_new_version(self, source_file: str, filename: str, 
                        version: str, change_description: str,
                        validation_result: Dict = None) -> str:
        """
        Сохранение новой версии файла.
        Возвращает путь к сохраненному файлу.
        """
        # Создание директории для конкретного файла
        file_dir = self.base_dir / filename
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # Формирование имени файла с версией
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_filename = f"{filename}.{version}_{timestamp}.xlsx"
        dest_path = file_dir / version_filename
        
        # Копирование файла
        shutil.copy2(source_file, dest_path)
        
        # Обновление истории
        if filename not in self.history["files"]:
            self.history["files"][filename] = {
                "created_at": datetime.now().isoformat(),
                "versions": []
            }
        
        version_entry = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "file_path": str(dest_path),
            "change_description": change_description,
            "validation": validation_result
        }
        
        self.history["files"][filename]["versions"].append(version_entry)
        self.history["files"][filename]["last_updated"] = datetime.now().isoformat()
        self._save_history()
        
        return str(dest_path)

    def get_version_diff(self, filename: str, version_old: str, version_new: str) -> Dict:
        """Сравнение двух версий"""
        versions = self.get_all_versions(filename)
        
        old_file = None
        new_file = None
        
        for v in versions:
            if v["version"] == version_old:
                old_file = v["file_path"]
            if v["version"] == version_new:
                new_file = v["file_path"]
        
        if not old_file or not new_file:
            return {"error": "Одна или обе версии не найдены"}
        
        # Сравнение данных
        try:
            df_old = pd.read_excel(old_file, engine='openpyxl')
            df_new = pd.read_excel(new_file, engine='openpyxl')
            
            # Простое сравнение по contract_id если есть
            if 'contract_id' in df_old.columns and 'contract_id' in df_new.columns:
                old_ids = set(df_old['contract_id'].astype(str))
                new_ids = set(df_new['contract_id'].astype(str))
                
                added = new_ids - old_ids
                removed = old_ids - new_ids
                common = old_ids & new_ids
                
                # Для общих записей можно проверить изменения
                modified = []
                if common:
                    df_old_indexed = df_old.set_index('contract_id')
                    df_new_indexed = df_new.set_index('contract_id')
                    
                    for cid in common:
                        if cid in df_old_indexed.index and cid in df_new_indexed.index:
                            # Упрощенное сравнение (можно улучшить)
                            row_old = df_old_indexed.loc[cid].to_dict()
                            row_new = df_new_indexed.loc[cid].to_dict()
                            if row_old != row_new:
                                modified.append(cid)
                
                return {
                    "added_count": len(added),
                    "added_ids": list(added)[:10],  # Первые 10
                    "removed_count": len(removed),
                    "removed_ids": list(removed)[:10],
                    "modified_count": len(modified),
                    "modified_ids": modified[:10],
                    "unchanged_count": len(common) - len(modified)
                }
            else:
                return {
                    "old_rows": len(df_old),
                    "new_rows": len(df_new),
                    "difference": len(df_new) - len(df_old)
                }
                
        except Exception as e:
            return {"error": f"Ошибка сравнения: {str(e)}"}

    def export_history_report(self, output_file: str = "reports/version_history_report.txt"):
        """Экспорт отчета по истории версий"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ ПО ИСТОРИИ ВЕРСИЙ КОНТРАКТОВ\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
            
            for filename, data in self.history["files"].items():
                f.write(f"Файл: {filename}\n")
                f.write(f"Создан: {data['created_at']}\n")
                f.write(f"Обновлен: {data.get('last_updated', 'Н/Д')}\n")
                f.write(f"Всего версий: {len(data['versions'])}\n")
                f.write("-" * 30 + "\n")
                
                for v in data["versions"]:
                    f.write(f"  Версия: {v['version']}\n")
                    f.write(f"  Дата: {v['timestamp']}\n")
                    f.write(f"  Описание: {v['change_description']}\n")
                    if v.get('validation'):
                        status = "✓ Валиден" if v['validation'].get('is_valid', False) else "✗ Ошибки"
                        f.write(f"  Статус валидации: {status}\n")
                    f.write("\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
        
        return str(output_path)
