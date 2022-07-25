import logging
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot/log/info.log',
)

logger = logging.getLogger(__name__)

TOKEN = os.environ.get('VPN_BOT_TOKEN', '')

QIWI_P2P = os.environ.get('QIWI_P2P', '')
