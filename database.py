from data_manager.db_manager import db_manager
import logging
from datetime import datetime
from cache.user_cache import user_cache
from cache.route_cache import route_cache
from utils.cache_decorators import cache_user_data

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db = db_manager
        self.init_db()
        logger.info("✅ База данных инициализирована с поддержкой Redis кэширования")
    
    def init_db(self):
        """Инициализация базы данных и таблиц"""
        # Таблица пользователей
        self.db.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                subscription_type TEXT DEFAULT 'free',
                subscription_end_date DATETIME,
                stripe_customer_id TEXT,
                purchased_at DATETIME,
                months INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица платежей
        self.db.execute_query('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stripe_payment_intent_id TEXT,
                amount INTEGER,
                currency TEXT DEFAULT 'rub',
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица прогресса пользователей
        self.db.execute_query('''
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id INTEGER PRIMARY KEY,
                completed_routes INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица достижений
        self.db.execute_query('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER,
                achievement_id TEXT,
                earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id)
            )
        ''')
        
        # Таблица пройденных маршрутов
        self.db.execute_query('''
            CREATE TABLE IF NOT EXISTS completed_routes (
                user_id INTEGER,
                route_name TEXT,
                completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, route_name)
            )
        ''')
    
    # ===== USER PROGRESS with CACHING =====
    
    @cache_user_data(ttl=1800)  # Кэшируем прогресс на 30 минут
    def get_user_progress(self, user_id):
        """Получение прогресса пользователя с кэшированием"""
        query = 'SELECT * FROM user_progress WHERE user_id = ?'
        result = self.db.execute_query(query, (user_id,))
        
        if not result:
            # Создаем запись если пользователя нет
            insert_query = 'INSERT INTO user_progress (user_id) VALUES (?)'
            self.db.execute_query(insert_query, (user_id,))
            return {
                'user_id': user_id,
                'completed_routes': 0,
                'total_points': 0, 
                'current_level': 1
            }
        
        return dict(result[0])
    
    def update_user_progress(self, user_id, completed_routes=None, points=None):
        """Обновление прогресса пользователя с инвалидацией кэша"""
        progress = self.get_user_progress(user_id)
        
        if completed_routes is not None:
            progress['completed_routes'] += completed_routes
        
        if points is not None:
            progress['total_points'] += points
        
        # Расчет уровня (каждые 100 очков = 1 уровень)
        progress['current_level'] = max(1, progress['total_points'] // 100 + 1)
        
        query = '''
            INSERT OR REPLACE INTO user_progress 
            (user_id, completed_routes, total_points, current_level) 
            VALUES (?, ?, ?, ?)
        '''
        self.db.execute_query(query, (
            user_id, progress['completed_routes'], 
            progress['total_points'], progress['current_level']
        ))
        
        # Инвалидируем кэш прогресса
        user_cache.delete_user_session(user_id)
        
        return progress

    # ===== ACHIEVEMENTS with CACHING =====
    
    @cache_user_data(ttl=3600)  # Кэшируем достижения на 1 час
    def get_user_achievements(self, user_id):
        """Получение достижений пользователя с кэшированием"""
        query = 'SELECT achievement_id FROM user_achievements WHERE user_id = ?'
        result = self.db.execute_query(query, (user_id,))
        return [row[0] for row in result]
    
    def add_achievement(self, user_id, achievement_id):
        """Добавление достижения пользователю с инвалидацией кэша"""
        try:
            query = '''
                INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) 
                VALUES (?, ?)
            '''
            self.db.execute_query(query, (user_id, achievement_id))
            
            # Инвалидируем кэш достижений
            user_cache.delete_user_session(user_id)
            
            return True
        except Exception as e:
            logger.error(f"Error adding achievement: {e}")
            return False
    
    # ===== COMPLETED ROUTES with CACHING =====
    
    @cache_user_data(ttl=1800)  # Кэшируем пройденные маршруты на 30 минут
    def get_completed_routes(self, user_id):
        """Получение списка пройденных маршрутов с кэшированием"""
        query = 'SELECT route_name FROM completed_routes WHERE user_id = ?'
        result = self.db.execute_query(query, (user_id,))
        return [row[0] for row in result]

    def add_completed_route(self, user_id, route_name):
        """Добавление маршрута в пройденные с инвалидацией кэша"""
        try:
            query = '''
                INSERT OR IGNORE INTO completed_routes (user_id, route_name) 
                VALUES (?, ?)
            '''
            self.db.execute_query(query, (user_id, route_name))
            
            # Инвалидируем кэш пройденных маршрутов
            user_cache.delete_user_session(user_id)
            
            return True
        except Exception as e:
            logger.error(f"Error adding completed route: {e}")
            return False

    def is_route_completed(self, user_id, route_name):
        """Проверка пройден ли маршрут с использованием кэша"""
        try:
            # Пробуем получить из кэша пройденных маршрутов
            completed_routes = self.get_completed_routes(user_id)
            return route_name in completed_routes
        except Exception as e:
            logger.error(f"Error checking completed route: {e}")
            # Фолбэк на прямой запрос если кэш не работает
            query = '''
                SELECT 1 FROM completed_routes 
                WHERE user_id = ? AND route_name = ?
            '''
            result = self.db.execute_query(query, (user_id, route_name))
            return len(result) > 0

    # ===== PREMIUM SUBSCRIPTION with CACHING =====
    
    def get_user_premium_status(self, user_id):
        """Получение premium статуса пользователя с кэшированием"""
        # Сначала пробуем получить из кэша
        cached_status = user_cache.get_user_premium_status(user_id)
        if cached_status is not None:
            return cached_status
        
        # Если нет в кэше, проверяем в базе
        query = '''
            SELECT subscription_type, subscription_end_date 
            FROM users WHERE user_id = ?
        '''
        result = self.db.execute_query(query, (user_id,))
        
        if result and len(result) > 0:
            subscription_type = result[0][0]
            subscription_end = result[0][1]
            
            is_premium = self._check_premium_status(subscription_type, subscription_end)
            
            # Сохраняем в кэш
            user_cache.set_user_premium_status(user_id, is_premium)
            
            return is_premium
        
        return False
    
    def _check_premium_status(self, subscription_type, subscription_end):
        """Проверяет актуальность premium подписки"""
        if subscription_type != 'premium':
            return False
            
        if not subscription_end:
            return False
            
        try:
            end_date = datetime.strptime(subscription_end, '%Y-%m-%d %H:%M:%S')
            return end_date > datetime.now()
        except:
            return False
    
    def update_user_subscription(self, user_id, subscription_type, subscription_end_date):
        """Обновление подписки пользователя с инвалидацией кэша"""
        try:
            query = '''
                INSERT OR REPLACE INTO users 
                (user_id, subscription_type, subscription_end_date) 
                VALUES (?, ?, ?)
            '''
            self.db.execute_query(query, (user_id, subscription_type, subscription_end_date))
            
            # Обновляем кэш premium статуса
            is_premium = self._check_premium_status(subscription_type, subscription_end_date)
            user_cache.set_user_premium_status(user_id, is_premium)
            
            logger.info(f"✅ Подписка пользователя {user_id} обновлена: {subscription_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления подписки пользователя {user_id}: {e}")
            return False

# Сохраняем обратную совместимость
db = Database()
