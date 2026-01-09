"""
🔍 СИСТЕМА ПОИСКА МАРШРУТОВ
Умный поиск с фильтрами по сложности, длительности, высоте и регионам
Адаптировано для telegram-bot-api
"""

import logging
from typing import List, Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext

from utils.location_helpers import get_all_routes
from utils.search_keyboards import (
    create_search_keyboard,
    create_filters_keyboard,
    create_difficulty_keyboard,
    create_duration_keyboard,
    create_region_keyboard,
    create_search_results_keyboard,
    get_altitude_filter_keyboard
)

# 🔍 ДОБАВЛЯЕМ ИМПОРТ ВАЛИДАТОРОВ ПОИСКА
from utils.search_validators import validate_search_query, sanitize_search_query, analyze_query_complexity

# 🔍 НЕЧЕТКИЙ ПОИСК - ДОБАВЛЯЕМ ПОСЛЕ СУЩЕСТВУЮЩИХ ИМПОРТОВ
try:
    from rapidfuzz import process
    FUZZY_AVAILABLE = True
    logging.info("Нечеткий поиск (RapidFuzz) активирован")
except ImportError:
    FUZZY_AVAILABLE = False
    logging.warning("RapidFuzz не установлен. Нечеткий поиск недоступен.")

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы пагинации
RESULTS_PER_PAGE = 5

# Глобальные переменные для хранения фильтров
user_search_filters = {}

# 🔍 НОВАЯ ФУНКЦИЯ: НЕЧЕТКИЙ ПОИСК
def fuzzy_search_routes(query: str, routes: list, threshold: int = 50) -> List[Dict]:
    """
    🔍 НЕЧЕТКИЙ ПОИСК С УЧЕТОМ ОПЕЧАТОК
    Возвращает маршруты, отсортированные по релевантности
    """
    if not FUZZY_AVAILABLE:
        logger.warning("Нечеткий поиск недоступен. Возвращаем оригинальные маршруты.")
        return routes
    
    if not query or len(query) < 2:
        return routes
    
    try:
        logger.info(f"Запускаем нечеткий поиск: '{query}'")
        
        # Создаем список текстов для поиска
        search_texts = []
        for route in routes:
            search_text = f"{route.get('name', '')} {route.get('description', '')}"
            search_texts.append(search_text.lower())
        
        # Выполняем нечеткий поиск
        matches = process.extract(query.lower(), search_texts, limit=len(routes))
        
        # Собираем результаты с оценкой релевантности
        matched_routes = []
        for match_text, score, match_index in matches:
            if score >= threshold:
                route = routes[match_index].copy()  # Создаем копию чтобы не менять оригинал
                route['match_score'] = score
                matched_routes.append(route)
        
        # Сортируем по убыванию релевантности
        matched_routes.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        logger.info(f"Нечеткий поиск завершен: найдено {len(matched_routes)} маршрутов")
        return matched_routes
        
    except Exception as e:
        logger.error(f"Ошибка в нечетком поиске: {e}")
        return routes

