from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.directions import show_directions_menu
from handlers.weather import show_weather_menu
from handlers.favorites import show_favorites_menu
from handlers.equipment import show_equipment_menu
from user_data import get_user_profile
from utils.keyboards import get_main_keyboard, get_close_keyboard, get_premium_keyboard
from utils.analytics import track_user_action

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка главного меню"""
    track_user_action(update.effective_user.id, 'user_active')
    
    # Проверяем не ожидаем ли мы текстовый ввод для поиска
    if context.user_data.get('waiting_for_search_query'):
        from handlers.search_handler import process_quick_search
        await process_quick_search(update, context)
        return
    
    # Удаляем сообщение с командой (с обработкой ошибок)
    if update.message:
        try:
            await update.message.delete()
        except Exception as e:
            # Если сообщение уже удалено или недоступно - продолжаем работу
            print(f"Не удалось удалить сообщение: {e}")
    
    text = update.message.text
    
    if text == "🗺️  Найти маршрут" or text == "🗺️  Направления":
        await show_directions_menu(update, context)
    elif text == "🎒 Снаряжение":
        await show_equipment_menu(update, context)
    elif text == "🌤️  Погода":
        await show_weather_menu(update, context)
    elif text == "💎 PREMIUM":
        await show_premium_menu(update, context)
    elif text == "⭐ Избранное":
        await show_favorites_menu(update, context)
    elif text == "ℹ️ Помощь":
        await show_help_menu(update, context)
    elif text == "🏆 Мой прогресс":
        await show_progress_menu(update, context)
    else:
        await update.effective_chat.send_message("Используйте меню ниже для навигации", reply_markup=get_main_keyboard())

# ВСЁ ОСТАЛЬНОЕ ОСТАВЛЯЕМ БЕЗ ИЗМЕНЕНИЙ
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ главного меню (для кнопки '🏠 Главное меню')"""
    welcome_text = "Выберите действие в меню ниже"

    keyboard = [
        [InlineKeyboardButton("🗺️  Направления", callback_data="back_directions")],
        [InlineKeyboardButton("🎒 Снаряжение", callback_data="equipment_menu")],
        [InlineKeyboardButton("🌤️  Погода", callback_data="weather_menu")],
        [InlineKeyboardButton("🏆 Мой прогресс", callback_data="show_progress")],
        [InlineKeyboardButton("⭐ Избранное", callback_data="show_favorites")],
        [InlineKeyboardButton("💎 PREMIUM", callback_data="premium_info")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text, 
            parse_mode='Markdown', 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.effective_chat.send_message(
            welcome_text, 
            parse_mode='Markdown', 
            reply_markup=get_main_keyboard()
        )

async def show_progress_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ меню прогресса"""
    from handlers.progress_handler import show_progress
    await show_progress(update, context)

async def show_premium_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ меню Premium"""
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)
    
    if profile['premium']:
        text = f"""
💎 *ВЫ PREMIUM ПОЛЬЗОВАТЕЛЬ!*

Ваша подписка активна ещё *{profile['days_left']}* дней
Доступны все премиум функции:

• 🔮 Все места силы и секретные локации
• 🗺️  Оффлайн карты для навигации  
• 📥 Скачивание маршрутов
• 🎁 Приоритетная поддержка
• 🔍 Расширенный поиск

*Спасибо за доверие!* 🌟
"""
    else:
        text = """
💎 *PREMIUM ПОДПИСКА*

Откройте все возможности бота:

• 🔮 *Сокровища на карте* - 15+ секретных локаций
• 🗺️  *Оффлайн карты* - навигация без интернета
• 📥 *Скачивание маршрутов* - GPS треки в 1 клик
• 🎁 *Приоритетная поддержка* - ответы за 5 минут
• 🔍 *Расширенный поиск* - фильтры по 10+ параметрам

*Выберите период подписки:*
"""
    
    keyboard = get_premium_keyboard(profile['premium'])
    
    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
    else:
        await update.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)

async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ меню помощи"""
    help_text = """
*ПОМОЩЬ И ПОДДЕРЖКА*

[Контакты поддержки](https://t.me/farotravel)
────────────────
• Telegram: [@farotravel](https://t.me/farotravel)
• Email: support@faro.travel

[Частые вопросы](https://t.me/farotravel)
────────────────
• Как забронировать тур?
• Способы оплаты
• Аренда снаряжения
• Навигация в горах

*Экстренная помощь:*
• МЧС: 112
• Спасательная служба: 8 (391) 211-11-11
• Медицинская помощь: 103

*Мы всегда готовы помочь!*
"""
    
    if update.message:
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_close_keyboard())
    else:
        await update.callback_query.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_close_keyboard())
