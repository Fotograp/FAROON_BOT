import logging
import threading
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PreCheckoutQueryHandler, ContextTypes
from config import BOT_TOKEN

# Импорт обработчиков
from handlers.start import start, account_command, support_command, rules_command, premium_command, profile_command, stats_command, metrics_command
from handlers.main_menu import handle_main_menu
from handlers.directions import show_directions_menu
from handlers.weather import show_weather_menu, handle_weather_callback
from handlers.favorites import show_favorites_menu
from handlers.equipment import show_equipment_menu
from handlers.button_router import button_handler  # ← ИЗМЕНЕНИЕ: новый роутер!
from handlers.payment_handler import handle_successful_payment
from handlers.search_handler import (
    start_search,
    quick_search_handler,
    process_quick_search,
    advanced_search_handler,
    filter_difficulty_handler,
    set_difficulty_filter,
    filter_duration_handler,
    set_duration_filter,
    filter_region_handler,
    set_region_filter,
    apply_filters_search,
    reset_filters_handler,
    popular_routes_handler,
    handle_pagination
)
from utils.backup_db import create_backup, cleanup_old_backups, run_periodic_backup
from utils.logging_config import setup_logging

# Настройка структурированного логирования
setup_logging()
logger = logging.getLogger(__name__)

def initialize_backup():
    """Инициализация системы бэкапов"""
    logger.info("🔄 Инициализация системы бэкапов...")
    create_backup()
    backup_thread = threading.Thread(target=run_periodic_backup, daemon=True)
    backup_thread.start()
    logger.info("✅ Система бэкапов запущена (раз в 24 часа)")

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка успешного платежа"""
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    user_id = update.effective_user.id
    
    parts = payload.split('_')
    if len(parts) >= 3 and parts[0] == 'premium':
        months = int(parts[2])
        
        if handle_successful_payment(user_id, payload):
            await update.message.reply_text(
                f"🎉 *Premium активирован на {months} месяцев!*\n\nТеперь вам доступны все премиум функции!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ *Ошибка активации Premium*\n\nОбратитесь в поддержку: @faro_support",
                parse_mode='Markdown'
            )

async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение платежа"""
    query = update.pre_checkout_query
    await query.answer(ok=True)

def main():
    initialize_backup()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("premium", premium_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("account", account_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("rule", rules_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("metrics", metrics_command))
    application.add_handler(CommandHandler("weather", show_weather_menu))
    
    # Обработчики кнопок погоды 
    application.add_handler(CallbackQueryHandler(handle_weather_callback, pattern="^weather_"))
    application.add_handler(CallbackQueryHandler(handle_weather_callback, pattern="^back_to_weather_menu"))
    
    # Обработчики поиска маршрутов
    application.add_handler(CallbackQueryHandler(start_search, pattern="^search_routes$"))
    application.add_handler(CallbackQueryHandler(quick_search_handler, pattern="^quick_search$"))
    application.add_handler(CallbackQueryHandler(advanced_search_handler, pattern="^advanced_search$"))
    application.add_handler(CallbackQueryHandler(filter_difficulty_handler, pattern="^filter_difficulty$"))
    application.add_handler(CallbackQueryHandler(set_difficulty_filter, pattern="^difficulty_"))
    application.add_handler(CallbackQueryHandler(filter_duration_handler, pattern="^filter_duration$"))
    application.add_handler(CallbackQueryHandler(set_duration_filter, pattern="^duration_"))
    application.add_handler(CallbackQueryHandler(filter_region_handler, pattern="^filter_region$"))
    application.add_handler(CallbackQueryHandler(set_region_filter, pattern="^region_"))
    application.add_handler(CallbackQueryHandler(apply_filters_search, pattern="^apply_filters$"))
    application.add_handler(CallbackQueryHandler(reset_filters_handler, pattern="^reset_filters$"))
    application.add_handler(CallbackQueryHandler(popular_routes_handler, pattern="^popular_routes$"))
    
    # Обработчик пагинации результатов поиска
    application.add_handler(CallbackQueryHandler(handle_pagination, pattern="^page_"))
    
    # Обработчики кнопок - ГЛАВНЫЙ РОУТЕР
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчики сообщений главного меню
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu))
    
    # Обработчики платежей
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
    logger.info("Бот FARO TRAVEL запущен")
    application.run_polling()

if __name__ == '__main__':
    main()