# 🔍 ОБНОВЛЕННАЯ ФУНКЦИЯ ПОИСКА
def search_routes(query: str = "", filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    🔍 ОСНОВНАЯ ФУНКЦИЯ ПОИСКА МАРШРУТОВ
    Теперь с поддержкой нечеткого поиска
    """
    if filters is None:
        filters = {}
    
    try:
        # Получаем все маршруты через единый интерфейс
        all_routes = get_all_routes()
        results = []
        
        # 🔍 УЛУЧШЕННЫЙ ПОИСК: ТОЧНЫЙ + НЕЧЕТКИЙ
        if query and len(query) >= 2:
            # 1. Сначала ищем точные совпадения
            exact_matches = []
            for route in all_routes:
                search_text = f"{route.get('name', '').lower()} {route.get('description', '').lower()}"
                if query.lower() in search_text:
                    route_copy = route.copy()
                    route_copy['match_score'] = 100  # Максимальная оценка для точных совпадений
                    exact_matches.append(route_copy)
            
            # 2. НЕЧЕТКИЙ ПОИСК ВРЕМЕННО ОТКЛЮЧЕН
            # if len(exact_matches) < 5 and FUZZY_AVAILABLE:
            #     remaining_routes = [r for r in all_routes if r not in [rm for rm in exact_matches]]
            #     fuzzy_matches = fuzzy_search_routes(query, remaining_routes, threshold=50)
            #     results = exact_matches + fuzzy_matches
            # else:
            results = exact_matches
                
            logger.info(f"Текстовый поиск: '{query}', точных совпадений: {len(exact_matches)}")
        else:
            # Без текстового запроса - все маршруты
            results = [route.copy() for route in all_routes]
        
        # 🎛️ ПРИМЕНЯЕМ ФИЛЬТРЫ К РЕЗУЛЬТАТАМ ПОИСКА
        filtered_results = []
        for route in results:
            if apply_filters(route, filters):
                filtered_results.append(route)
        
        # 🧹 УБИРАЕМ ВРЕМЕННОЕ ПОЛЕ match_score ПЕРЕД ВОЗВРАТОМ
        for route in filtered_results:
            route.pop('match_score', None)
        
        logger.info(f"Поиск завершен: '{query}', фильтры: {filters}, найдено: {len(filtered_results)}")
        return filtered_results
        
    except Exception as e:
        logger.error(f"Ошибка в search_routes: {e}")
        return []

# 🔍 ВСЕ ОСТАЛЬНЫЕ ФУНКЦИИ ПОЛНОСТЬЮ СОХРАНЯЕМ:
async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск системы поиска - главное меню поиска"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_search_filters[user_id] = {}

        # 🔧 ОЧИСТКА СОСТОЯНИЙ ПОИСКА
        context.user_data.pop('waiting_for_search_query', None)
        context.user_data.pop('search_results', None) 
        context.user_data.pop('search_query', None)
        context.user_data.pop('search_filters', None)
        
        search_keyboard = create_search_keyboard()
        
        await query.edit_message_text(
            "🔍 <b>ПОИСК МАРШРУТОВ</b>\n\n"
            "Выберите тип поиска:\n\n"
            "• <b>Быстрый поиск</b> - по названию или описанию\n"
            "• <b>Расширенный поиск</b> - с фильтрами\n"
            "• <b>Популярные маршруты</b> - топовые направления",
            reply_markup=search_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в start_search: {e}")
        await update.callback_query.answer("❌ Ошибка при запуске поиска", show_alert=True)

async def quick_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрый поиск по названию"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Сохраняем состояние для текстового ввода
        context.user_data['waiting_for_search_query'] = True
        
        await query.edit_message_text(
            "🔍 <b>БЫСТРЫЙ ПОИСК</b>\n\n"
            "Введите название маршрута или ключевые слова:\n\n"
            "<i>Примеры:</i>\n"
            "• <code>Борус</code>\n"
            "• <code>озеро</code>\n"
            "• <code>водопад</code>\n"
            "• <code>легкий маршрут</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="search_routes")]]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в quick_search_handler: {e}")
        await update.callback_query.answer("❌ Ошибка при поиске", show_alert=True)

async def process_quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстового запроса для быстрого поиска"""
    try:
        # 🔧 ПРОВЕРКА ОТМЕНЫ ПОИСКА
        if update.message.text.strip().lower() in ['отмена', 'cancel', 'назад']:
            context.user_data.pop('waiting_for_search_query', None)
            await start_search(update, context)
            return
            
        if not context.user_data.get('waiting_for_search_query'):
            return

        search_query = update.message.text.strip()
        
        # 🔍 ВАЛИДАЦИЯ ЗАПРОСА
        validation_result = validate_search_query(search_query)
        
        if not validation_result["valid"]:
            await update.message.reply_text(
                f"❌ <b>Некорректный запрос</b>\n\n"
                f"{validation_result['error']}\n\n"
                f"<i>Примеры правильных запросов:</i>\n"
                f"• <code>Борус</code>\n"
                f"• <code>озеро горных духов</code>\n"
                f"• <code>легкий маршрут</code>",
                parse_mode="HTML"
            )
            return
        
        # Используем очищенный запрос
        cleaned_query = validation_result["cleaned_query"]
        
        # Анализируем сложность запроса для логирования
        complexity_info = analyze_query_complexity(cleaned_query)
        logger.info(f"Поисковый запрос: '{cleaned_query}', сложность: {complexity_info['complexity']}")
        
        await update.message.reply_text(f"🔍 <b>Ищем:</b> <code>{cleaned_query}</code>", parse_mode="HTML")
        
        # Выполняем поиск с очищенным запросом
        results = search_routes(query=cleaned_query)
        
        if results:
            await show_search_results(update, context, results, search_query=cleaned_query)
        else:
            # 🔍 ПРЕДЛАГАЕМ АЛЬТЕРНАТИВЫ ПРИ НУЛЕВЫХ РЕЗУЛЬТАТАХ
            alternative_suggestions = get_alternative_suggestions(cleaned_query)
            
            response_text = (
                f"😔 <b>Ничего не найдено</b>\n\n"
                f"По запросу '<code>{cleaned_query}</code>' маршрутов не найдено.\n\n"
            )
            
            if alternative_suggestions:
                response_text += f"<b>Возможно, вы искали:</b>\n{alternative_suggestions}\n\n"
            
            response_text += (
                "Попробуйте:\n"
                "• Изменить запрос\n"
                "• Использовать расширенный поиск\n" 
                "• Посмотреть популярные маршруты"
            )
            
            await update.message.reply_text(
                response_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 Новый поиск", callback_data="quick_search")],
                    [InlineKeyboardButton("🎛️ Расширенный поиск", callback_data="advanced_search")],
                    [InlineKeyboardButton("⭐ Популярные маршруты", callback_data="popular_routes")],
                    [InlineKeyboardButton("◀️ Назад к поиску", callback_data="search_routes")]
                ]),
                parse_mode="HTML"
            )
        
        # Сбрасываем состояние
        context.user_data.pop('waiting_for_search_query', None)
        
    except Exception as e:
        logger.error(f"Ошибка в process_quick_search: {e}")
        await update.message.reply_text("❌ Произошла ошибка при поиске. Попробуйте еще раз.")

