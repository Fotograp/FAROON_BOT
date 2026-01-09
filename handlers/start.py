from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.keyboards import get_main_keyboard, get_directions_keyboard, get_close_keyboard
from utils.analytics import get_stats_summary
from utils.metrics import metrics
from user_data import get_user_profile

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
*FAROON | ПЛАНИРУЙ ИНАЧЕ*

*Я проведу тебя туда, где карты молчат*
────────────────────

*Открой Свой мир за пределами путеводителя:*

• Известные и малоизвестные локации
• Уютный отдых вдали от городской суеты  
• Исторические памятники и самобытные селения
• Маршруты разной категории сложности
────────────────────

*Здесь нет безликих точек — только места с душой, где хочется остаться*
────────────────────

*FAROON*
_Plan Different. Live Deeper_

Выбери категорию и начни Всё по-новому...
"""
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=get_main_keyboard())
    else:
        await update.callback_query.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=get_main_keyboard())

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    premium_text = """
*PREMIUM ДОСТУП FARO TRAVEL* 🗝️

Откройте все возможности планирования путешествий:

*✨ Что входит в PREMIUM:*
• Полный доступ ко всем категориям маршрутов
• Эксклюзивные локации и секретные тропы
• Оффлайн-карты для навигации без интернета
• Расширенные описания маршрутов
• Приоритетная поддержка

*💎 Тарифы:*
• 1 месяц - 299 ₽
• 3 месяца - 699 ₽ (экономия 200 ₽)
• 1 год - 1999 ₽ (экономия 1500 ₽)

*🚀 Как активировать:*
1. Выберите тариф ниже
2. Оплатите через безопасную систему
3. Получите мгновенный доступ ко всем функциям

*Готовы открыть всю Сибирь?*
"""

    keyboard = [
        [InlineKeyboardButton("💳 1 месяц - 299 ₽", callback_data="premium_1month")],
        [InlineKeyboardButton("💎 3 месяца - 699 ₽", callback_data="premium_3months")],
        [InlineKeyboardButton("🚀 1 год - 1999 ₽", callback_data="premium_1year")],
        [InlineKeyboardButton("❓ Частые вопросы", callback_data="premium_faq")],
        [InlineKeyboardButton("❌ Закрыть", callback_data="close_message")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(premium_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(premium_text, parse_mode='Markdown', reply_markup=reply_markup)

async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account_text = """
*ЛИЧНЫЙ КАБИНЕТ*

[Профиль пользователя](https://t.me/farotravel)
────────────────
• Статистика ваших походов
• Достижения и награды
• Баланс и оплата услуг

[История бронирований](https://t.me/farotravel)
────────────────
• Бронирование баз отдыха
• Заказ экскурсий
• История поездок

*В разработке:*
• Система лояльности
• Персональные рекомендации
• Планировщик маршрутов

*Скоро будут доступны новые функции!*
    """
    
    await update.message.reply_text(
        account_text,
        parse_mode='Markdown',
        reply_markup=get_close_keyboard()
    )

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = """
*ПОМОЩЬ И ПОДДЕРЖКА*

[Контакты поддержки](https://t.me/farotravel)
────────────────
• Telegram: [@farotravel](https://t.me/farotravel)
• Email: support@faro.travel
• Сайт: [faro.travel](https://faro.travel)

[Частые вопросы](https://t.me/farotravel)
────────────────
• Как забронировать тур?
• Способы оплаты
• Аренда снаряжения
• Навигация в горах

[Техническая поддержка](https://t.me/farotravel)
────────────────
• Проблемы с приложением
• Сообщить об ошибке
• Предложения по улучшению

*Экстренная помощь:*
• МЧС: 112
• Спасательная служба: 8 (391) 211-11-11
• Медицинская помощь: 103

*Мы всегда готовы помочь!*
    """
    
    await update.message.reply_text(
        support_text,
        parse_mode='Markdown',
        reply_markup=get_close_keyboard()
    )

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = """
*ПРАВИЛА СЕРВИСА FARO TRAVEL*

[Общие положения](https://t.me/farotravel)
────────────────
• Сервис предназначен для планирования туристических маршрутов
• Мы предоставляем информационную поддержку
• Все маршруты проходят проверку на безопасность

[Обязанности пользователей](https://t.me/farotravel)
────────────────
• Соблюдать правила нахождения в природных парках
• Не оставлять мусор на маршрутах
• Соблюдать правила пожарной безопасности
• Иметь при себе средства связи и навигации

[Бронирование и оплата](https://t.me/farotravel)
────────────────
• Оплата услуг происходит через безопасные платежные системы
• Возврат средств осуществляется согласно условиям договора
• Бронирование подтверждается после полной оплаты

[Безопасность](https://t.me/farotravel)
────────────────
• Сервис не несет ответственности за действия пользователей
• Рекомендуем использовать проверенное снаряжение
• Обязательно сообщайте о своих маршрутах спасательным службам

[Конфиденциальность](https://t.me/farotravel)
────────────────
• Мы защищаем ваши персональные данные
• Используем данные только для улучшения сервиса
• Не передаем информацию третьим лицам

*Соблюдайте правила и наслаждайтесь путешествиями!*
    """
    
    await update.message.reply_text(
        rules_text,
        parse_mode='Markdown',
        reply_markup=get_close_keyboard()
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    profile = get_user_profile(user.id)
    
    if profile['premium']:
        text = f"""*ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ* 🗝️

👤 *{user.first_name}*
💎 *Статус:* PREMIUM
📅 *Подписка до:* {profile['expire_date'].strftime('%d.%m.%Y')}
⏳ *Осталось дней:* {profile['days_left']}

*Доступ ко всем функциям:*
• Все категории маршрутов
• Секретные локации  
• Оффлайн-карты
• Расширенные описания"""
    else:
        text = f"""*ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ*

👤 *{user.first_name}*  
💎 *Статус:* Базовый
🚫 *Доступно:* Только "Тропы хайкинга"

*Откройте PREMIUM для доступа к:*
• Всем категориям маршрутов
• Секретным локациям
• Оффлайн-картам
• Расширенным описаниям

💳 *Получить PREMIUM:* /premium"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != 5941272698:
        await update.message.reply_text("❌ Эта команда только для администратора")
        return
    
    stats = get_stats_summary()
    
    text = f"""
📊 СТАТИСТИКА БОТА

👥 Пользователи:
• Всего пользователей: {stats['total_users']}
• Активных сегодня: {stats['active_today']}
• Premium пользователей: {stats['premium_users']}

💎 Premium:
• Всего конверсий: {stats['premium_conversions']}

🔗 Партнерские ссылки:
• Всего кликов: {stats['affiliate_clicks']}

⭐ Избранное:
• Добавлений в избранное: {stats['favorites_added']}

🗺️ Популярные маршруты:
"""
    
    for route, views in stats['popular_routes']:
        text += f"• {route}: {views} просмотров\n"
    
    await update.message.reply_text(text)

async def metrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ метрик производительности для админа"""
    user_id = update.effective_user.id
    
    if user_id != 5941272698:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    report = metrics.get_performance_report()
    
    if not report:
        await update.message.reply_text("📊 Метрики пока не собраны")
        return
    
    message = "📊 *Метрики производительности*\n\n"
    for metric_name, stats in report.items():
        message += f"*{metric_name}:*\n"
        message += f"• Вызовов: {stats['count']}\n"
        message += f"• Среднее: {stats['avg']:.3f}с\n"
        message += f"• Максимум: {stats['max']:.3f}с\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')
