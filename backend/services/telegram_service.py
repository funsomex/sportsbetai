"""
Telegram notification service
"""
import httpx
import logging
from config.settings import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)


async def send_telegram_message(chat_id: str, message: str) -> bool:
    """Send a message via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                logger.info(f"Telegram message sent to {chat_id}")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False


async def send_value_bet_alert(chat_id: str, value_bet: dict) -> bool:
    """Send a value bet alert to Telegram"""
    message = f"""🎯 *Value Bet Detectado*

⚽ *{value_bet['match']['home_team']} vs {value_bet['match']['away_team']}*
🏆 {value_bet['match']['league']}

📊 *Selección:* {value_bet['selection']}
💰 *Cuota:* {value_bet['odds']}
📈 *Valor:* +{value_bet['value_percentage']}%
🎯 *Confianza:* {value_bet['confidence']}%

🏠 Casa: {value_bet['bookmaker']}"""

    return await send_telegram_message(chat_id, message)


async def send_recovery_code(chat_id: str, code: str) -> bool:
    """Send a password recovery code to Telegram"""
    message = f"""🔐 *Código de Recuperación*

Tu código de recuperación de contraseña es:

*{code}*

Este código expira en 15 minutos.

Si no solicitaste este código, ignora este mensaje."""

    return await send_telegram_message(chat_id, message)
