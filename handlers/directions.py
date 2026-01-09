from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from utils.keyboards import (
    get_directions_keyboard, get_hiking_keyboard, get_borus_categories_keyboard,
    get_borus_peaks_keyboard, get_borus_lakes_waterfalls_keyboard, get_borus_easy_routes_keyboard,
    get_west_sayan_keyboard, get_east_sayan_keyboard, get_ergaki_keyboard,
    get_krasnoyarsk_categories_keyboard, get_water_keyboard, get_active_keyboard, get_resort_keyboard,
    get_water_beaches_keyboard, get_water_lakes_keyboard, get_water_fishing_keyboard,
    get_active_rafting_keyboard, get_active_climbing_keyboard,
    get_resort_glamping_keyboard, get_resort_guesthouses_keyboard,
    get_resort_bases_keyboard, get_resort_camping_keyboard,
    get_active_mtb_keyboard, get_active_freeride_keyboard,
    get_khakassia_hiking_keyboard
)

async def show_directions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🗺️ *Всё многообразие Сибири — в ваших руках.*\n\nВыберите, как вы хотите её увидеть и почувствовать:"
    
    # Создаем комбинированную клавиатуру с кнопкой Закрыть
    directions_keyboard = get_directions_keyboard()
    close_button = [[InlineKeyboardButton("❌ Закрыть", callback_data="close_message")]]
    
    # Объединяем клавиатуры (преобразуем tuple в list)
    combined_keyboard = list(directions_keyboard.inline_keyboard) + close_button
    reply_markup = InlineKeyboardMarkup(combined_keyboard)
    
    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_hiking_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message=False):
    query = update.callback_query
    await query.answer()
    
    text = "🥾 *Здесь начинаются настоящие приключения.*\n\nМаршруты, которые проверят вас на прочность и подарят виды, ради которых стоит жить:"
    
    # ИСПРАВЛЕНИЕ: используем чистую клавиатуру без добавления кнопки "Закрыть"
    reply_markup = get_hiking_keyboard()
    
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_water_recreation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "💧 *Места, где вода умеет успокаивать душу.*\n\nНайдите свой берег, чтобы остановить время:"
    
    reply_markup = get_water_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_active_recreation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "⚡ *Для тех, кому мало просто идти.*\n\nЗдесь стихия становится вашим попутчиком:"
    
    reply_markup = get_active_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_resort_bases_submenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "🏕️ *Каждому герою нужна точка восстановления.*\n\nНайдите место для ночлега, где о вас позаботятся:"
    
    reply_markup = get_resort_keyboard()
    
    # Проверяем, не пытаемся ли изменить на то же самое сообщение
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            # Игнорируем ошибку - сообщение уже показывает нужное меню
            pass
        else:
            # Другие ошибки прокидываем дальше
            raise

# Тропы для хайкинга - подкатегории
async def show_borus_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message= False):
    query = update.callback_query
    await query.answer()
    
    # 🔥 УДАЛЯЕМ ФОТО-СООБЩЕНИЕ ЕСЛИ ОНО ЕСТЬ
    try:
        if query.message.photo:
            try:
                await query.message.delete()
            except BadRequest:
                pass
    except:
        pass
    
    text = "*🏔️  БОРУС*\n\n*Выберите категорию маршрутов:*"
    
    # 👇 ЗАМЕНЯЕМ вызов функции:
    reply_markup = get_borus_categories_keyboard()

    if new_message:
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        try:
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            if "Message is not modified" in str(e):
                pass
            else:
                raise

