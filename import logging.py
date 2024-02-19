
from telegram import Bot
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.utils.request import Request

import logging
import csv
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TORT_MAP = {
    1: 'Готовый',
    2: 'Самостоятельное приготовление',
}

VID_TORTA = {
    1: ('Медовик', 100),
    2: ('Наполеон', 200),
    3: ('Хозяюшка', 300),
}

LEVELS_MAP = {
    1: ('Один уровень', 450),
    2: ('Два уровня', 750),
    3: ('Три уровня', 1150),
}

COMMENTS_MAP = {
    1: 'Да',
    2: 'Нет',
}

TEXT_MAP = {
    1: ('Да', 500),
    2: ('Нет', 0),
}

FORM_MAP = {
    'square': ('Квадрат', 600),
    'circle': ('Круг', 400),
    'rectangle': ('Прямоугольник', 1000)
}

TOPPING_MAP = {
    'none': ('Без топпинга', 0),
    'white_choco': ('Белый шоколад', 200),
    'caramel': ('Карамельный сироп', 180),
}

BERRIES_MAP = {
    'none': ('Без ягод', 0),
    'blackberry': ('Ежевика', 400),
    'strawberry': ('Клубника', 300),
    # Остальные ягоды
}

DECOR_MAP = {
    'none': ('Без декора', 0),
    'marmalade': ('Мармелад', 200),
    # Остальной декор
}


NAME, CAKE, TEXT, LEVELS, TYPE_CAKE, WAITING_FOR_COMMENT, WAITING_FOR_TEXT, DIFFERENT_DECOR, ADRESS, CHOSE_BERRIES, CHOOSE_DECOR, SHAPE, TOPPING, BERRIES, DECOR, COMMENT, DELIVERY_DATE, DELIVERY_TIME = range(
    18)


CALLBACK_BEGIN = 'x1'


def start_buttons_handler(update: Update, context: CallbackContext):
    """ Не относится к сценарию диалога, но создаёт начальные inline-кнопки
    """
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Начать', callback_data=CALLBACK_BEGIN),
            ],
        ],
    )
    update.message.reply_text(
        'Нажми на кнопку:',
        reply_markup=inline_buttons,
    )


def start_handler(update: Update, context: CallbackContext):
    """ Начало взаимодействия по клику на inline-кнопку
    """
    #init = update.callback_query.data
    chat_id = update.callback_query.message.chat.id
    update.callback_query.answer()

    # Спросить имя
    update.callback_query.bot.send_message(
        chat_id=chat_id,
        text='Введи своё имя чтобы продолжить:',
    )
    return NAME


def name_handler(update: Update, context: CallbackContext):
    # Получить имя
    context.user_data['name'] = update.message.text

    # Спросить пол
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value, callback_data=key)
             for key, value in TORT_MAP.items()],
        ],
    )
    update.message.reply_text(
        text='Выберите вариант торта чтобы продолжить',
        reply_markup=inline_buttons,
    )
    return CAKE


def cake_handler(update: Update, context: CallbackContext):
    cake = int(update.callback_query.data)
    context.user_data['cake'] = cake

    if cake == 1:
        inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=value[0], callback_data=key)
                 for key, value in VID_TORTA.items()],
            ],
        )
        update.callback_query.message.reply_text(
            'Выберите торт из предложенных',
            reply_markup=inline_buttons,)
        return TYPE_CAKE
    elif cake == 2:
        # Выбор количества уровней для самостоятельного приготовления
        inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=value[0], callback_data=key)
                 for key, value in LEVELS_MAP.items()],
            ],
        )
        update.callback_query.message.reply_text(
            'Выберите количество уровней:',
            reply_markup=inline_buttons,
        )
        return LEVELS


def type_cake_handler(update: Update, context: CallbackContext):
    type_cake = update.callback_query.data
    context.user_data['type_cake'] = VID_TORTA[int(type_cake)][1]
    context.user_data['price'] = VID_TORTA[int(type_cake)][1]

    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value, callback_data=key)
             for key, value in COMMENTS_MAP.items()],
        ],
    )
    update.callback_query.message.reply_text(
        'Хотите добавить комментарий к заказу?',
        reply_markup=inline_buttons,)
    return COMMENT


def levels_handler(update: Update, context: CallbackContext):
    levels = int(update.callback_query.data)

    # Сохраняем комментарий в user_data
    context.user_data['levels'] = LEVELS_MAP.get(int(levels))[0]
    context.user_data['price'] = LEVELS_MAP.get(int(levels))[1]

    #chat_id = update.callback_query.message.chat.id
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value[0], callback_data=key)
             for key, value in FORM_MAP.items()],
        ],
    )
    # update.callback_query.answer()
    update.callback_query.message.reply_text(
        'Выберите форму:',
        reply_markup=inline_buttons,
    )
    # context.bot.send_message(
    #    chat_id=chat_id,
    #    text='Введи адрес доставки:',
    #)
    return SHAPE


