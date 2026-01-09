import os
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Telegram Bot Token
BOT_TOKEN = "***"

# Payments Configuration
PROVIDER_TOKEN = "***"

# Цены в копейках (для РФ)
PREMIUM_PRICES = {
    1: 29900,   # 299 руб
    3: 69900,   # 699 руб  
    12: 199000  # 1990 руб
}

# Bot Configuration
ADMIN_IDS = [***]  # Твой ID

# Настройки кэширования
CACHE_TTL = 300  # 5 минут в секундах

# Настройки бэкапов
BACKUP_RETENTION_DAYS = 7  # Хранить бэкапы 7 дней

# Партнерские программы
AFFILIATE_CONFIG = {
    'tripster': {
        'base_url': 'https://www.tripster.ru',
        'affiliate_param': 'ref'
    },
    'ostrovok': {
        'base_url': 'https://ostrovok.ru',
        'affiliate_param': 'partner'
    },
    'aviasales': {
        'base_url': 'https://aviasales.ru',
        'affiliate_param': 'marker'
    }
}

# Настройки аналитики
ANALYTICS_CONFIG = {
    'track_views': True,
    'track_clicks': True,
    'track_conversions': True,
    'save_interval': 300  # Сохранять каждые 5 минут
}

# Яндекс.Карты API
YANDEX_MAPS_API_KEY = "***"

# Настройки оффлайн-карт
MAPS_CONFIG = {
    'tile_size': 256,  # размер тайла в пикселях
    'max_zoom': 16,    # максимальный зум
    'cache_size_mb': 500,  # максимальный размер кэша
    'yandex_base_url': 'https://static-maps.yandex.ru/v1'
}

# Database Configuration
DATABASE_CONFIG = {
    'sqlite': {
        'path': 'faro_travel.db',
        'enabled': True  # Пока используем SQLite
    },
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'faro_travel',
        'user': 'faro_user',
        'password': 'secure_password_123',
        'enabled': False  # Будем включать после миграции
    }
}

# Redis Configuration - ОБНОВЛЕНО
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'enabled': True,  # ВКЛЮЧАЕМ Redis
    'timeouts': {
        'connect': 5,    # 5 секунд на подключение
        'read': 3,       # 3 секунды на чтение
        'write': 3       # 3 секунды на запись
    }
}

# TTL настройки для разных типов данных
CACHE_TTL_CONFIG = {
    'user_premium': 300,      # 5 минут для premium статуса
    'route_data': 3600,       # 1 час для данных маршрутов
    'user_sessions': 1800,    # 30 минут для сессий
    'statistics': 600,        # 10 минут для статистики
    'weather': 1800           # 30 минут для погоды
}

# Migration Settings
MIGRATION_SETTINGS = {
    'batch_size': 1000,
    'backup_before_migration': True,
    'validate_after_migration': True
}

# Weather API - ДОБАВЛЕНО
WEATHER_API_KEY = "***"

# Проверка обязательных настроек
required_configs = ['BOT_TOKEN', 'PROVIDER_TOKEN', 'ADMIN_IDS', 'YANDEX_MAPS_API_KEY']
for config in required_configs:
    if not globals().get(config):
        raise ValueError(f"Обязательная настройка {config} не определена")

logger = logging.getLogger(__name__)
logger.info("Конфигурация бота загружена")