async def show_west_sayan_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message=False):
    query = update.callback_query
    await query.answer()
    
    # 🔥 УДАЛЯЕМ ФОТО-СООБЩЕНИЕ ЕСЛИ ОНО ЕСТЬ
    try:
        if query.message.photo:
            await query.message.delete()
    except BadRequest:
        pass
    
    text = "*🔼 ЗАПАДНЫЙ САЯН*\n\nВыберите категорию:"
    reply_markup = get_west_sayan_keyboard()

    if new_message:
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        try:
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            if "Message is not modified" not in str(e):
                await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_east_sayan_routes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*ВОСТОЧНЫЙ САЯН*\n\n*Выберите маршрут:*"
    reply_markup = get_east_sayan_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_ergaki_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message=False):
    query = update.callback_query
    await query.answer()
    
    # 🔥 УДАЛЯЕМ ФОТО-СООБЩЕНИЕ ЕСЛИ ОНО ЕСТЬ
    try:
        if query.message.photo:
            await query.message.delete()
    except BadRequest:
        pass
    
    text = "*🗻 ПРИРОДНЫЙ ПАРК ЕРГАКИ*\n\nВыберите категорию:"
    reply_markup = get_ergaki_keyboard()

    if new_message:
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        try:
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            if "Message is not modified" not in str(e):
                await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_khakassia_hiking_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message=False):
    query = update.callback_query
    await query.answer()
    
    # 🔥 УДАЛЯЕМ ФОТО-СООБЩЕНИЕ ЕСЛИ ОНО ЕСТЬ
    try:
        if query.message.photo:
            await query.message.delete()
    except BadRequest:
        pass
    
    text = "*🌄 ХАКАСИЯ*\n\n*Выберите район для путешествия:*"
    reply_markup = get_khakassia_hiking_keyboard()

    if new_message:
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        try:
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            if "Message is not modified" not in str(e):
                await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_krasnoyarsk_hiking_routes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "*🏙️ КРАСНОЯРСК*\n\n*Выберите категорию маршрутов:*"
    
    reply_markup = get_krasnoyarsk_categories_keyboard()
    
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

# Отдых у воды - подкатегории
async def show_water_beaches_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*ПЛЯЖИ*\n\nВыберите пляж:"
    reply_markup = get_water_beaches_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_water_lakes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*ОЗЕРА*\n\nВыберите озеро:"
    reply_markup = get_water_lakes_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_water_fishing_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*РЫБАЛКА*\n\nВыберите место для рыбалки:"
    reply_markup = get_water_fishing_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

# АКТИВНЫЙ ОТДЫХ
async def show_active_rafting_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*СПЛАВ*\n\nВыберите маршрут сплава:"
    reply_markup = get_active_rafting_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_active_climbing_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*СКАЛОЛАЗАНИЕ*\n\nВыберите место для скалолазания:"
    reply_markup = get_active_climbing_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_active_mtb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*ВЕЛОМУРУЛЫ*\n\nВыберите маршрут:"
    reply_markup = get_active_mtb_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_active_freeride_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*ФРИРАЙД*\n\nВыберите направление:"
    reply_markup = get_active_freeride_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

# 🏍️ КВАДРОЦИКЛЫ
async def show_quad_regions(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message=False):
    query = update.callback_query
    text = "*🏍️ КВАДРОЦИКЛЫ*\n\nВыберите регион:"
    from utils.keyboards import get_quad_regions_keyboard
    keyboard = get_quad_regions_keyboard()
    
    if new_message or (query and query.message.photo):
        if query and query.message.photo:
            await query.message.delete()
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
    else:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)

async def show_ust_mana_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message=False):
    query = update.callback_query
    text = "*🏍️ УСТЬ МАНА*\n\nВыберите маршрут:"
    from utils.keyboards import get_ust_mana_routes_keyboard
    keyboard = get_ust_mana_routes_keyboard()
    
    if new_message or (query and query.message.photo):
        if query and query.message.photo:
            await query.message.delete()
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
    else:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)

# ПАРКИ И ОТЕЛИ
async def show_resort_glamping_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*ГЛЭМПИНГИ*\n\nВыберите глэмпинг:"
    reply_markup = get_resort_glamping_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_resort_guesthouses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*ГОСТЕВЫЕ ДОМА*\n\nВыберите гостевой дом:"
    reply_markup = get_resort_guesthouses_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_resort_bases_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*БАЗЫ ОТДЫХА*\n\nВыберите базу отдыха:"
    reply_markup = get_resort_bases_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def show_resort_camping_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "*КЕМПИНГИ*\n\nВыберите кемпинг:"
    reply_markup = get_resort_camping_keyboard()
    try:
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

# Удаляем старые заглушки
async def show_development_message(query, section_name):
    text = f"*{section_name.upper()}*\n\n*В разработке*\n\nСкоро здесь появится подробная информация!"
    keyboard = [
        [InlineKeyboardButton("⬅️  назад", callback_data="back_directions")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