async def advanced_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расширенный поиск с фильтрами"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in user_search_filters:
            user_search_filters[user_id] = {}
        
        filters = user_search_filters[user_id]
        filters_text = get_filters_text(filters)
        
        filters_keyboard = create_filters_keyboard()
        
        await query.edit_message_text(
            f"🎛️ <b>РАСШИРЕННЫЙ ПОИСК</b>\n\n"
            f"{filters_text}\n"
            "Выберите фильтры для поиска:",
            reply_markup=filters_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в advanced_search_handler: {e}")
        await update.callback_query.answer("❌ Ошибка при расширенном поиске", show_alert=True)

async def filter_difficulty_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фильтр по сложности"""
    try:
        query = update.callback_query
        await query.answer()
        
        difficulty_keyboard = create_difficulty_keyboard()
        
        await query.edit_message_text(
            "🏔️ <b>ФИЛЬТР ПО СЛОЖНОСТИ</b>\n\n"
            "Выберите уровень сложности маршрута:",
            reply_markup=difficulty_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в filter_difficulty_handler: {e}")
        await update.callback_query.answer("❌ Ошибка при выборе сложности", show_alert=True)

async def set_difficulty_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка фильтра сложности"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        difficulty_map = {
            "difficulty_easy": "легкий",
            "difficulty_medium": "средний", 
            "difficulty_hard": "сложный",
            "difficulty_expert": "эксперт"
        }
        
        difficulty = difficulty_map.get(query.data, "")
        if difficulty:
            user_search_filters[user_id]['difficulty'] = difficulty
            await query.answer(f"✅ Сложность: {difficulty}")
        else:
            await query.answer("❌ Ошибка выбора сложности")
        
        # Возвращаемся к фильтрам
        await advanced_search_handler(update, context)
        
    except Exception as e:
        logger.error(f"Ошибка в set_difficulty_filter: {e}")
        await update.callback_query.answer("❌ Ошибка при установке фильтра", show_alert=True)

async def filter_duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фильтр по длительности"""
    try:
        query = update.callback_query
        await query.answer()
        
        duration_keyboard = create_duration_keyboard()
        
        await query.edit_message_text(
            "⏱️ <b>ФИЛЬТР ПО ДЛИТЕЛЬНОСТИ</b>\n\n"
            "Выберите продолжительность маршрута:",
            reply_markup=duration_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в filter_duration_handler: {e}")
        await update.callback_query.answer("❌ Ошибка при выборе длительности", show_alert=True)

async def set_duration_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка фильтра длительности"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        duration_map = {
            "duration_2": (0, 2),
            "duration_4": (2, 4),
            "duration_8": (4, 8),
            "duration_more": (8, 24)
        }
        
        duration_range = duration_map.get(query.data, (0, 24))
        user_search_filters[user_id]['min_duration'] = duration_range[0]
        user_search_filters[user_id]['max_duration'] = duration_range[1]
        
        await query.answer(f"✅ Длительность: {duration_range[0]}-{duration_range[1]}ч")
        
        # Возвращаемся к фильтрам
        await advanced_search_handler(update, context)
        
    except Exception as e:
        logger.error(f"Ошибка в set_duration_filter: {e}")
        await update.callback_query.answer("❌ Ошибка при установке фильтра", show_alert=True)

async def filter_region_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фильтр по региону"""
    try:
        query = update.callback_query
        await query.answer()
        
        region_keyboard = create_region_keyboard()
        
        await query.edit_message_text(
            "🗺️ <b>ФИЛЬТР ПО РЕГИОНУ</b>\n\n"
            "Выберите географический регион:",
            reply_markup=region_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в filter_region_handler: {e}")
        await update.callback_query.answer("❌ Ошибка при выборе региона", show_alert=True)

async def set_region_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка фильтра региона"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        region_map = {
            "region_sayany": "Саяны",
            "region_khakassia": "Хакасия",
            "region_shushensky": "Шушенский район",
            "region_ergaki": "Ергаки", 
            "region_krasnoyarsk_sea": "Красноярское Море"
        }
        
        region = region_map.get(query.data, "")
        if region:
            user_search_filters[user_id]['region'] = region
            await query.answer(f"✅ Регион: {region}")
        else:
            await query.answer("❌ Ошибка выбора региона")
        
        # Возвращаемся к фильтрам
        await advanced_search_handler(update, context)
        
    except Exception as e:
        logger.error(f"Ошибка в set_region_filter: {e}")
        await update.callback_query.answer("❌ Ошибка при установке фильтра", show_alert=True)

async def altitude_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фильтра по высоте"""
    try:
        query = update.callback_query
        await query.answer()
        
        text = "📏 *ФИЛЬТР ПО ВЫСОТЕ*\n\nВыберите диапазон высоты над уровнем моря:"
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_altitude_filter_keyboard())
        
    except Exception as e:
        logger.error(f"Ошибка в altitude_filter_handler: {e}")
        await query.answer("❌ Ошибка при загрузке фильтра высоты", show_alert=True)

