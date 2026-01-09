import os
import shutil
import json
from datetime import datetime
import logging
import threading
import time
import asyncio
from utils.notifications import notify_backup_issue

logger = logging.getLogger(__name__)

def create_backup():
    """Создание резервных копий JSON файлов"""
    try:
        backup_dir = "data/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Файлы для бэкапа
        files_to_backup = [
            "data/premium_users.json",
            "data/analytics.json", 
            "data/affiliate_config.json"
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backed_up_files = []
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                # Имя бэкап файла
                filename = os.path.basename(file_path)
                backup_path = os.path.join(backup_dir, f"{filename}_{timestamp}.backup")
                
                # Копируем файл
                shutil.copy2(file_path, backup_path)
                backed_up_files.append(filename)
                logger.info(f"✅ Бэкап создан: {backup_path}")
            else:
                logger.warning(f"⚠️ Файл не найден: {file_path}")
        
        # Очищаем старые бэкапы
        cleanup_old_backups()
        
        if backed_up_files:
            logger.info(f"✅ Успешно созданы бэкапы: {', '.join(backed_up_files)}")
            return True
        else:
            logger.warning("⚠️ Не создано ни одного бэкапа")
            return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания бэкапа: {e}")
        # УВЕДОМЛЕНИЕ О ПРОБЛЕМЕ С БЭКАПОМ
        asyncio.create_task(notify_backup_issue("create_backup", str(e)))
        return False

def cleanup_old_backups(max_backups=7):
    """Удаление старых бэкапов (оставляем последние max_backups для каждого типа файлов)"""
    try:
        backup_dir = "data/backups"
        if not os.path.exists(backup_dir):
            return
            
        # Группируем бэкапы по типу файла
        backup_files = {}
        for file in os.listdir(backup_dir):
            if file.endswith(".backup"):
                # Извлекаем тип файла (premium_users, analytics, etc)
                file_type = file.split('_')[0]
                file_path = os.path.join(backup_dir, file)
                if file_type not in backup_files:
                    backup_files[file_type] = []
                backup_files[file_type].append((file_path, os.path.getctime(file_path)))
        
        # Удаляем старые бэкапы для каждого типа
        deleted_count = 0
        for file_type, files in backup_files.items():
            files.sort(key=lambda x: x[1])  # Сортируем по дате
            while len(files) > max_backups:
                old_backup = files.pop(0)
                os.remove(old_backup[0])
                deleted_count += 1
                logger.info(f"🗑️ Удален старый бэкап: {old_backup[0]}")
        
        if deleted_count > 0:
            logger.info(f"🗑️ Удалено старых бэкапов: {deleted_count}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка очистки бэкапов: {e}")
        # УВЕДОМЛЕНИЕ О ПРОБЛЕМЕ С ОЧИСТКОЙ БЭКАПОВ
        asyncio.create_task(notify_backup_issue("cleanup_backups", str(e)))

def run_periodic_backup():
    """Запуск периодического бэкапа (раз в 24 часа)"""
    while True:
        time.sleep(86400)  # 24 часа в секундах
        logger.info("🔄 Запуск периодического бэкапа...")
        success = create_backup()
        if success:
            logger.info("✅ Периодический бэкап завершен успешно")
        else:
            logger.error("❌ Периодический бэкап завершен с ошибками")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_backup()
