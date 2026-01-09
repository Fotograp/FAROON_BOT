import time
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.validators import validate_callback_data

# Импорты модульных обработчиков
from handlers.handlers.quad_handlers import handle_quad_callbacks
from handlers.handlers.active_handlers import handle_active_callbacks
from handlers.handlers.hiking_handlers import handle_hiking_callbacks
from handlers.handlers.location_handlers import handle_location_callbacks
from handlers.handlers.water_handlers import handle_water_callbacks
from handlers.handlers.resort_handlers import handle_resort_callbacks
from handlers.handlers.weather_handlers import handle_weather_callbacks
from handlers.handlers.premium_handlers import handle_premium_callbacks
from handlers.handlers.utility_handlers import show_development_message
from handlers.handlers.navigation_handlers import handle_navigation_callbacks
from handlers.handlers.favorites_handlers import handle_favorites_callbacks
from handlers.handlers.search_handlers import handle_search_callbacks
from handlers.handlers.photo_handlers import handle_photo_callbacks
from handlers.handlers.gps_handlers import handle_gps_callbacks
from handlers.handlers.progress_handlers import handle_progress_callbacks
from handlers.handlers.equipment_handlers import handle_equipment_callbacks
from handlers.handlers.route_actions_handlers import handle_route_actions_callbacks
from handlers.handlers.partner_handlers import handle_partner_callbacks
from handlers.gps_navigation import handle_gps_navigation, download_kml_track, download_gpx_track, download_pdf_map, show_map_view, show_gps_instructions, get_track_data