async def set_altitude_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка фильтра высоты"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Обработка сброса фильтра высоты
        if query.data == "altitude_reset":
            user_search_filters[user_id].pop('min_altitude', None)
            user_search_filters[user_id].pop('max_altitude', None)
            await query.answer("✅ Фильтр высоты сброшен")
        
        # Обработка выбора диапазона высоты
        elif query.data.startswith("altitude_"):
            altitude_map = {
                "altitude_0_1000": (0, 1000),
                "altitude_1000_2000": (1000, 2000),
                "altitude_2000_3000": (2000, 3000),
                "altitude_3000_9999": (3000, 9999)
            }
            
            altitude_range = altitude_map.get(query.data, (0, 9999))
            user_search_filters[user_id]['min_altitude'] = altitude_range[0]
            user_search_filters[user_id]['max_altitude'] = altitude_range[1]
            
            await query.answer(f"✅ Высота: {altitude_range[0]}-{altitude_range[1]}м")
        
        # Возвращаемся к фильтрам
        await advanced_search_handler(update, context)
        
    except Exception as e:
        logger.error(f"Ошибка в set_altitude_filter: {e}")
        await update.callback_query.answer("❌ Ошибка при установке фильтра высоты", show_alert=True)

async def apply_filters_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Применение фильтров и выполнение поиска"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        filters = user_search_filters.get(user_id, {})
        
        await query.edit_message_text(
            f"🔍 <b>ИЩЕМ МАРШРУТЫ...</b>\n\n"
            f"Применяем фильтры...",
            parse_mode="HTML"
        )
        
        # Выполняем поиск с фильтрами (теперь с улучшенным алгоритмом)
        results = search_routes(filters=filters)
        
        if results:
            await show_search_results(update, context, results, filters=filters)
        else:
            filters_text = get_filters_text(filters)
            await query.edit_message_text(
                "😔 <b>Ничего не найдено</b>\n\n"
                f"По выбранным фильтрам маршрутов не найдено.\n\n"
                f"{filters_text}\n"
                "Попробуйте:\n"
                "• Изменить фильтры\n"  
                "• Использовать быстрый поиск\n"
                "• Посмотреть популярные маршруты",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎛️ Изменить фильтры", callback_data="advanced_search")],
                    [InlineKeyboardButton("🔍 Быстрый поиск", callback_data="quick_search")],
                    [InlineKeyboardButton("⭐ Популярные маршруты", callback_data="popular_routes")],
                    [InlineKeyboardButton("◀️ Назад к поиску", callback_data="search_routes")]
                ]),
                parse_mode="HTML"
            )
        
    except Exception as e:
        logger.error(f"Ошибка в apply_filters_search: {e}")
        await update.callback_query.edit_message_text(
            "❌ <b>Ошибка при поиске</b>\n\n"
            "Попробуйте еще раз или измените фильтры.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎛️ К фильтрам", callback_data="advanced_search")],
                [InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]
            ]),
            parse_mode="HTML"
        )

