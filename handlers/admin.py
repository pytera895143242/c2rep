from aiogram import types
from misc import dp, bot
import sqlite3
from .sqlit import info_members, reg_one_channel, cheak_traf, obnovatrafika, reg_partners_schet, cheach_all_par, info, \
    reg_utm_support, cheak_support, changee_support, regviplata, cheak_viplats, change_infopay, changee_support_tochka
from .sqlit import delite_user
from .callbak_data import obnovlenie
import asyncio
from datetime import timedelta, datetime

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.utils.exceptions import BotBlocked, ChatNotFound

ADMIN_ID_1 = 494588959  # Cаня
ADMIN_ID_2 = 44520977  # Коля
ADMIN_ID_3 = 678623761  # Бекир
ADMIN_ID_4 = 941730379  # Джейсон
ADMIN_ID_5 = 807911349  # Байзат
ADMIN_ID_6 = 2116984782  # Пабло
ADMIN_ID_7 = 2078570944  # Цукер

ADMIN_ID = [ADMIN_ID_1, ADMIN_ID_2, ADMIN_ID_4, ADMIN_ID_5, ADMIN_ID_6, ADMIN_ID_7]


class reg(StatesGroup):
    name = State()
    fname = State()


class reg_support(StatesGroup):
    step1 = State()
    step2 = State()
    step3 = State()


class st_reg(StatesGroup):
    st_name = State()
    st_fname = State()
    step_q = State()
    step_regbutton = State()


class reg_trafik(StatesGroup):
    traf1 = State()
    traf2 = State()


class partners12(StatesGroup):
    step1 = State()
    step2 = State()
    pye_change_step = State()


@dp.message_handler(commands=['admin'])
async def admin_ka(message: types.Message):
    id = message.from_user.id
    if id in ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        bat_vie_support = types.InlineKeyboardButton(text='👁Просмотр саппортов', callback_data='bat_vie_support')
        bat_reg_support = types.InlineKeyboardButton(text='🆕Регистрация саппорта', callback_data='bat_reg_support')
        bat_setin = types.InlineKeyboardButton(text='🔧Настройка трафика', callback_data='settings')
        reg_new_partners = types.InlineKeyboardButton(text='🔘РЕГИСТРАЦИЯ НОВОГО ПАРТНЕРА',
                                                      callback_data='reg_new_partners')
        vienw_partners = types.InlineKeyboardButton(text='🔘СТАТИСТИКА ВСЕХ ПАРТНЕРОВ', callback_data='vienw_partners')

        bat_a = types.InlineKeyboardButton(text='Трафик', callback_data='list_members')
        bat_e = types.InlineKeyboardButton(text='Рассылка', callback_data='write_message')
        bat_j = types.InlineKeyboardButton(text='База', callback_data='baza')

        markup.add(bat_vie_support)
        markup.add(bat_reg_support)
        markup.add(bat_setin)
        markup.add(reg_new_partners)
        markup.add(vienw_partners)
        markup.add(bat_a, bat_e,bat_j)

        await bot.send_message(message.chat.id, 'Выполнен вход в админ панель', reply_markup=markup)


