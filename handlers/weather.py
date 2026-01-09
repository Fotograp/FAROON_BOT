from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from weather.weather_api import get_weather_for_route, format_weather_message

async def show_weather_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
*ПРОГНОЗ ПОГОДЫ*

Выберите регион для просмотра погоды:
    """
    
    keyboard = [
        [InlineKeyboardButton("🏔️  Саяны", callback_data="weather_sayany")],
        [InlineKeyboardButton("🏞️  Хакасия", callback_data="weather_khakassia")],
        [InlineKeyboardButton("📍 Шушенский район", callback_data="weather_shushensky")],
        [InlineKeyboardButton("⛰️  Ергаки", callback_data="weather_ergaki")],
        [InlineKeyboardButton("🌊 Красноярское Море", callback_data="weather_krasnoyarsk_sea")],
        [InlineKeyboardButton("❌ Закрыть", callback_data="close_message")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    region_map = {
        "weather_sayany": "sayany",
        "weather_khakassia": "khakassia", 
        "weather_shushensky": "shushensky",
        "weather_ergaki": "ergaki",
        "weather_krasnoyarsk_sea": "krasnoyarsk_sea"
    }
    
    region_key = query.data
    region_name = region_map.get(region_key)
    
    if region_name:
        # Используем наш новый модуль погоды с AWAIT
        weather_data = await get_weather_for_route(region_name)
        text = format_weather_message(weather_data, region_name)
        
        # ПОГОДА МЕНЮ
        keyboard = [[InlineKeyboardButton("⬅️  назад", callback_data="back_to_weather_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # ИСПРАВЛЕНИЕ: Обработка сообщений с фото
        try:
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except BadRequest:
            # Если сообщение с фото - отправляем новое сообщение
            await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
    elif region_key == "back_to_weather_menu":
        await show_weather_menu(update, context)
    elif region_key == "close_message":
        await query.delete_message()

async def show_route_weather(update: Update, context: ContextTypes.DEFAULT_TYPE, route_name: str):
    """Показать погоду для конкретного маршрута"""
    query = update.callback_query
    await query.answer()
    
    from utils.location_helpers import get_location
    loc = get_location(route_name)
    
    if not loc:
        await query.answer("❌ Данные маршрута не найдены", show_alert=True)
        return
    
    region_name = loc.get('region', 'sayany')
    weather_data = await get_weather_for_route(region_name)
    
    if not weather_data:
        text = f"❌ Не удалось получить погоду для региона: {region_name}\n\nПопробуйте позже."
    else:
        text = format_weather_message(weather_data, region_name)
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад к действиям", callback_data=f"actions_{route_name}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