def shape_handler(update: Update, context: CallbackContext):
    shape = update.callback_query.data

    # Сохраняем комментарий в user_data
    context.user_data['shape'] = FORM_MAP.get(shape)[0]
    context.user_data['price'] += FORM_MAP.get(shape)[1]
    #chat_id = update.callback_query.message.chat.id
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value[0], callback_data=key)
             for key, value in TOPPING_MAP.items()],
        ],
    )
    update.callback_query.answer()
    update.callback_query.message.reply_text(
        'Выберите топинг:',
        reply_markup=inline_buttons,
    )
    return TOPPING


def toping_handler(update: Update, context: CallbackContext):
    shape = update.callback_query.data

    # Сохраняем комментарий в user_data
    context.user_data['topping'] = TOPPING_MAP.get(shape)[0]
    context.user_data['price'] += TOPPING_MAP.get(shape)[1]
    #chat_id = update.callback_query.message.chat.id
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value, callback_data=key)
             for key, value in COMMENTS_MAP.items()],
        ],
    )
    update.callback_query.answer()
    update.callback_query.message.reply_text(
        'Хотите добавить ягоды:',
        reply_markup=inline_buttons,
    )
    # context.bot.send_message(
    #    chat_id=chat_id,
    #    text='Хотите добавить ягоды:',
    #)
    return BERRIES


def berry_handler(update: Update, context: CallbackContext):
    berry_answer = int(update.callback_query.data)
    #context.user_data[CAKE] = cake

    if berry_answer == 1:
        inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=value[0], callback_data=key)
                 for key, value in BERRIES_MAP.items()],
            ],
        )
        update.callback_query.message.reply_text(
            'Какие ягоды хотите?',
            reply_markup=inline_buttons,)
        return CHOSE_BERRIES
    else:
        inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=value, callback_data=key)
                 for key, value in COMMENTS_MAP.items()],
            ],
        )
        update.callback_query.message.reply_text(
            text='Хотите добавить декор?',
            reply_markup=inline_buttons,
        )
        return CHOOSE_DECOR


def choose_berries_handler(update: Update, context: CallbackContext):
    berry_choice = update.callback_query.data

    # Записываем выбор ягод и их стоимость
    context.user_data['berry_choice'] = berry_choice
    context.user_data['price'] += BERRIES_MAP[berry_choice][1]
    # Теперь спрашиваем о декоре
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value, callback_data=key)
             for key, value in COMMENTS_MAP.items()],
        ],
    )
    update.callback_query.message.reply_text(
        text='Хотите добавить декор?',
        reply_markup=inline_buttons,
    )
    return CHOOSE_DECOR


def ask_for_decor(update: Update, context: CallbackContext):
    #query = update.callback_query
    # Отображаем доступные варианты декора
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value, callback_data=key)
             for key, value in COMMENTS_MAP.items()],
        ],
    )
    update.message.reply_text(
        text='Хотите добавить декор?',
        reply_markup=inline_buttons,
    )
    return CHOOSE_DECOR


def decor_handler(update: Update, context: CallbackContext):
    decor_answer = int(update.callback_query.data)
    #context.user_data[CAKE] = cake

    if decor_answer == 1:
        inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=value[0], callback_data=key)
                 for key, value in DECOR_MAP.items()],
            ],
        )
        update.callback_query.message.reply_text(
            'Какoй декор хотите?',
            reply_markup=inline_buttons,)
        return DIFFERENT_DECOR
    else:
        inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=value, callback_data=key)
                 for key, value in COMMENTS_MAP.items()],
            ],
        )
        update.callback_query.message.reply_text(
            'Хотите добавить текст?',
            reply_markup=inline_buttons,)
        return TEXT


def choose_decor_handler(update: Update, context: CallbackContext):
    decor_choice = update.callback_query.data

    # Записываем выбор ягод и их стоимость
    context.user_data['decor_choice'] = decor_choice
    context.user_data['price'] += DECOR_MAP[decor_choice][1]
    # Теперь спрашиваем о декоре\
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=value, callback_data=key)
             for key, value in COMMENTS_MAP.items()],
        ],
    )
    update.callback_query.message.reply_text(
        'Хотите добавить текст?',
        reply_markup=inline_buttons,)
    return TEXT


def text_handler(update: Update, context: CallbackContext):
    comment = int(update.callback_query.data)

    if comment == 1:
        #chat_id = update.callback_query.message.chat.id
        update.callback_query.answer()
        context.user_data['price'] += TEXT_MAP[comment][1]
        # Запрашиваем у пользователя ввод комментария

        update.callback_query.message.reply_text(
            'Введите текст',)
        return WAITING_FOR_TEXT
    else:
        chat_id = update.callback_query.message.chat.id
        update.callback_query.answer()
        context.bot.send_message(
            chat_id=chat_id,
            text='Введи адрес доставки:',
        )
        return ADRESS


def waiting_for_text(update: Update, context: CallbackContext):
    # Получаем текст комментария от пользователя
    user_desire = update.message.text

    # Сохраняем комментарий в user_data
    context.user_data['text'] = user_desire
    # Переходим к следующему шагу (например, запросу адреса)
    update.message.reply_text(
        'Спасибо за комментарий! Теперь введи адрес доставки:')
    return ADRESS