async def reset_filters_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс всех фильтров"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_search_filters[user_id] = {}
        
        await query.answer("✅ Фильтры сброшены")
        await advanced_search_handler(update, context)
        
    except Exception as e:
        logger.error(f"Ошибка в reset_filters_handler: {e}")
        await update.callback_query.answer("❌ Ошибка при сбросе фильтров", show_alert=True)

async def popular_routes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Популярные маршруты (топ по рейтингу или посещаемости)"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Получаем все маршруты через единый интерфейс
        all_routes = get_all_routes()
        
        # Временно: просто показываем первые 10 маршрутов
        popular_results = all_routes[:10]
        
        await query.edit_message_text(
            "⭐ <b>ПОПУЛЯРНЫЕ МАРШРУТЫ</b>\n\n"
            "Самые посещаемые и интересные маршруты:",
            parse_mode="HTML"
        )
        
        await show_search_results(update, context, popular_results, "популярные")
        
    except Exception as e:
        logger.error(f"Ошибка в popular_routes_handler: {e}")
        await update.callback_query.answer("❌ Ошибка при загрузке популярных маршрутов", show_alert=True)

def get_alternative_suggestions(query: str) -> str:
    """
    💡 ПРЕДЛОЖЕНИЕ АЛЬТЕРНАТИВНЫХ ВАРИАНТОВ ПОИСКА
    """
    query_lower = query.lower()
    suggestions = []
    
    # Простые подсказки на основе популярных запросов
    popular_alternatives = {
        "борус": ["Пик Борус", "Малый Борус", "Озеро Банзай"],
        "ергаки": ["Зуб Дракона", "Висячий Камень", "Озеро Горных Духов"],
        "озеро": ["Маранкуль", "Озеро Горных Духов", "Ивановские озера"],
        "водопад": ["Долина Водопадов", "Кинзелюкский водопад"],
        "хакасия": ["Сундуки", "Туимский провал", "Ивановские озера"],
        "саяны": ["Пик Араданский", "Мунку-Сардык", "Агульское озеро"]
    }
    
    # Ищем подходящие альтернативы
    for key, alternatives in popular_alternatives.items():
        if key in query_lower:
            suggestions.extend(alternatives)
    
    # Убираем дубликаты и ограничиваем количество
    unique_suggestions = list(dict.fromkeys(suggestions))[:3]
    
    if unique_suggestions:
        return "\n".join([f"• {suggestion}" for suggestion in unique_suggestions])
    
    return ""

