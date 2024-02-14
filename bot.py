from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler

TOKEN = '6864128581:AAEXqLq2qZIvjy8efP9rKUZIieiQ54wbmAI'

# Определение состояний диалога
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

# Клавиатуры для выбора
reply_keyboard = [
    ['Готовый торт', 'Самостоятельное приготовление'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Привет! Хотите заказать готовый торт или предпочитаете приготовить самостоятельно?",
        reply_markup=markup,
    )
    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    if text == "Готовый торт":
        update.message.reply_text(
            'Какой торт вы хотите заказать? Вот наши варианты: Торт 1, Торт 2, Торт 3')
        return TYPING_REPLY
    elif text == "Самостоятельное приготовление":
        update.message.reply_text(
            'Какой размер торта вы хотите? Напишите размер.')
        return TYPING_CHOICE


def custom_choice(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Пожалуйста, укажите ваш выбор.')
    return TYPING_REPLY


def received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    update.message.reply_text(f"Вы выбрали: {text}. Спасибо за ваш заказ!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Готовый торт|Самостоятельное приготовление)$'), regular_choice)],
            TYPING_CHOICE: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), custom_choice)],
            TYPING_REPLY: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), received_information)],
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
