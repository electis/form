import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, \
    MessageHandler, filters

import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MAIN, SITES, SITE, TYPING_REPLY, TYPING_CHOICE = range(5)
SAVE, BACK = 'save', 'back'

main_keyboard = [
    ["Аккаунт", "Сайты"],
    ["Баланс", "Помощь"],
]
sites_keyboard = [
    ["Добавить сайт", "Назад"]
]
site_keyboard = (
    ("domain", "Домен (Обязательно)"),
    ("email", "Почта для уведомлений"),
    ("redirect", "Ссылка редиректа"),
    ("captcha_required", "Проверка капчи"),
    ("captcha_key", "Ключ капчи"),
    ("captcha_secret_key", "Секретный ключ капчи"),
    ("description", "Описание сайта"),
)


def make_site_keyboard(data: dict = None) -> InlineKeyboardMarkup:
    data = data or dict()
    keyboard = list()
    for col in site_keyboard:
        keyboard.append([
            InlineKeyboardButton(col[1], callback_data=col[0]),
            InlineKeyboardButton(data.get(col[0], '---'), callback_data=col[0])
        ])
    keyboard.append([InlineKeyboardButton('Сохранить', callback_data=SAVE)])
    keyboard.append([InlineKeyboardButton('Отмена', callback_data=BACK)])
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_user.send_message(
        "Привет! Это бот для управления аккаунтом обработчика HTML-форм сервиса form.electis.ru\n"
        "Выберите пункт меню",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True),
    )
    return MAIN


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вывод собранной информации и завершение разговора."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"BB",
        reply_markup=ReplyKeyboardRemove(),
    )
    user_data.clear()
    return ConversationHandler.END


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    if text == 'Сайты':
        reply_text = 'Ваши сайты:\n...'
        await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(sites_keyboard, one_time_keyboard=True))
        return SITES
    await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")
    return TYPING_REPLY


async def sites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    if text == sites_keyboard[0][0]:
        menu = await update.message.reply_text(text, reply_markup=make_site_keyboard())
        context.user_data["menu_msg"] = menu.message_id
        context.user_data["menu_text"] = menu.text
        return SITE
    return await start(update, context)


async def site_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    variant = query.data
    await query.answer()

    context.user_data["choice"] = variant

    if variant == SAVE:
        ...
        return SITES
    elif variant == BACK:
        ...
        chat_id = context._chat_id
        await context.bot.deleteMessage(message_id=context.user_data["menu"], chat_id=chat_id)
        reply_text = 'Ваши сайты:\n...'
        await update.effective_user.send_message(
            reply_text, reply_markup=ReplyKeyboardMarkup(sites_keyboard, one_time_keyboard=True))
        return SITES

    await query.edit_message_text(text=f"Введите {dict(site_keyboard)[variant]}")
    return TYPING_REPLY


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(user_data.get('menu_text') or text, reply_markup=make_site_keyboard(user_data))
    return SITE


if __name__ == "__main__":
    application = Application.builder().token(settings.INFORM_TG_TOKEN).build()
    regex_from_2d = lambda x: '|'.join(['|'.join(a) for a in x])

    site = '|'.join([a[0] for a in site_keyboard])

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex(""), start),
            CallbackQueryHandler(start),
        ],
        states={
            MAIN: [
                MessageHandler(filters.Regex(f"^({regex_from_2d(main_keyboard)})$"), main_menu),
                CommandHandler("start", start),
            ],
            SITES: [
                MessageHandler(filters.Regex(f"^({regex_from_2d(sites_keyboard)})$"), sites_menu),
                CommandHandler("start", start),
            ],
            SITE: [
                CallbackQueryHandler(site_menu),
                CommandHandler("start", start),
            ],
            TYPING_CHOICE: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), main_menu),
                CommandHandler("start", start),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), received_information),
                CommandHandler("start", start),
            ],
        },
        fallbacks=[CommandHandler("stop", done)],
    )

    application.add_handler(conv_handler)
    # application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

'''
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["Почта", "Favourite colour"],
    ["Number of siblings", "Something else..."],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: dict[str, str]) -> str:
    """Вспомогательная функция для форматирования
    собранной информации о пользователе."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Это бот для управления аккаунтом обработчика HTML-форм сервиса form.electis.ru",
        reply_markup=markup,
    )
    return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрос информации о выбранном предопределенном выборе."""
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")
    return TYPING_REPLY


async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрос описания пользовательской категории."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )
    return TYPING_CHOICE


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)}You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )
    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вывод собранной информации и завершение разговора."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )
    user_data.clear()
    return ConversationHandler.END


if __name__ == "__main__":
    application = Application.builder().token(settings.INFORM_TG_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Age|Favourite colour|Number of siblings)$"), regular_choice
                ),
                MessageHandler(filters.Regex("^Something else...$"), custom_choice),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    application.add_handler(conv_handler)
    # Запуск бота.
    application.run_polling()
'''
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from tortoise import Tortoise, run_async

import settings
from models import Users

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def init():
    await Tortoise.init(settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def button(update, _):
    query = update.callback_query
    variant = query.data
    await query.answer()

    await query.edit_message_text(text=f"Выбранный вариант: {variant}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or update.effective_user.id
    # user = await Users.get_or_create(username=username)
    keyboard = [
        [InlineKeyboardButton("Задать почту", callback_data='mail')],
        [InlineKeyboardButton("Капча неактивна", callback_data='captcha')],
        [
            InlineKeyboardButton("Тест 1", callback_data='1'),
            InlineKeyboardButton("Тест 2", callback_data='2'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите пункт", reply_markup=reply_markup)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or update.effective_user.id
    # user = await Users.get_or_create(username=username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="bb")


async def unknown(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def text(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


if __name__ == '__main__':
    run_async(init())
    application = ApplicationBuilder().token(settings.INFORM_TG_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.run_polling()
"""