async def show_search_results(update: Update, context: ContextTypes.DEFAULT_TYPE, results: List[Dict], search_query: str = "", filters: Dict = None, page: int = 0):
    """
    📊 ПОКАЗ РЕЗУЛЬТАТОВ ПОИСКА С ПАГИНАЦИЕЙ
    """
    try:
        if not results:
            return
        
        # Сохраняем результаты в context для навигации
        context.user_data['search_results'] = results
        context.user_data['search_query'] = search_query
        context.user_data['search_filters'] = filters
        
        # Вычисляем пагинацию
        total_results = len(results)
        total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        current_page = min(page, total_pages - 1) if total_pages > 0 else 0
        
        # Получаем результаты для текущей страницы
        start_idx = current_page * RESULTS_PER_PAGE
        end_idx = start_idx + RESULTS_PER_PAGE
        page_results = results[start_idx:end_idx]
        
        # Формируем сообщение с результатами
        results_text = f"🎯 <b>НАЙДЕНО МАРШРУТОВ:</b> {total_results}\n"
        
        if search_query:
            results_text += f"🔍 <b>Запрос:</b> <code>{search_query}</code>\n"
        elif filters:
            results_text += f"🎛️ <b>Применены фильтры</b>\n"
        
        results_text += f"📄 <b>Страница:</b> {current_page + 1}/{total_pages}\n\n"
        
        # Показываем результаты текущей страницы
        for i, route in enumerate(page_results, start_idx + 1):
            results_text += format_route_preview(route, i)
        
        # Создаем клавиатуру с пагинацией
        results_keyboard = create_search_results_keyboard(total_results, current_page, total_pages)
        
        # ИСПРАВЛЕНИЕ: Проверяем откуда пришел запрос
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(
                results_text,
                reply_markup=results_keyboard,
                parse_mode="HTML"
            )
        else:
            # Если пришло текстовое сообщение, отправляем новое сообщение
            await update.message.reply_text(
                results_text,
                reply_markup=results_keyboard,
                parse_mode="HTML"
            )
        
    except Exception as e:
        logger.error(f"Ошибка в show_search_results: {e}")
        # ИСПРАВЛЕНИЕ: Отправляем ошибку в зависимости от типа update
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text("❌ Ошибка при показе результатов")
        else:
            await update.message.reply_text("❌ Ошибка при показе результатов")

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка навигации по страницам результатов"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Получаем данные из callback_data
        if query.data.startswith("page_"):
            page_num = int(query.data.replace("page_", ""))
            
            # Получаем сохраненные результаты поиска
            results = context.user_data.get('search_results', [])
            search_query = context.user_data.get('search_query', "")
            filters = context.user_data.get('search_filters', {})
            
            if results:
                await show_search_results(update, context, results, search_query, filters, page_num)
            else:
                await query.answer("❌ Результаты поиска устарели", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка в handle_pagination: {e}")
        await query.answer("❌ Ошибка при навигации", show_alert=True)

def apply_filters(route: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """
    🎛️ ПРИМЕНЕНИЕ ФИЛЬТРОВ К МАРШРУТУ
    """
    try:
        # Фильтр сложности
        if filters.get('difficulty'):
            if route.get('difficulty') != filters['difficulty']:
                return False
        
        # Фильтр длительности (в часах)
        if filters.get('min_duration') or filters.get('max_duration'):
            duration = route.get('duration_hours', 0)
            min_dur = filters.get('min_duration', 0)
            max_dur = filters.get('max_duration', float('inf'))
            
            if not (min_dur <= duration <= max_dur):
                return False
        
        # Фильтр высоты
        if filters.get('min_altitude') or filters.get('max_altitude'):
            altitude = route.get('max_altitude', 0)
            min_alt = filters.get('min_altitude', 0)
            max_alt = filters.get('max_altitude', float('inf'))
            
            if not (min_alt <= altitude <= max_alt):
                return False
        
        # Фильтр региона
        if filters.get('region'):
            if route.get('region') != filters['region']:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в apply_filters: {e}")
        return False

def format_route_preview(route: Dict[str, Any], index: int) -> str:
    """Форматирование preview маршрута"""
    name = route.get('name', 'Без названия')
    difficulty = route.get('difficulty', 'не указана')
    duration = route.get('duration_hours', 0)
    altitude = route.get('max_altitude', 0)
    
    # Эмодзи для сложности
    difficulty_emoji = {
        'легкий': '🟢',
        'средний': '🟡', 
        'сложный': '🔴',
        'эксперт': '⚫'
    }.get(difficulty, '⚪')
    
    return (
        f"{index}. {difficulty_emoji} <b>{name}</b>\n"
        f"   📊 Сложность: {difficulty}\n"
        f"   ⏱️ Длительность: {duration}ч\n"
        f"   📏 Высота: {altitude}м\n\n"
    )

def get_filters_text(filters: Dict[str, Any]) -> str:
    """Текст текущих активных фильтров"""
    if not filters:
        return "📋 <b>Фильтры:</b> не установлены\n"
    
    filters_text = "📋 <b>Установленные фильтры:</b>\n"
    
    if filters.get('difficulty'):
        filters_text += f"• 🏔️ Сложность: {filters['difficulty']}\n"
    
    if filters.get('min_duration') or filters.get('max_duration'):
        min_dur = filters.get('min_duration', 0)
        max_dur = filters.get('max_duration', 24)
        filters_text += f"• ⏱️ Длительность: {min_dur}-{max_dur}ч\n"
    
    if filters.get('region'):
        filters_text += f"• 🗺️ Регион: {filters['region']}\n"
    
    if filters.get('min_altitude') or filters.get('max_altitude'):
        min_alt = filters.get('min_altitude', 0)
        max_alt = filters.get('max_altitude', 3000)
        filters_text += f"• 📏 Высота: {min_alt}-{max_alt}м\n"
    
    return filters_text

# Экспортируем функции для использования в других модулях
__all__ = [
    'start_search', 
    'quick_search_handler',
    'process_quick_search', 
    'advanced_search_handler',
    'filter_difficulty_handler',
    'set_difficulty_filter',
    'filter_duration_handler', 
    'set_duration_filter',
    'filter_region_handler',
    'set_region_filter',
    'altitude_filter_handler',
    'set_altitude_filter',
    'apply_filters_search',
    'reset_filters_handler',
    'popular_routes_handler',
    'search_routes',
    'handle_pagination',
    'get_alternative_suggestions'
]
