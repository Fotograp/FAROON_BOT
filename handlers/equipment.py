from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from data.equipment import get_equipment_checklist, get_shops_by_city

async def show_equipment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню снаряжения"""
    text = """
СИСТЕМА ПОДБОРА СНАРЯЖЕНИЯ

Выберите раздел:
• Чек-листы - готовые списки для разных активностей
• Магазины - где купить снаряжение в Красноярске и онлайн
• Для маршрута - автоматический подбор для вашего похода
• PREMIUM - эксклюзивные скидки у партнеров
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Чек-листы по типам", callback_data="equipment_checklists")],
        [InlineKeyboardButton("🛒 Магазины снаряжения", callback_data="equipment_shops")],
        [InlineKeyboardButton("💎 Premium-скидки", callback_data="equipment_premium")],
        [InlineKeyboardButton("❌ Закрыть", callback_data="close_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_equipment_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню типов активностей для чек-листов"""
    text = """
ВЫБЕРИТЕ ТИП АКТИВНОСТИ

Получите готовый чек-лист снаряжения:
"""
    
    keyboard = [
        [InlineKeyboardButton("🏔️  Горный треккинг", callback_data="equip_type_mountain")],
        [InlineKeyboardButton("🥾 Однодневный хайкинг", callback_data="equip_type_hiking")],
        [InlineKeyboardButton("🧗 Скалолазание", callback_data="equip_type_climbing")],
        [InlineKeyboardButton("🌊 Водный туризм", callback_data="equip_type_water")],
        [InlineKeyboardButton("❄️  Зимние маршруты", callback_data="equip_type_winter")],
        [InlineKeyboardButton("🏕️  Кемпинг и палатки", callback_data="equip_type_camping")],
        [InlineKeyboardButton("⬅️  назад", callback_data="equipment_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_equipment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback'ов снаряжения"""
    query = update.callback_query
    callback_data = query.data
    
    if callback_data == "equipment_main":
        await show_equipment_menu(update, context)
    elif callback_data == "equipment_checklists":
        await show_equipment_types(update, context)
    elif callback_data.startswith("equip_type_"):
        await show_equipment_checklist(update, context)
    elif callback_data == "equipment_shops":
        await show_shops_menu(update, context)
    elif callback_data == "close_menu":
        await query.delete_message()
    else:
        await query.answer("Функция в разработке", show_alert=True)

async def show_equipment_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать чек-лист для выбранного типа"""
    query = update.callback_query
    equipment_type = query.data.replace("equip_type_", "")
    
    checklist = get_equipment_checklist(equipment_type)
    
    if not checklist:
        await query.answer("Чек-лист временно недоступен", show_alert=True)
        return
    
    text = f"""
{checklist['title']}

{checklist['description']}

────────────────
ОБЯЗАТЕЛЬНОЕ СНАРЯЖЕНИЕ:
{chr(10).join(['• ' + item for item in checklist['required']])}

────────────────
РЕКОМЕНДУЕМОЕ:
{chr(10).join(['• ' + item for item in checklist['recommended']])}

────────────────
{checklist['tips']}
"""
    
    keyboard = [
        [InlineKeyboardButton("⬅️  назад", callback_data="equipment_checklists")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_shops_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора магазинов"""
    text = """
🛒 МАГАЗИНЫ СНАРЯЖЕНИЯ

Выберите город для поиска магазинов:
"""
    
    keyboard = [
        [InlineKeyboardButton("🏙️  Красноярск", callback_data="shops_city_krasnoyarsk")],
        [InlineKeyboardButton("🏙️  Абакан", callback_data="shops_city_abakan")],
        [InlineKeyboardButton("⬅️  назад к снаряжению", callback_data="equipment_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def show_krasnoyarsk_shop_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    text = """
*АЛЬПИНДУСТРИЯ* 
*Профессиональное горное снаряжение*

*Адрес:* ул. Взлётная, 24, Красноярск
*Часы работы:* 10:00-20:00
*Телефон:* +7 (391) 234-56-78

────────────────
*Специализация:*
• Горное и альпинистское снаряжение
• Треккинговая одежда и обувь  
• Профессиональная экипировка
• Консультация экспертов
"""
    
    keyboard = [
        [InlineKeyboardButton("🗺️  на карте", url="https://yandex.ru/maps/?text=Красноярск+ул.Взлётная+24")],
        [InlineKeyboardButton("🛒 на сайт", url="https://alpindustria.ru")],
        [InlineKeyboardButton("➡️  следующий", callback_data="krasnoyarsk_shop_2")],
        [InlineKeyboardButton("⬅️  назад", callback_data="equipment_shops")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_krasnoyarsk_shop_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    text = """
*ПОКРОВ*
*Туристическое снаряжение и кемпинг*

*Адрес:* ул. Новосибирская, 35, цокольный этаж
*Часы работы:* 09:00-21:00  
*Телефон:* +7 (391) 345-67-89

────────────────
*Специализация:*
• Туристическое снаряжение
• Кемпинговая мебель
• Рюкзаки и палатки
• Аксессуары для отдыха
"""
    
    keyboard = [
        [InlineKeyboardButton("🗺️  на карте", url="https://yandex.ru/maps/?text=Красноярск+ул.Новосибирская+35")],
        [InlineKeyboardButton("🛒 на сайт", url="https://pokrov.ru")],
        [InlineKeyboardButton("➡️  следующий", callback_data="krasnoyarsk_shop_3")],
        [InlineKeyboardButton("⬅️  назад", callback_data="equipment_shops")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_krasnoyarsk_shop_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    text = """
*АМАТИС*
*Одежда и обувь для outdoor*

*Адрес:* ул. Диксона, 2, Покровка
*Часы работы:* 10:00-20:00
*Телефон:* +7 (391) 456-78-90

────────────────
*Специализация:*
• Одежда для outdoor
• Обувь для треккинга  
• Термобелье и аксессуары
• Сезонные коллекции
"""
    
    keyboard = [
        [InlineKeyboardButton("🗺️  на карте", url="https://yandex.ru/maps/?text=Красноярск+ул.Диксона+2")],
        [InlineKeyboardButton("🛒 на сайт", url="https://amatis24.ru")],
        [InlineKeyboardButton("🏙️  Абакан", callback_data="shops_city_abakan")],
        [InlineKeyboardButton("⬅️  назад к снаряжению", callback_data="equipment_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_abakan_shop_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Первая карточка магазина Абакана"""
    query = update.callback_query
    
    text = """
*ТРИАЛ-СПОРТ*
*Велосипедное и туристическое снаряжение*

*Адрес:* ул. Маршала Жукова, 22, Абакан
*Часы работы:* 09:00-20:00
*Телефон:* +7 (390) 212-34-56

────────────────
*Специализация:*
• Велосипедное снаряжение
• Туристическое оборудование
• Спортивная экипировка
• Запчасти и аксессуары
"""
    
    keyboard = [
        [InlineKeyboardButton("🗺️  на карте", url="https://yandex.ru/maps/?text=Абакан+ул.Маршала+Жукова+22")],
        [InlineKeyboardButton("🛒 на сайт", url="https://trial-sport.ru")],
        [InlineKeyboardButton("➡️  следующий", callback_data="abakan_shop_2")],
        [InlineKeyboardButton("⬅️  назад", callback_data="equipment_shops")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_abakan_shop_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вторая карточка магазина Абакана"""
    query = update.callback_query
    
    text = """
*СПОРТМАСТЕР*
*Спортивная одежда и обувь*

*Адрес:* ТЦ "Калина", ул. Некрасова, 31а, Абакан
*Часы работы:* 10:00-22:00
*Телефон:* +7 (800) 777-88-99

────────────────
*Специализация:*
• Спортивная одежда и обувь
• Фитнес-оборудование
• Туристические товары
• Сезонные распродажи
"""
    
    keyboard = [
        [InlineKeyboardButton("🗺️  на карте", url="https://yandex.ru/maps/?text=Абакан+ул.Некрасова+31а")],
        [InlineKeyboardButton("🛒 на сайт", url="https://sportmaster.ru")],
        [InlineKeyboardButton("➡️  следующий", callback_data="abakan_shop_3")],
        [InlineKeyboardButton("⬅️  назад", callback_data="equipment_shops")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_abakan_shop_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Третья карточка магазина Абакана"""
    query = update.callback_query
    
    text = """
*БРОДЯГА*
*Туристическое снаряжение*

*Адрес:* пр. Дружбы народов, 41, Абакан
*Часы работы:* 10:00-19:00
*Телефон:* +7 (390) 223-45-67

────────────────
*Специализация:*
• Туристическое снаряжение
• Рюкзаки и палатки
• Оборудование для кемпинга
• Снаряжение для рыбалки
"""
    
    keyboard = [
        [InlineKeyboardButton("🗺️  на карте", url="https://yandex.ru/maps/?text=Абакан+пр.Дружбы+народов+41")],
        [InlineKeyboardButton("🛒 на сайт", url="https://бродяга24.рф")],
        [InlineKeyboardButton("🏙️  Красноярск", callback_data="shops_city_krasnoyarsk")],
        [InlineKeyboardButton("⬅️  назад к снаряжению", callback_data="equipment_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_shop_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Детальная карточка магазина с действиями"""
    query = update.callback_query
    shop_type = query.data.replace("shop_", "")
    
    shops = {
        # Красноярск
        "alpindustria": {
            "name": "АЛЬПИНДУСТРИЯ",
            "rating": "★★★★★ 4.8",
            "address": "ул. Взлётная, 24, Красноярск",
            "phone": "+7 (391) 234-56-78",
            "hours": "10:00-20:00",
            "specialization": "Горное снаряжение, альпинистское оборудование, треккинговая одежда",
            "discount": "Бесплатная консультация по подбору",
            "description": "Профессиональный магазин горного снаряжения с экспертной консультацией",
            "map_url": "https://yandex.ru/maps/?text=Красноярск+ул.Взлётная+24",
            "website": "https://alpindustria.ru"
        },
        "pokrov": {
            "name": "ПОКРОВ", 
            "rating": "★★★★☆ 4.6",
            "address": "ул. Новосибирская, 35, цокольный этаж, Красноярск",
            "phone": "+7 (391) 345-67-89",
            "hours": "09:00-21:00",
            "specialization": "Туристическое снаряжение, кемпинговая мебель, рюкзаки и палатки",
            "discount": "Система накопительных скидок",
            "description": "Магазин туристического снаряжения с широким ассортиментом для отдыха на природе",
            "map_url": "https://yandex.ru/maps/?text=Красноярск+ул.Новосибирская+35",
            "website": "https://pokrov.ru"
        },
        "amatis": {
            "name": "АМАТИС",
            "rating": "★★★★☆ 4.7",
            "address": "ул. Диксона, 2, Покровка, Красноярск",
            "phone": "+7 (391) 456-78-90", 
            "hours": "10:00-20:00",
            "specialization": "Одежда для outdoor, обувь для треккинга, термобелье",
            "discount": "Примерка и тестирование",
            "description": "Специализированный магазин outdoor одежды и обуви",
            "map_url": "https://yandex.ru/maps/?text=Красноярск+ул.Диксона+2",
            "website": "https://amatis24.ru"
        },
        # Абакан
        "trial": {
            "name": "ТРИАЛ-СПОРТ",
            "rating": "★★★★★ 4.7",
            "address": "ул. Маршала Жукова, 22, Абакан",
            "phone": "+7 (390) 212-34-56",
            "hours": "09:00-20:00",
            "specialization": "Велосипедное снаряжение, туристическое оборудование, спортивная экипировка",
            "discount": "Широкий ассортимент для активного отдыха",
            "description": "Магазин спортивного снаряжения и оборудования для активного образа жизни",
            "map_url": "https://yandex.ru/maps/?text=Абакан+ул.Маршала+Жукова+22",
            "website": "https://trial-sport.ru"
        },
        "sportmaster": {
            "name": "СПОРТМАСТЕР",
            "rating": "★★★★☆ 4.5", 
            "address": "ТЦ 'Калина', ул. Некрасова, 31а, Абакан",
            "phone": "+7 (800) 777-88-99",
            "hours": "10:00-22:00",
            "specialization": "Спортивная одежда и обувь, фитнес-оборудование, туристические товары",
            "discount": "Постоянные акции и скидки",
            "description": "Крупнейшая сеть спортивных магазинов с широким ассортиментом",
            "map_url": "https://yandex.ru/maps/?text=Абакан+ул.Некрасова+31а",
            "website": "https://sportmaster.ru"
        },
        "brodyaga": {
            "name": "БРОДЯГА",
            "rating": "★★★★☆ 4.6",
            "address": "пр. Дружбы народов, 41, Абакан", 
            "phone": "+7 (390) 223-45-67",
            "hours": "10:00-19:00",
            "specialization": "Туристическое снаряжение, рюкзаки и палатки, оборудование для кемпинга",
            "discount": "Специализация на туризме и отдыхе",
            "description": "Специализированный магазин туристического снаряжения и оборудования",
            "map_url": "https://yandex.ru/maps/?text=Абакан+пр.Дружбы+народов+41",
            "website": "https://бродяга24.рф"
        }
    }
    
    shop = shops.get(shop_type)
    if not shop:
        await query.answer("Магазин не найден", show_alert=True)
        return
    
    text = f"""
{shop['name']}
{shop['rating']}

{shop['description']}

Адрес: {shop['address']}
Телефон: {shop['phone']}
Часы работы: {shop['hours']}

Специализация: {shop['specialization']}

Преимущества: {shop['discount']}
"""
    
    keyboard = []
    
    # Кнопки действий
    action_buttons = []
    # Для всех магазинов добавляем карту (они все имеют физические адреса)
    action_buttons.append(InlineKeyboardButton("🗺️  Адрес на карте", url=shop['map_url']))
    
    if action_buttons:
        keyboard.append(action_buttons)
    
    keyboard.append([InlineKeyboardButton("🛒 Перейти в магазин", url=shop['website'])])
    
    # Кнопки возврата
    if shop_type in ["alpindustria", "pokrov", "amatis"]:
        keyboard.append([InlineKeyboardButton("⬅️  назад", callback_data="shops_city_krasnoyarsk")])
    else:
        keyboard.append([InlineKeyboardButton("⬅️  назад", callback_data="shops_city_abakan")])
    
    keyboard.append([InlineKeyboardButton("⬅️  назад к снаряжению", callback_data="equipment_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)