@dp.callback_query_handler(text='baza')
async def baza(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        a = open('server.db','rb')
        await bot.send_document(chat_id=call.message.chat.id, document=a)
    await bot.answer_callback_query(call.id)

@dp.callback_query_handler(text='bat_vie_support')  # Просмотр всей статистики Support
async def bat_vie_support(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        answer = cheak_support()
        await bot.send_message(chat_id=call.message.chat.id, text='⭐️Статистика по саппортам👇', parse_mode='html')

        for i in answer:
            markup = types.InlineKeyboardMarkup()
            try:
                bat_a = types.InlineKeyboardButton(text='Изменить реквезиты', callback_data=f'change_payinfo{i[0]}')
                markup.add(bat_a)
                bat_b = types.InlineKeyboardButton(text='Обнулить этого чела', callback_data=f'toch_obnal_{i[0]}')
                markup.add(bat_b)
            except:
                print('Ошибка')

            try:
                int(i[1])
                await bot.send_message(chat_id=call.message.chat.id, text=f'<b>Канал:</b> {i[0]}\n'
                                                                          f'<b>Админ:</b> tg://user?id={i[1]}\n'
                                                                          f'<b>Неоплаченный трафик:</b> {i[3]}\n'
                                                                          f'<b>Трафика всего:</b> {i[2]}\n'
                                                                          f'<b>Реквезиты партнера:</b> {i[4]}',
                                       parse_mode='html', reply_markup=markup)
            except:
                await bot.send_message(chat_id=call.message.chat.id, text=f'<b>Канал:</b> {i[0]}\n'
                                                                          f'<b>Админ:</b> {i[1]}\n'
                                                                          f'<b>Неоплаченный трафик:</b> {i[3]}\n'
                                                                          f'<b>Трафика всего:</b> {i[2]}\n'
                                                                          f'<b>Реквезиты партнера:</b> {i[4]}',
                                       parse_mode='html', reply_markup=markup)
            await asyncio.sleep(0.03)
    await bot.answer_callback_query(call.id)


# Изменение реквезитов у канала
@dp.callback_query_handler(text_startswith='change_payinfo')  # Обрабочик изменений реквезитов у саппортов
async def change_payinfo(call: types.callback_query, state: FSMContext):
    if call.message.chat.id in ADMIN_ID:
        channel = call.data[14:]  # Имя канала, где надо изменить реквезиты
        await state.update_data(channel=channel)
        await bot.send_message(call.message.chat.id, text='Введите новые платежные данные партнера!')

        await partners12.pye_change_step.set()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=partners12.pye_change_step, content_types='text')
async def get_pyeinfo_support(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        newinfo = message.text
        d = await state.get_data()
        channel = d['channel']
        change_infopay(channel, newinfo)
        try:
            newinfo = message.text
            d = await state.get_data()
            channel = d['channel']
            change_infopay(channel, newinfo)
            await bot.send_message(message.chat.id, text='Успешно!')

        except:
            await bot.send_message(message.chat.id, text='Неудача')

        await state.finish()


@dp.callback_query_handler(text_startswith='toch_obnal_')  # Точечное обнуление
async def fdsfdsfsdfds(call: types.callback_query, state: FSMContext):
    try:
        channel = (call.data[11:])
        changee_support_tochka(channel)  # Обнуляем чела с каналом channel
        await call.message.answer(text=f'Обнуление канала {channel} Успешно')
    except:
        await call.message.answer(text='Точечное обнуление почему-то не удалось')
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text='bat_reg_support')  # Регистрация Support
async def bat_reg_support(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        await bot.send_message(chat_id=call.message.chat.id,
                               text='Введите основной канал Саппорта в формате @name_channel')
        await reg_support.step1.set()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=reg_support.step1, content_types='text')
async def get_reg_support(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        try:
            await state.update_data(channel=message.text)
            await bot.send_message(chat_id=message.chat.id, text='Введите информацию об админе (Юзер - Имя)')
            await reg_support.step2.set()  # СОСТОЯНИЕ ИНФОРМАЦИИ ОБ АДМИНЕ
        except:
            await bot.send_message(chat_id=message.chat.id, text='Неудача')
            await state.finish()


@dp.message_handler(state=reg_support.step2, content_types='text')
async def get_reg_support2(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        try:
            await state.update_data(user_name=message.text)
            await bot.send_message(chat_id=message.chat.id,
                                   text='Отлично! Теперь можете ввести реквезиты партнера, и название его платежной системы')
            await reg_support.step3.set()
        except:
            await bot.send_message(chat_id=message.chat.id, text='Неудача')
            await state.finish()


@dp.message_handler(state=reg_support.step3, content_types='text')
async def get_reg_support33(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        number_support = message.text  # Реквезиты саппорта

        info_about_parthers = await state.get_data()
        channel_support = info_about_parthers['channel']  # Канал
        username_support = info_about_parthers['user_name']  # Юзернейм саппортов
        try:
            reg_utm_support(utm=channel_support, info=username_support, pay_info=number_support)  # Регистрация партнера
            reg_one_channel(channel_support)
            await bot.send_message(message.chat.id, text='Успешно')
        except:
            await bot.send_message(message.chat.id, text='Неудача!')

        await state.finish()


# ПРОСМОТР ВСЕХ ПАРТНЕРОВ
@dp.callback_query_handler(text='vienw_partners')  # ПРОСМОТР ВСЕХ ПАРТНЕРОВ
async def vienw_partners(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        q = cheach_all_par()
        sim = 0
        if q != []:  # Если зарегистрирован в базе для просмотра
            for i in q:
                s = (info(i[0]))
                sim += int(s)
                await bot.send_message(call.message.chat.id, f'Счетчик @{i[0]}: {s}')
        await bot.send_message(call.message.chat.id, f'Сумма всех счетчиков: {sim}')
    await bot.answer_callback_query(call.id)


# МЕНЮ НОВЫХ ПАРТНЕРОВ
@dp.callback_query_handler(text='reg_new_partners')  # МЕНЮ
async def check_all_partners(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        bat_a = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
        markup.add(bat_a)

        await bot.send_message(chat_id=call.message.chat.id, text='Перешлите сообщение от партнера',
                               reply_markup=markup)
        await partners12.step1.set()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=partners12.step1, content_types='text')
async def get_id_partners(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        try:
            id = message.forward_from.id
            await state.update_data(id_partners=id)
            await bot.send_message(chat_id=message.chat.id, text='ID получен! \n'
                                                                 'Введите имя канала слитно без пробелов, через @')
            await partners12.step2.set()

        except:
            await bot.send_message(chat_id=message.chat.id, text='У партнера скрытый аккаунт!\n'
                                                                 'Повторите попытку')


@dp.message_handler(state=partners12.step2, content_types='text')
async def get_channel_partners(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        chennel = message.text
        if chennel[0] == '@':
            await bot.send_message(chat_id=message.chat.id, text='Канал зарегистрирован')
            text_id = (await state.get_data())['id_partners']
            reg_partners_schet(channel=chennel[1:], id=text_id)
            await state.finish()

        else:
            await bot.send_message(chat_id=message.chat.id, text='Повторите попытку')


# НАСТРОЙКА ТРАФИКА
@dp.callback_query_handler(text='settings')
async def baza12(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        markup_traf = types.InlineKeyboardMarkup()
        bat_a = types.InlineKeyboardButton(text='ИЗМЕНИТЬ КАНАЛЫ⚙️', callback_data='change_trafik')
        markup_traf.add(bat_a)
        list = cheak_traf()
        await bot.send_message(call.message.chat.id, text=f'Список активный каналов на данный момент:\n\n'
                                                          f'1. {list[0][0]} - {list[0][1]}\n\n'
                                                          f'2. {list[1][0]} - {list[1][1]}\n\n'
                                                          f'3. {list[2][0]} - {list[2][1]}\n\n\n'
                                                          f'<b>Внимание! Первый по счету канал , должен быть обязательно с кино-тематикой</b>\n'
                                                          f'Для изменения жми кнопку', parse_mode='html',
                               reply_markup=markup_traf, disable_web_page_preview=True)
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text='change_trafik')  # Изменение каналов, на которые нужно подписаться
async def baza12342(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        bat_a = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
        markup.add(bat_a)

        await bot.send_message(call.message.chat.id,
                               text='Введите новый список каналов\n<b>ПЕРВЫЙ КАНАЛ ДОЛЖЕН БЫТЬ ОБЯЗАТЕЛЬНО С КИНО-ТЕМАТИКОЙ!</b>\n\n'
                                    'Список каналов вводи по примеру:\n\n'
                                    '@channel1 - https://t.me/joinchat/gQuo4v3mmUllNTJi\n'
                                    '@channel2 - https://t.me/joinchat/gQuo4v3mmUllNTJi\n'
                                    '@channel3 - https://t.me/joinchat/gQuo4v3mmUllNTJi\n\n'
                                    '<pre>Сначала вводи имя которое будет отобращаться в боте, через тире саму ссылку!</pre>',
                               parse_mode='html', reply_markup=markup, disable_web_page_preview=True)
        await reg_trafik.traf1.set()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=reg_trafik.traf1, content_types='text')
async def traf_obnovlenie(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        try:
            mas = message.text.split('\n')  # Массив с данными о каждом канале

            info_1 = (mas[0]).split('-')  # Инфо о первом канале
            info_2 = (mas[1]).split('-')  # Инфо о втором канале
            info_3 = (mas[2]).split('-')  # Инфо о третьем канале

            channe1_name = info_1[0][:-1]
            channel1_link = info_1[1][1:]

            channe2_name = info_2[0][:-1]
            channel2_link = info_2[1][1:]

            channe3_name = info_3[0][:-1]
            channel3_link = info_3[1][1:]

            obnovatrafika([channe1_name, channel1_link], [channe2_name, channel2_link],
                          [channe3_name, channel3_link])  # Внесение новых каналов в базу данных
            obnovlenie()
            await bot.send_message(chat_id=message.chat.id, text='Обновление успешно')
            await state.finish()

        except:
            await bot.send_message(chat_id=message.chat.id,
                                   text='Ошибка! Вы сделали что-то неправильное. ТЕбе необходимо снова зайти в админ панель и выбрать нужный пункт.'
                                        'Сообщение со списком каналом мне отсылать сейчас бессмыслено - я тебя буду игнорить, поэтому делай по новой все')
            await state.finish()


############################  REG ONE CHANNEL  ###################################
@dp.callback_query_handler(text='new_channel')  # АДМИН КНОПКА Добавления нового трафика
async def check(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        await bot.send_message(call.message.chat.id, 'Отправь название нового канала в формате\n'
                                                     '@name_channel')
        await reg.name.set()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=reg.name, content_types='text')
async def name_channel(message: types.Message, state: FSMContext):
    if message.chat.id in ADMIN_ID:
        check_dog = message.text[:1]
        if check_dog != '@':
            await bot.send_message(message.chat.id, 'Ты неправильно ввел имя группы!\nПовтори попытку!')
        else:
            reg_one_channel(message.text)
            await bot.send_message(message.chat.id, 'Регистрация успешна')
            await state.finish()


@dp.callback_query_handler(text='list_members')  # АДМИН КНОПКА ТРАФИКА
async def check(call: types.callback_query):
    if call.message.chat.id in ADMIN_ID:
        a = info_members()  # Вызов функции из файла sqlit
        await bot.send_message(call.message.chat.id, f'Количество пользователей: {a}')
    await bot.answer_callback_query(call.id)


########################  Рассылка  ################################
@dp.callback_query_handler(text='write_message')  # АДМИН КНОПКА Рассылка пользователям
async def check(call: types.callback_query, state: FSMContext):
    murkap = types.InlineKeyboardMarkup()
    bat0 = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
    murkap.add(bat0)
    await bot.send_message(call.message.chat.id, 'Перешли мне уже готовый пост и я разошлю его всем юзерам',
                           reply_markup=murkap)
    await st_reg.step_q.set()
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text='otemena', state='*')
async def otmena_12(call: types.callback_query, state: FSMContext):
    await bot.send_message(call.message.chat.id, 'Отменено')
    await state.finish()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=st_reg.step_q,
                    content_types=['text', 'photo', 'video', 'video_note', 'voice'])  # Предосмотр поста
async def redarkt_post(message: types.Message, state: FSMContext):
    await st_reg.st_name.set()
    murkap = types.InlineKeyboardMarkup()
    bat0 = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
    bat1 = types.InlineKeyboardButton(text='РАЗОСЛАТЬ', callback_data='send_ras')
    bat2 = types.InlineKeyboardButton(text='Добавить кнопки', callback_data='add_but')
    murkap.add(bat1)
    murkap.add(bat2)
    murkap.add(bat0)

    await message.copy_to(chat_id=message.chat.id)
    q = message
    await state.update_data(q=q)

    await bot.send_message(chat_id=message.chat.id, text='Пост сейчас выглядит так 👆', reply_markup=murkap)


# НАСТРОЙКА КНОПОК
@dp.callback_query_handler(text='add_but', state=st_reg.st_name)  # Добавление кнопок
async def addbutton(call: types.callback_query, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.send_message(call.message.chat.id, text='Отправляй мне кнопки по принципу Controller Bot')
    await st_reg.step_regbutton.set()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=st_reg.step_regbutton, content_types=['text'])  # Текст кнопок в неформате
async def redarkt_button(message: types.Message, state: FSMContext):
    arr3 = message.text.split('\n')
    murkap = types.InlineKeyboardMarkup()  # Клавиатура с кнопками

    massiv_text = []
    massiv_url = []

    for but in arr3:
        new_but = but.split('-')
        massiv_text.append(new_but[0][:-1])
        massiv_url.append(new_but[1][1:])
        bat9 = types.InlineKeyboardButton(text=new_but[0][:-1], url=new_but[1][1:])
        murkap.add(bat9)

    try:
        data = await state.get_data()
        mess = data['q']  # ID сообщения для рассылки

        await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=mess.message_id,
                               reply_markup=murkap)

        await state.update_data(text_but=massiv_text)  # Обновление Сета
        await state.update_data(url_but=massiv_url)  # Обновление Сета

        murkap2 = types.InlineKeyboardMarkup()  # Клавиатура - меню
        bat0 = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
        bat1 = types.InlineKeyboardButton(text='РАЗОСЛАТЬ', callback_data='send_ras')
        murkap2.add(bat1)
        murkap2.add(bat0)

        await bot.send_message(chat_id=message.chat.id, text='Теперь твой пост выглядит так☝', reply_markup=murkap2)


    except:
        await bot.send_message(chat_id=message.chat.id, text='Ошибка. Отменено')
        await state.finish()


# КОНЕЦ НАСТРОЙКИ КНОПОК


@dp.callback_query_handler(text='send_ras', state="*")  # Рассылка
async def fname_step(call: types.callback_query, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    data = await state.get_data()
    mess = data['q']  # Сообщения для рассылки

    murkap = types.InlineKeyboardMarkup()  # Клавиатура с кнопками
    try:  # Пытаемся добавить кнопки. Если их нету оставляем клаву пустой
        text_massiv = data['text_but']
        url_massiv = data['url_but']
        for t in text_massiv:
            for u in url_massiv:
                bat = types.InlineKeyboardButton(text=t, url=u)
                murkap.add(bat)
                break

    except:
        pass

    db = sqlite3.connect('server.db')
    sql = db.cursor()
    await state.finish()
    users = sql.execute("SELECT id FROM user_time").fetchall()
    bad = 0
    good = 0
    delit = 0
    await bot.send_message(call.message.chat.id,
                           f"<b>Всего пользователей: <code>{len(users)}</code></b>\n\n<b>Расслыка начата!</b>",
                           parse_mode="html")
    for i in users:
        await asyncio.sleep(0.03)
        try:
            await mess.copy_to(i[0], reply_markup=murkap)
            good += 1
        except (BotBlocked, ChatNotFound):
            try:
                delite_user(i[0])
                delit += 1

            except:
                pass
        except:
            bad += 1

    await bot.send_message(
        call.message.chat.id,
        "<u>Рассылка окончена\n\n</u>"
        f"<b>Всего пользователей:</b> <code>{len(users)}</code>\n"
        f"<b>Отправлено:</b> <code>{good}</code>\n"
        f"<b>Удалено пользователей:</b> <code>{delit}</code>\n"
        f"<b>Произошло ошибок:</b> <code>{bad}</code>",
        parse_mode="html"
    )
    await bot.answer_callback_query(call.id)
#########################################################
