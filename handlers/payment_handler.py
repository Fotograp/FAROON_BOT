import time
import logging
import asyncio
from config import PREMIUM_PRICES, PROVIDER_TOKEN
from user_data import add_premium_user
from utils.notifications import notify_payment_issue, notify_premium_activation

logger = logging.getLogger(__name__)

def validate_payment_payload(invoice_payload: str, user_id: int) -> bool:
    """Валидация payload платежа - защита от подделки"""
    try:
        # Формат: premium_{user_id}_{months}_{timestamp}
        parts = invoice_payload.split('_')
        if len(parts) != 4 or parts[0] != 'premium':
            logger.warning(f"Неверный формат payload: {invoice_payload}")
            return False
        
        payload_user_id = int(parts[1])
        months = int(parts[2])
        timestamp = int(parts[3])
        
        # КРИТИЧНО: Проверка соответствия user_id
        if payload_user_id != user_id:
            logger.warning(f"Несоответствие user_id: ожидалось {user_id}, получено {payload_user_id}")
            return False
            
        # Проверка времени (не старше 1 часа)
        if time.time() - timestamp > 3600:
            logger.warning(f"Просроченный payload: {invoice_payload}")
            return False
            
        # Проверка корректности месяцев подписки
        if months not in [1, 3, 12]:
            logger.warning(f"Некорректное количество месяцев: {months}")
            return False
            
        return True
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка парсинга payload: {e}, payload: {invoice_payload}")
        return False

def create_invoice(user_id, months):
    """Создание инвойса для Telegram Payments"""
    try:
        price = PREMIUM_PRICES.get(months)
        if not price:
            logger.error(f"Цена не найдена для месяцев: {months}")
            return None
            
        # Добавляем timestamp для защиты
        timestamp = int(time.time())
        
        invoice_data = {
            'title': f'💎 Premium подписка - {months} мес',
            'description': f'Доступ ко всем премиум функциям на {months} месяцев',
            'payload': f'premium_{user_id}_{months}_{timestamp}',
            'provider_token': PROVIDER_TOKEN,
            'currency': 'RUB',
            'prices': [{'label': 'Premium подписка', 'amount': price}],
            'start_parameter': f'premium_{months}',
        }
        
        logger.info(f"Создан инвойс для user_id={user_id}, months={months}")
        return invoice_data
        
    except Exception as e:
        logger.error(f"Ошибка создания инвойса: {e}, user_id={user_id}, months={months}")
        return None

def handle_successful_payment(user_id, payload):
    """Обработка успешной оплаты с валидацией и логированием"""
    try:
        logger.info(f"Обработка платежа: user_id={user_id}, payload={payload}")
        
        # ВАЖНО: Проверяем payload перед активацией
        if not validate_payment_payload(payload, user_id):
            logger.error(f"НЕВАЛИДНЫЙ PAYLOAD: user_id={user_id}, payload={payload}")
            # УВЕДОМЛЕНИЕ АДМИНУ О ПОДОЗРИТЕЛЬНОМ ПЛАТЕЖЕ
            asyncio.create_task(notify_payment_issue(user_id, "Невалидный payload (возможная подделка)", payload))
            return False
            
        # Извлекаем months из payload
        months = int(payload.split('_')[2])
        
        # Активируем Premium подписку
        success = add_premium_user(user_id, months)
        if success:
            logger.info(f"✅ PREMIUM АКТИВИРОВАН: user_id={user_id}, months={months}")
            # УВЕДОМЛЕНИЕ О УСПЕШНОЙ АКТИВАЦИИ
            asyncio.create_task(notify_premium_activation(user_id, months))
        else:
            logger.error(f"❌ ОШИБКА БАЗЫ ДАННЫХ: user_id={user_id}, months={months}")
            # УВЕДОМЛЕНИЕ ОБ ОШИБКЕ БАЗЫ
            asyncio.create_task(notify_payment_issue(user_id, "Ошибка базы данных при активации Premium", payload))
            
        return success
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА АКТИВАЦИИ: {e}, user_id={user_id}, payload={payload}")
        # УВЕДОМЛЕНИЕ О КРИТИЧЕСКОЙ ОШИБКЕ
        asyncio.create_task(notify_payment_issue(user_id, f"Критическая ошибка активации: {str(e)}", payload))
        return False
