import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from cache.user_cache import user_cache
from utils.location_helpers import get_location
from utils.keyboards import get_close_keyboard

logger = logging.getLogger(__name__)

class FavoritesHandler:
    def __init__(self):
        self.logger = logger
    
    def get_user_favorites(self, user_id):
        """Получает список избранных маршрутов пользователя"""
        try:
            favorite_ids = user_cache.get_user_favorites(user_id)
            favorites = []
            
            for route_id in favorite_ids:
                route = get_location(route_id)
                if route:
                    favorites.append(route)
            
            self.logger.debug(f"✅ Загружено {len(favorites)} избранных маршрутов для пользователя {user_id}")
            return favorites
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения избранного для пользователя {user_id}: {e}")
            return []
    
    def add_to_favorites(self, user_id, route_id):
        """Добавляет маршрут в избранное"""
        try:
            success = user_cache.add_to_favorites(user_id, route_id)
            if success:
                self.logger.debug(f"✅ Маршрут {route_id} добавлен в избранное пользователя {user_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления в избранное: {e}")
            return False
    
    def remove_from_favorites(self, user_id, route_id):
        """Удаляет маршрут из избранного"""
        try:
            success = user_cache.remove_from_favorites(user_id, route_id)
            if success:
                self.logger.debug(f"✅ Маршрут {route_id} удален из избранного пользователя {user_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления из избранного: {e}")
            return False
    
    def is_favorite(self, user_id, route_id):
        """Проверяет, есть ли маршрут в избранном"""
        try:
            return user_cache.is_in_favorites(user_id, route_id)
        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки избранного: {e}")
            return False

async def show_favorites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню избранных маршрутов"""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    
    # Создаем экземпляр обработчика
    favorites_handler = FavoritesHandler()
    favorites = favorites_handler.get_user_favorites(user_id)
    
    if not favorites:
        text = """
*ИЗБРАННЫЕ МАРШРУТЫ*

*Список пуст*

[Как добавить в избранное](https://t.me/farotravel)
────────────────
1. Откройте карточку маршрута
2. Нажмите кнопку «Добавить в избранное»
3. Маршрут появится здесь

*Начните с просмотра маршрутов в разделе "Направления"*
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Закрыть", callback_data="close_message")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        text = f"*ИЗБРАННЫЕ МАРШруты*\n\n"
        text += f"*Найдено маршрутов: {len(favorites)}*\n\n"
        text += "*Выберите маршрут для просмотра:*"
        
        keyboard = []
        for route in favorites:
            keyboard.append([InlineKeyboardButton(route["name"], callback_data=f"route_{route['id']}")])
        
        keyboard.append([InlineKeyboardButton("❌ Закрыть", callback_data="close_message")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

# Глобальный экземпляр обработчика
favorites_handler = FavoritesHandler()