def comment_handler(update: Update, context: CallbackContext):
    logger.info("Entered comment_handler")
    comment = int(update.callback_query.data)
    logger.info(f"Comment callback data: {comment}")

    if comment == 1:
        chat_id = update.callback_query.message.chat.id
        update.callback_query.answer()

        # Запрашиваем у пользователя ввод комментария
        context.bot.send_message(
            chat_id=chat_id,
            text='Введи комментарий:',
        )
        return WAITING_FOR_COMMENT
    else:
        chat_id = update.callback_query.message.chat.id
        update.callback_query.answer()
        context.bot.send_message(
            chat_id=chat_id,
            text='Введи адрес доставки:',
        )
        return ADRESS


def waiting_for_comment_handler(update: Update, context: CallbackContext):
    # Получаем текст комментария от пользователя
    user_comment = update.message.text

    # Сохраняем комментарий в user_data
    context.user_data['comment'] = user_comment

    # Переходим к следующему шагу (например, запросу адреса)
    update.message.reply_text(
        'Спасибо за комментарий! Теперь введи адрес доставки:')
    return ADRESS


def finish_handler(update: Update, context: CallbackContext):
    # Получение адреса и сохранение его в user_data
    address = update.message.text
    context.user_data['address'] = address

    # Получение общей цены
    total_price = context.user_data.get('price', 0)

    # Сообщение пользователю
    update.message.reply_text(
        f'Ваш заказ оформлен. Общая стоимость: {total_price} руб.')

    # Формирование данных для записи
    order_data = {
        'name': context.user_data.get('name', ''),
        'address': address,
        'cake': context.user_data.get('cake', ''),
        'type_cake': context.user_data.get('type_cake', ''),
        'levels': context.user_data.get('levels', ''),
        'shape': context.user_data.get('shape', ''),
        'toping': context.user_data.get('topping', ''),
        'berry_choice': context.user_data.get('berry_choice', ''),
        'decor_choice': context.user_data.get('decor_choice', ''),
        'text': context.user_data.get('text', ''),
        'comment': context.user_data.get('comment', ''),
        'total_price': total_price,
        # Добавьте все остальные данные, которые нужно сохранить
    }

    # Запись данных в CSV
    file_path = './orders.csv'  # Укажите путь к вашему файлу
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=order_data.keys())
        # Если файл пуст, напишите заголовок
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(order_data)

    # Очистка данных пользователя
    context.user_data.clear()

    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext):
    """ Отменить весь процесс диалога. Данные будут утеряны
    """
    update.message.reply_text('Отмена. Для начала с нуля нажмите /start')
    return ConversationHandler.END


def echo_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Нажмите /start для заполнения анкеты!',
    )


def main():
    request = Request(con_pool_size=8)
    bot = Bot(
        token='6583277326:AAEIxd1l7JllW0y96Cy9vElWMgMfE6QIXK8',
        request=request
    )
    updater = Updater(
        bot=bot,
        use_context=True
    )

    # Проверить что бот корректно подключился к Telegram API
    info = bot.get_me()
    #logger.info(f'Bot info: {info}')

    # Навесить обработчики команд
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_handler),
        ],
        states={
            NAME: [
                MessageHandler(Filters.all, name_handler),
            ],
            CAKE: [
                CallbackQueryHandler(cake_handler),
            ],
            TYPE_CAKE: [
                CallbackQueryHandler(type_cake_handler),
            ],
            COMMENT: [
                CallbackQueryHandler(comment_handler),
            ],
            LEVELS: [
                CallbackQueryHandler(levels_handler),
            ],
            SHAPE: [
                CallbackQueryHandler(shape_handler),
            ],
            TOPPING: [
                CallbackQueryHandler(toping_handler),
            ],
            BERRIES: [
                CallbackQueryHandler(berry_handler),
            ],
            CHOSE_BERRIES: [
                CallbackQueryHandler(choose_berries_handler),
            ],
            CHOOSE_DECOR: [
                CallbackQueryHandler(decor_handler),
            ],
            DECOR: [
                CommandHandler('decor', ask_for_decor),
            ],
            DIFFERENT_DECOR: [
                CallbackQueryHandler(choose_decor_handler),
            ],
            WAITING_FOR_COMMENT: [
                MessageHandler(Filters.all, waiting_for_comment_handler),
            ],
            TEXT: [
                CallbackQueryHandler(text_handler),
            ],
            WAITING_FOR_TEXT: [
                MessageHandler(Filters.all, waiting_for_text),
            ],
            ADRESS: [
                MessageHandler(Filters.all, finish_handler),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ],
    )
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(
        CommandHandler('start', start_buttons_handler))
   # updater.dispatcher.add_handler(MessageHandler(Filters.all, echo_handler))
   # logging.getLogger("").setLevel(logging.WARNING)
    # Начать бесконечную обработку входящих сообщений
    updater.start_polling()
    updater.idle()
    #logger.info('Stopped Anketa-bot')


if __name__ == '__main__':
    main()
