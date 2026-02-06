import os
import time
import schedule
import requests
from solana.rpc.api import Client
from solders.pubkey import Pubkey as PublicKey
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
RPC_URL = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", 1))

required_vars = ["WALLET_ADDRESS", "BOT_TOKEN", "CHAT_ID"]
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Переменная {var} не найдена в .env файле!")

solana_client = Client(RPC_URL)
bot = Bot(token=BOT_TOKEN)
last_signature = None

def check_for_token_creation():
    global last_signature
    print(f"Проверка транзакций для {WALLET_ADDRESS}...")

    try:
        address = PublicKey.from_string(WALLET_ADDRESS)
        signatures_resp = solana_client.get_signatures_for_address(address, limit=10)
        signatures = signatures_resp.value

        if not signatures:
            print("Нет транзакций или ошибка.")
            return

        if last_signature is None:
            last_signature = signatures[0].signature
            print("Инициализация: сохранена первая подпись.")
            return

        for sig_info in signatures:
            if sig_info.signature == last_signature:
                break

            # Получаем детали транзакции
            tx_resp = solana_client.get_transaction(
                sig_info.signature,
                max_supported_transaction_version=0
            )
            tx = tx_resp.value

            if not tx:
                continue

            message = tx.transaction.message
            for instr in message.instructions:
                program_id_index = instr.program_id_index
                program_id = str(message.account_keys[program_id_index])

                # Token Program или Token-2022
                if program_id in [
                    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                    "TokenzQdBNbLqP5VEhdkAS6nBuiPcCKvgEUNJN3XwLfQ"
                ]:
                    if hasattr(instr, 'parsed') and instr.parsed:
                        if instr.parsed.get('type') == 'initializeMint':
                            mint = instr.parsed['info'].get('mint')
                            alert_message = (
                                f"Создан новый токен!\n"
                                f"Кошелёк: {WALLET_ADDRESS}\n"
                                f"Токен Mint: {mint}\n"
                                f"Tx: https://solscan.io/tx/{sig_info.signature}\n"
                                f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            print(alert_message)
                            bot.send_message(chat_id=CHAT_ID, text=alert_message)
                            break

        last_signature = signatures[0].signature

    except Exception as e:
        print(f"Ошибка при проверке: {e}")

# Планировщик
schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_for_token_creation)

print(f"Мониторинг запущен для кошелька {WALLET_ADDRESS}")
print(f"Интервал: каждые {CHECK_INTERVAL_MINUTES} минут")
print("Ожидание задач...")

while True:
    schedule.run_pending()
    time.sleep(1)
