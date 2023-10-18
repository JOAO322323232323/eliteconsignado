import logging
import asyncio
from telegram import Bot
from telegram import InputFile
from telegram.error import TelegramError

# Configuração do bot (substitua pelo seu token)
BOT_TOKEN = '6477981448:AAFqTlfVOLKce1QyqWgJAdsVw5Td1JLS2Ps'
bot = Bot(token=BOT_TOKEN)

# ID do chat (seu ID do Telegram)
CHAT_ID = '1093868027'

# Caminho para o arquivo que você deseja enviar
arquivo_path = 'dados.db'  # Substitua pelo caminho real do arquivo

async def enviar_arquivo():
    try:
        with open(arquivo_path, 'rb') as arquivo:
            await bot.send_document(chat_id=CHAT_ID, document=InputFile(arquivo))
        print("Arquivo enviado com sucesso!")
    except TelegramError as e:
        print("Erro ao enviar o arquivo:", e)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(enviar_arquivo())