logger = logging.getLogger(__name__)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный роутер для обработки inline кнопок"""
    start_time = time.time()
    
    query = update.callback_query
    await query.answer()
    callback_data = query.data
    user_id = query.from_user.id

    logger.debug(f"Получен callback_data: '{callback_data}' от user_id={user_id}")

    # ВАЛИДАЦИЯ callback_data
    if not validate_callback_data(callback_data):
        logger.warning(f"Невалидный callback_data от user_id={user_id}: {callback_data}")
        await query.answer("❌ Ошибка: неверные данные")
        return

    # ✅ ОБРАБОТКА ЗАКРЫТИЯ СООБЩЕНИЙ
    if callback_data == "close_message":
        try:
            await query.message.delete()
        except Exception as e:
            print(f"🔴 ОШИБКА В РОУТЕРЕ: {callback_data} -> {e}")  # ← ДОБАВИТЬ
            logger.warning(f"Не удалось удалить сообщение: {e}")
            await query.answer("✅ Закрыто")
        return

    # 🎯 ПЕРЕНАПРАВЛЕНИЕ ПО КАТЕГОРИЯМ
    try:
        # КВАДРОТУРЫ (отдельный обработчик) - ДОЛЖЕН БЫТЬ ПЕРВЫМ
        if (callback_data.startswith("quad_") or
            callback_data == "active_quad" or
            callback_data.startswith("details_quad_")):
            handled = await handle_quad_callbacks(update, context)
            if handled:
                return
        
        # 🔥 ДЕЙСТВИЯ С МАРШРУТАМИ - ПЕРЕМЕЩАЕМ ВЫШЕ ДЛЯ ПРАВИЛЬНОЙ ОБРАБОТКИ
        elif (callback_data.startswith("actions_") or
              callback_data.startswith("details_") or
              callback_data.startswith("hotel_details_") or
              callback_data.startswith("hunting_details_") or
              callback_data.startswith("book_")):
            handled = await handle_route_actions_callbacks(update, context)
            if handled:
                return

        # КОНКРЕТНЫЕ CALLBACK'И ХАКАСИИ
        elif callback_data in ["khakassia_ordzhonikidzevsky", "khakassia_shirinsky", "khakassia_abakan", 
                              "khakassia_ust_abakansky", "khakassia_askizsky", "khakassia_tashtypsky", 
                              "khakassia_bogradsky"]:
            handled = await handle_hiking_callbacks(update, context)
            if handled:
                return
        
        # АКТИВНЫЙ ОТДЫХ (кроме квадротуров)
        elif (callback_data in ["active_rafting", "active_climbing", "active_mtb", 
                              "active_freeride", "category_active"]):
            handled = await handle_active_callbacks(update, context)
            if handled:
                return
        
        # ПЕШИЙ ТУРИЗМ
        elif (callback_data.startswith("hiking_") or 
              callback_data.startswith("borus_") or
              callback_data.startswith("west_") or
              callback_data.startswith("east_") or
              callback_data.startswith("ergaki_") or
              callback_data.startswith("khakassia_") or
              (callback_data.startswith("krasnoyarsk_") and not callback_data.startswith("krasnoyarsk_shop_")) or
              callback_data == "category_hiking"):
            handled = await handle_hiking_callbacks(update, context)
            if handled:
                return
        
        # ЛОКАЦИИ (охота и рыбалка)
        elif (callback_data.startswith("hunting_") or
              callback_data == "category_hunting"):
            handled = await handle_location_callbacks(update, context)
            if handled:
                return
        
        # ОТДЫХ У ВОДЫ (пляжи, озера, рыбалка)
        elif (callback_data.startswith("water_") or
              callback_data == "category_water" or
              callback_data in ["water_beaches", "water_lakes", "water_fishing"]):
            handled = await handle_water_callbacks(update, context)
            if handled:
                return
        
        # РАЗМЕЩЕНИЕ И ОТЕЛИ
        elif (callback_data.startswith("resort_") or
              callback_data == "category_resort" or
              callback_data in ["resort_glamping", "resort_guesthouses", "resort_bases", "resort_camping"]):
            handled = await handle_resort_callbacks(update, context)
            if handled:
                return
        
        # ПОГОДА
        elif callback_data.startswith("weather_"):
            handled = await handle_weather_callbacks(update, context)
            if handled:
                return
        
        # PREMIUM ФУНКЦИИ
        elif (callback_data.startswith("premium_") or
              callback_data in ["premium_info", "premium_faq", "premium_purchase", 
                              "premium_back_to_menu", "premium_offline_maps", 
                              "premium_treasures", "premium_my_routes"]):
            handled = await handle_premium_callbacks(update, context)
            if handled:
                return

        # НАВИГАЦИЯ И ВОЗВРАТЫ
        elif (callback_data.startswith("back_") or
              callback_data.startswith("maps_") or
              callback_data.startswith("back_to_route_") or
              callback_data in ["back_main", "main_menu", "back_directions", "back_hiking", 
                               "back_locations", "back_to_borus_menu"]):
            handled = await handle_navigation_callbacks(update, context)
            if handled:
                return

        # ИЗБРАННОЕ
        elif (callback_data.startswith("fav_") or
              callback_data.startswith("add_fav_") or
              callback_data.startswith("remove_fav_") or
              callback_data == "show_favorites"):
            handled = await handle_favorites_callbacks(update, context)
            if handled:
                return

        # ПОИСК И ФИЛЬТРЫ
        elif (callback_data.startswith("search_") or
              callback_data.startswith("page_") or
              callback_data.startswith("altitude_") or
              callback_data in ["search_routes", "quick_search", "advanced_search", 
                               "popular_routes", "filter_altitude", "back_to_filters"]):
            handled = await handle_search_callbacks(update, context)
            if handled:
                return

        # ФОТОГАЛЕРЕЯ
        elif (callback_data.startswith("show_photos_") or
              callback_data.startswith("close_photo_")):
            handled = await handle_photo_callbacks(update, context)
            if handled:
                return

        # СКАЧИВАНИЕ GPS ТРЕКОВ 
        elif callback_data.startswith("download_kml_"):
            route_name = callback_data.replace('download_kml_', '')
            await download_kml_track(update, context, route_name)
            return
    
        elif callback_data.startswith("download_gpx_"):
            route_name = callback_data.replace('download_gpx_', '')
            await download_gpx_track(update, context, route_name)
            return
    
        elif callback_data.startswith("gps_instructions_"):
            route_name = callback_data.replace('gps_instructions_', '')
            await show_gps_instructions(update, context, route_name)
            return

        elif callback_data.startswith("download_pdf_"):
            route_name = callback_data.replace('download_pdf_', '')
            from handlers.gps_navigation import download_pdf_map
            await download_pdf_map(update, context, route_name)
            return

        elif callback_data.startswith("gps_view_"):
            route_name = callback_data.replace('gps_view_', '')
            from handlers.gps_navigation import show_map_view
            await show_map_view(update, context, route_name)
            return

        # GPS НАВИГАЦИЯ - ИСПРАВЛЕННЫЙ БЛОК
        elif callback_data.startswith("gps_nav_"):
            route_name = callback_data.replace('gps_nav_', '')
            # Добавляем проверку наличия GPS данных для маршрута
            track_data = get_track_data(route_name)
            if track_data:
                logger.info(f"Обработка GPS навигации для маршрута: {route_name}")
                await handle_gps_navigation(update, context, route_name)
            else:
                logger.warning(f"GPS данные не найдены для маршрута: {route_name}")
                await query.answer("❌ GPS трек для этого маршрута недоступен", show_alert=True)
            return

        # GPS ОБРАБОТЧИКИ
        elif callback_data.startswith("gps_"):
            handled = await handle_gps_callbacks(update, context)
            if handled:
                return

        # ПРОГРЕСС И ДОСТИЖЕНИЯ
        elif (callback_data.startswith("complete_route_") or
              callback_data in ["show_progress", "show_achievements", "show_stats", "already_completed"]):
            handled = await handle_progress_callbacks(update, context)
            if handled:
                return

        # СНАРЯЖЕНИЕ
        elif (callback_data.startswith("equipment_") or
              callback_data.startswith("equip_type_") or
              callback_data.startswith("shop_") or
              callback_data.startswith("shops_") or
              callback_data in ["equipment_main", "equipment_checklists", "equipment_shops", 
                               "equipment_premium", "close_menu", "shops_city_krasnoyarsk",
                               "krasnoyarsk_shop_1", "krasnoyarsk_shop_2", "krasnoyarsk_shop_3", "shops_city_abakan", "abakan_shop_1", "abakan_shop_2", "abakan_shop_3"]):
            handled = await handle_equipment_callbacks(update, context)
            if handled:
                return

        # ПАРТНЕРСКИЕ СЕРВИСЫ
        elif (callback_data.startswith("hotels_") or
              callback_data.startswith("flights_") or
              callback_data.startswith("tours_")):
            handled = await handle_partner_callbacks(update, context)
            if handled:
                return
        
        # ЕСЛИ НЕ ОБРАБОТАНО - СООБЩЕНИЕ О РАЗРАБОТКЕ
        logger.warning(f"Необработанный callback_data: {callback_data}")
        await show_development_message(query, callback_data)
        return
            
    except ImportError as e:
        logger.error(f"Ошибка импорта модуля: {e}")
        await query.answer("❌ Модуль временно недоступен", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка в роутере: {e}")
        await query.answer("❌ Внутренняя ошибка бота", show_alert=True)

    # ЗАМЕР ВРЕМЕНИ ВЫПОЛНЕНИЯ
    execution_time = time.time() - start_time
    from utils.metrics import metrics
    metrics.track_metric('button_handler_time', execution_time)
