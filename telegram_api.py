#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Don't forget to enable inline mode with @BotFather

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import html
import json
import logging
import os
import traceback
from html import escape
from uuid import uuid4

import telegram
from sqlalchemy.util import asyncio
from telegram import __version__ as TG_VER

from coin_info import CoinInfo

USER_TOKEN = "5576835435:AAHxTLt6KiDKh4XWNiFcrn0_wqcRmDbHbD8"
CHATID_ME = "501305840"

bot = telegram.Bot(USER_TOKEN)

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
reply_keyboard = []


# Define a few command handlers. These usually take the two arguments update and
# context.
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=USER_TOKEN, text=message, parse_mode=ParseMode.HTML
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


'''
async def get_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    try:
        pic = open(r'D:\python_workspace\coin_alarm\plot.png', 'rb')
        await bot.sendPhoto(chat_id=CHATID_ME, photo=pic)
    except Exception as err:
        print(err)
'''


async def get_table_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    try:
        Win.screenshot()
        base_dir = os.getcwd()
        filename = r'table.png'
        pic = open(os.path.join(base_dir, filename), 'rb')
        await bot.sendPhoto(chat_id=CHATID_ME, photo=pic)
    except Exception as err:
        print(err)


async def turn_alarm_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    try:
        print("alarm_stop: %s " % CoinInfo.alarm_stop)
        CoinInfo.alarm_stop = 1
        print("alarm_stop: %s " % CoinInfo.alarm_stop)
    except Exception as err:
        print(err)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query

    if query == "":
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"<b>{escape(query)}</b>", parse_mode=ParseMode.HTML
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"<i>{escape(query)}</i>", parse_mode=ParseMode.HTML
            ),
        ),
    ]

    await update.inline_query.answer(results)


async def get_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Select the chart you want to get from below list",
        reply_markup=markup,
    )

    return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    print(text)
    # await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")
    Win.plot(text)
    try:
        base_dir = os.getcwd()
        filename = r'plot.png'
        pic = open(os.path.join(base_dir, filename), 'rb')
        await bot.sendPhoto(chat_id=CHATID_ME, photo=pic)
    except Exception as err:
        print(err)

    context.user_data.clear()
    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        # f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        # reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


async def bot_send_msg(msg):
    await bot.send_message(text=msg, chat_id=CHATID_ME)


async def bot_send_pic(pic):
    try:
        pic = open(pic, 'rb')
        print("start sending pic")
        await bot.sendPhoto(chat_id=CHATID_ME, photo=pic)
        print("done sending pic")
    except Exception as err:
        print(err)


def send_pic(pic):
    print("send pic")
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as err:
        print(err)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    finally:
        loop.run_until_complete(bot_send_pic(pic))


def send_msg(msg):
    print("send msg - %s" % msg)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as err:
        print(err)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    finally:
        loop.run_until_complete(bot_send_msg(msg))


def main(myWindow):
    """Run the bot."""
    global Win
    Win = myWindow

    for idx, coin in enumerate(Win.coin_list):
        reply_keyboard.append([])
        reply_keyboard[idx].append(coin.name)
    print(reply_keyboard)
    global markup
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(USER_TOKEN).build()

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # application.add_handler(CommandHandler("get_chart", get_chart_command))
    application.add_handler(CommandHandler("get_table", get_table_command))
    application.add_handler(CommandHandler("turn_alarm_off", turn_alarm_off))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("get_chart", get_chart_command)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.TEXT, regular_choice
                ),
                # MessageHandler(filters.Regex("^Something else...$"), help),
            ],
        },
        fallbacks=[MessageHandler(filters.TEXT, done)],
    )
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(InlineQueryHandler(inline_query))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
