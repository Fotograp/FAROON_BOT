import logging
import sqlite3
#import psycopg2
#from psycopg2.extras import RealDictCursor
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_type = 'sqlite'  # Пока используем SQLite
        self.connection = None
        self.setup_database()
    
    def setup_database(self):
        """Настройка подключения к базе данных"""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(
                    DATABASE_CONFIG['sqlite']['path'],
                    check_same_thread=False
                )
                self.connection.row_factory = sqlite3.Row
                logger.info("✅ SQLite database connected")
                
           # elif self.db_type == 'postgresql':
           #     pg_config = DATABASE_CONFIG['postgresql']
           #     self.connection = psycopg2.connect(
           #         host=pg_config['host'],
           #         port=pg_config['port'],
           #         database=pg_config['database'],
           #         user=pg_config['user'],
           #         password=pg_config['password']
           #     )
           #     logger.info("✅ PostgreSQL database connected")
                
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
    
    def get_cursor(self):
        """Получение курсора"""
        return self.connection.cursor()
    
    def execute_query(self, query, params=None):
        """Выполнение запроса"""
        try:
            cursor = self.get_cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"❌ Query execution error: {e}")
            self.connection.rollback()
            raise
    
    def migrate_to_postgresql(self):
        """Миграция данных из SQLite в PostgreSQL"""
        if self.db_type != 'sqlite':
            logger.error("❌ Migration can only be done from SQLite")
            return False
        
        logger.info("🚀 Starting migration to PostgreSQL...")
        # Здесь будет логика миграции
        return True

# Глобальный экземпляр
db_manager = DatabaseManager()
