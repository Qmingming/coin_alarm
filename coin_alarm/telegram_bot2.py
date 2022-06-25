import asyncio
import logging
from telegram import Update
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

user_token = '5576835435:AAHxTLt6KiDKh4XWNiFcrn0_wqcRmDbHbD8'
chat_id_myself = '501305840'
bot = telegram.Bot(user_token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def send(msg):
    bot = telegram.Bot(user_token)
    await bot.sendMessage(chat_id=chat_id_myself, text=msg)



if __name__ == '__main__':
    #application = ApplicationBuilder().token('5576835435:AAHxTLt6KiDKh4XWNiFcrn0_wqcRmDbHbD8').build()

    #start_handler = CommandHandler('start', start)
    #application.add_handler(start_handler)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(send("sup"))

    #application.run_polling()
