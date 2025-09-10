from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from asyncio import sleep
from token import prod_token, test_token

admins = [640429258]

# -------------- PRINTING ID --------------
class UserIDLoggerMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        username = message.from_user.username if message.from_user.username else ("ID " + message.from_user.id)
        print(f"{username}\nmessage={message.text}\n")

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        username = callback_query.from_user.username if callback_query.from_user.username else ("ID " + callback_query.from_user.id)
        print(f"{username}\ncallback={callback_query.data}\n")
# -----------------------------------------

bot = Bot(token=test_token)
# bot = Bot(token=prod_token)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(UserIDLoggerMiddleware())
googletable = gspread.authorize(Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])).open_by_key('15u6HaCSljK_GY4P8PlqymgEW7iA8MkWcAYbq7TH9QHc')
gametable = googletable.get_worksheet(0)
timetable = googletable.get_worksheet(1)
usertable = googletable.get_worksheet(2)

class Form(StatesGroup):
    lang = State()
    name = State()
    menu = State()
    takeblock = State()
    selectday = State()
    mygames = State()
    giving_game = State()
    taking_game = State()
    selectday_back = State()

# ---------- SELECTING LANGUAGE -----------

@dp.message_handler()
async def start_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'id' not in data:
            data['id'] = message.from_user.id
        id = data['id']
    users = usertable.get_values()[1:]
    for user in users:
        if user[0] == str(id):
            async with state.proxy() as data:
                data['lang'] = user[2]
                data['name'] = user[1]
            await Form.menu.set()
            await askmenu(message, state)
            return
    await message.answer("Please choose an appropriate language.", reply_markup=lang_buttons())
    await Form.lang.set()

@dp.callback_query_handler()
async def main_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = callback_query.from_user.id
    if (callback_query.data == 'rus' or callback_query.data == 'eng'):
        lang_callback(callback_query, state)
    await bot.answer_callback_query(callback_query.id)

def lang_buttons():
    rus = InlineKeyboardButton("🇷🇺 Russian", callback_data='rus')
    eng = InlineKeyboardButton("🇺🇸 English", callback_data='eng')
    inline_kb = InlineKeyboardMarkup().row(rus, eng)
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.lang)
async def lang_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'rus' or callback_query.data == 'eng':
        async with state.proxy() as data:
            data['lang'] = callback_query.data
        await Form.name.set()
        await askname(callback_query.message, state)
    await bot.answer_callback_query(callback_query.id)

# ----------------- AUTH ------------------

@dp.message_handler(state=Form.name)
async def askname(message: types.Message, state: FSMContext):
    if ("@innopolis.university" in message.text or "@innolopis.ru" in message.text or "@innopolis.ru" in message.text or "@innopolis.mail.onmicrosoft.com" in message.text or "@innopolis-university.ru" in message.text or "@innopolis.onmicrosoft.com" in message.text):
        await checkuser(message, state)
    else:
        async with state.proxy() as data:
            if (data['lang'] == "rus"):
                await message.answer("Введите свою почту @innopolis.")
            else:
                await message.answer("Enter your @innopolis email.")

async def checkuser(message: types.Message, state: FSMContext):
    name = ""
    userid = -1
    with open('innousers.csv', encoding='utf-8') as f:
        for line in f:
            userid += 1
            line = line.split(',')
            if line[0] == message.text:
                name = line[1] + ", " + line[8] + "\n" + line[0]
                break
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            if (name == ""):
                await message.answer("❌ Пользователь не найден. Проверьте правильность ввода почты.\n\nЕсли вы считаете, что произошла ошибка, свяжитесь с @gleb_pp")
            else:
                await message.answer("Это вы?\n" + name, reply_markup=user_check_buttons(userid, data['lang']))
        else:
            if (name == ""):
                await message.answer("❌ User not found. Make sure your mail is entered correctly.\n\nIf you think there has been an error, contact @gleb_pp")
            else:
                await message.answer("Is it you\n" + name, reply_markup=user_check_buttons(userid, data['lang']))

def user_check_buttons(userid, lang):
    if (lang == "rus"):
        yes = InlineKeyboardButton("Да", callback_data=('user_yes' + str(userid)))
        no = InlineKeyboardButton("Нет", callback_data='user_no') 
    else:
        yes = InlineKeyboardButton("Yes", callback_data='user_yes' + str(userid))
        no = InlineKeyboardButton("No", callback_data='user_no')
    inline_kb = InlineKeyboardMarkup().row(yes, no)
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.name)
async def user_check_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if ("user_yes" in callback_query.data):
        async with state.proxy() as data:
            userid = int(callback_query.data[8:])
            i = -1
            with open('innousers.csv', encoding='utf-8') as f:
                for line in f:
                    i += 1
                    if (i == userid):
                        line = line.split(',')
                        data['name'] = line[1] + ", " + line[8]
                        break
            print(data['name'])
            row_index = len(usertable.col_values(3)) + 1
            usertable.update(f'A{row_index}:C{row_index}', [[str(data['id']), data['name'], data['lang']]])
        await Form.menu.set()
        await askmenu(callback_query.message, state)
    elif (callback_query.data == "user_no"):
        await askname(callback_query.message, state)
    elif (callback_query.data == 'rus' or callback_query.data == 'eng'):
        await lang_callback(callback_query, state)
    await bot.answer_callback_query(callback_query.id)

# ----------------- MENU ------------------

@dp.message_handler(state=Form.menu)
async def askmenu(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            await message.answer("Вы находитесь в меню", reply_markup=menu_buttons(data['lang'], data['id']))
        else:
            await message.answer("You are in the menu now", reply_markup=menu_buttons(data['lang'], data['id']))

def menu_buttons(lang, user):
    if (lang == "rus"):
        games = InlineKeyboardButton("🖐 Мои игры", callback_data='mygames')
        newgame = InlineKeyboardButton("🎲 Взять новую игру", callback_data='newgame')
        lang = InlineKeyboardButton("🌐 Сменить язык", callback_data='lang')
    else:
        games = InlineKeyboardButton("🖐 My games", callback_data='mygames')
        newgame = InlineKeyboardButton("🎲 Take a new game", callback_data='newgame')
        lang = InlineKeyboardButton("🌐 Switch the language", callback_data='lang')
    inline_kb = InlineKeyboardMarkup().add(games).add(newgame).add(lang)
    if user in admins:
        adm1 = InlineKeyboardButton("🔙", callback_data='admin_take')
        adm2 = InlineKeyboardButton("⬆️", callback_data='admin_give')
        adm3 = InlineKeyboardButton("🔜", callback_data='admin_plans')
        inline_kb.row(adm1, adm2, adm3)
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.menu)
async def menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == "mygames"):
        await Form.mygames.set()
        await mygames(callback_query.message, state)
    elif (callback_query.data == "newgame"):
        await ask_game_lang(callback_query.message, state)
    elif (callback_query.data == "lang"):
        await change_lang(callback_query.message, state)
    elif (callback_query.data == "game_rus"):
        async with state.proxy() as data:
            data['game_lang'] = 'rus'
        await Form.takeblock.set()
        await askblock(callback_query.message, state)
    elif (callback_query.data == "game_eng"):
        async with state.proxy() as data:
            data['game_lang'] = 'eng'
        await Form.takeblock.set()
        await askblock(callback_query.message, state)
    elif (callback_query.data == "any_game"):
        async with state.proxy() as data:
            data['game_lang'] = 'any'
        await Form.takeblock.set()
        await askblock(callback_query.message, state)
    elif (callback_query.data == 'admin_give'):
        games = gametable.get_values()
        reserved = [i for i in range(len(games)) if games[i][3] == 'reserved']
        mess = 'Bookings\n\n'
        for i in reserved:
            mess += games[i][1] + '\n' + games[i][4] + '\n' + games[i][5] + '\n\n'
        await Form.giving_game.set()
        await callback_query.message.answer(mess, reply_markup=admin_give_buttons())
    elif (callback_query.data == 'admin_take'):
        games = gametable.get_values()
        onhand = [i for i in range(len(games)) if games[i][3] == 'on hand']
        mess = 'On-hand games\n\n'
        for i in onhand:
            mess += games[i][1] + '\n' + games[i][4] + '\nUntil ' + games[i][6] + '\n\n'
        await Form.taking_game.set()
        await callback_query.message.answer(mess, reply_markup=admin_take_buttons())
    elif (callback_query.data == 'admin_plans'):
        mess = "Future meetings\n\n"
        table = timetable.get_values()
        for slot in table[1:]:
            if slot[2] != '—':
                mess += slot[0] + ", " + slot[1] + '\n' + slot[3] + '\n\n'
        await callback_query.message.answer(mess, reply_markup=admin_cansel_meeting_buttons(table))
    elif ('admin_cancel' in callback_query.data):
        row_index = int(callback_query.data[12:]) + 1
        slot = timetable.row_values(row_index)
        if (slot[2] == "—"):
            await callback_query.message.answer("The reservation is not found")
            return
        await bot.send_message(slot[2], "Бронирование " + slot[0] + ", " + slot[1] + " отменено администратором.\n―――――――――――\n" + "Reservation on " + slot[0] + ", " + slot[1] + " canceled by the administrator.")
        timetable.update("C" + str(row_index), [['—']])
        games = gametable.get_values()
        for i in range(1, len(games)):
            row_index = i + 1
            if games[i][5] == (slot[0] + ", " + slot[1]):
                gametable.update(f'D{row_index}:H{row_index}', [["free", "", "" , "", ""]])
                break
            elif games[i][9] == (slot[0] + ", " + slot[1]):
                gametable.update('J' + str(row_index), [[""]])
                break
        await callback_query.message.answer("The reservation was cancelled")
    else:
        async with state.proxy() as data:
            if (data['lang'] == 'eng' and callback_query.data == 'rus') or (data['lang'] == 'rus' and callback_query.data == 'eng'):
                await change_lang(callback_query.message, state)

    await bot.answer_callback_query(callback_query.id)

# ------------ CANSEL MEETING ------------

def admin_cansel_meeting_buttons(table):
    inline_kb = InlineKeyboardMarkup()
    for i in range(1, len(table)):
        slot = table[i]
        if slot[2] != '—':
            inline_kb.add(InlineKeyboardButton('cancel: ' + slot[0] + ", " + slot[1], callback_data=('admin_cancel' + str(i))))
    return inline_kb

# ------------- GIVING GAME --------------

def admin_give_buttons():
    games = gametable.get_values()
    reserved = [i for i in range(len(games)) if games[i][3] == 'reserved']
    inline_kb = InlineKeyboardMarkup()
    for i in reserved:
        inline_kb.add(InlineKeyboardButton(games[i][1] + ' [' + games[i][0] + ']', callback_data=('admin_give_game_' + str(i))))
    inline_kb.add(InlineKeyboardButton('↩️ Back to main menu', callback_data='tomenu'))
    return inline_kb

def remove_timeslot(meeting):
    day = meeting[:(meeting.find(','))]
    slot = meeting[(meeting.find(',') + 2):]
    row_ind = 1
    for timeslot in timetable.get_values():
        if timeslot[0] == day and timeslot[1] == slot:
            timetable.update("C" + str(row_ind), [['—']])
            break
        row_ind += 1

@dp.callback_query_handler(lambda c: c.data, state=Form.giving_game)
async def admin_give_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if ('admin_give_game_' in callback_query.data):
        games = gametable.get_values()
        gameid = int(callback_query.data[16:])
        if (games[gameid][3] == 'reserved'):
            row_index = gameid + 1
            async with state.proxy() as data:
                data['game_given'] = str(row_index)
            await callback_query.message.answer('How many days does the person need?')
        else:
            await callback_query.message.answer('The game is not reserved')
    elif (callback_query.data == 'tomenu'):
        await Form.menu.set()
        await askmenu(callback_query.message, state)
    elif ('admin_take_game_' in callback_query.data):
        await Form.taking_game.set()
        await admin_take_callback(callback_query, state)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(state=Form.giving_game)
async def admin_give_days(message: types.Message, state: FSMContext):
    games = gametable.get_values()
    async with state.proxy() as data:
        gameid = int(data['game_given']) - 1
    if (games[gameid][3] != 'reserved'):
        await message.answer('The game is not reserved')
        await Form.menu.set()
        await askmenu(message, state)
    try:
        a = int(message.text)
        if (a > 7 or a < 1):
            await message.answer('Cannot give game on more than 7 days')
        else:
            remove_timeslot(games[gameid][5])
            async with state.proxy() as data:
                gg = data['game_given']
                gametable.update(f'D{gg}:G{gg}', [['on hand', games[int(gg) - 1][4], dateafter(0), dateafter(a)]])
            await message.answer('Game is successfully given')
            await bot.send_message(games[gameid][7], "*Игра выдана*\n" + games[gameid][1] + "\nДо " + dateafter(a) +  "\n―――――――――――\n" + "*Game given*\n" + game_name(games[gameid], 'eng') + "\nUntil " + dateafter(a), parse_mode='Markdown')
            await Form.menu.set()
            await askmenu(message, state)
    except:
        await message.answer('This is not a number of days')
        await Form.menu.set()
        await askmenu(message, state)

# ------------ TAKING GAME ----------------

def admin_take_buttons():
    games = gametable.get_values()
    reserved = [i for i in range(len(games)) if games[i][3] == 'on hand']
    inline_kb = InlineKeyboardMarkup()
    for i in reserved:
        inline_kb.add(InlineKeyboardButton(games[i][1], callback_data=('admin_take_game_' + str(i))))
    inline_kb.add(InlineKeyboardButton('↩️ Back to main menu', callback_data='tomenu'))
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.taking_game)
async def admin_take_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if ('admin_take_game_' in callback_query.data):
        games = gametable.get_values()
        gameid = int(callback_query.data[16:])
        if (games[gameid][3] != 'on hand'):
            await callback_query.message.answer('Game is not on hand')
            await Form.menu.set()
            await askmenu(callback_query.message, state)
            return
        row_index = gameid + 1
        person = games[gameid][7]
        if len(games[gameid]) >= 10 and games[gameid][9] != '':
            remove_timeslot(games[gameid][9])
            gametable.update("J" + str(row_index), [['']])
        gametable.update(f'D{row_index}:H{row_index}', [["free", '', '', '', '']])
        await callback_query.message.answer('Game is successfully taken back')
        await bot.send_message(int(person), "*Игра возвращена*\n" + games[gameid][1] + "\n―――――――――――\n" + "*The game is back*\n" + game_name(games[gameid], 'eng'), parse_mode='Markdown')
        await Form.menu.set()
        await askmenu(callback_query.message, state)
    elif (callback_query.data == 'tomenu'):
        await Form.menu.set()
        await askmenu(callback_query.message, state)
    elif ('admin_give_game_' in callback_query.data):
        await Form.giving_game.set()
        await admin_give_callback(callback_query, state)
    await bot.answer_callback_query(callback_query.id)

# ------------ CHANGING LANG --------------

async def change_lang(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            await message.answer("Your language is English now.")
            data['lang'] = 'eng'
            # поменять язык в таблице
        else:
            await message.answer("Язык переключён на русский.")
            data['lang'] = 'rus'
            # поменять язык в таблице

# -------------- GAME LANG ----------------

async def ask_game_lang(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            await message.answer("Игры на каких языках вас интересуют?", reply_markup=game_lang_buttons(data['lang']))
        else:
            await message.answer("What languages are you interested in playing games in?", reply_markup=game_lang_buttons(data['lang']))

def game_lang_buttons(lang):
    if (lang == "rus"):
        rus = InlineKeyboardButton("🇷🇺 Русский", callback_data='game_rus')
        eng = InlineKeyboardButton("🇺🇸 Английский", callback_data='game_eng')
        any = InlineKeyboardButton("🌐 Не имеет значения", callback_data='any_game')
        inline_kb = InlineKeyboardMarkup().row(rus, eng).add(any)
    else:
        eng = InlineKeyboardButton("🇺🇸 English", callback_data='game_eng')
        rus = InlineKeyboardButton("🇷🇺 Russian", callback_data='game_rus')
        any = InlineKeyboardButton("🌐 Doesn't matter", callback_data='any_game')
        inline_kb = InlineKeyboardMarkup().row(eng, rus).add(any)
    return inline_kb

# ----------- SELECTING BLOCK -------------

@dp.message_handler(state=Form.takeblock)
async def askblock(message: types.Message, state: FSMContext):
    block = {"rus":'БЛОК', 'eng':"BLOCK"}
    table = gametable.get_values()[1:]
    for i in range(len(table)):
        if message.text in table[i] and table[i][3] == "free":
            async with state.proxy() as data:
                data['game'] = str(i + 1)
            await Form.selectday.set()
            await selectday(message, state)
            return
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            send = '"▪️" — игра свободна\n"▫️" — игра на руках\n\n*БЛОК 1*\n'
        else:
            send = '"▪️" — the game is available\n"▫️" — the game is unavailable\n\n*BLOCK 1*\n'
        bl = 1
        for game in table:
            if (int(game[0]) > bl):
                bl += 1
                send += "\n*" + block[data['lang']] + " " + str(bl) + "*\n"
            if (data['game_lang'] == 'rus' and game[2] != "EN") or (data['game_lang'] == 'eng' and game[2] != "RU") or (data['game_lang'] == 'any'):
                if (game[3] == "free"):
                    send += "▪️ " + game_name(game, data['lang']) + '\n'
                else:
                    send += "▫️ " + game_name(game, data['lang']) + '\n'

        await message.answer(send, parse_mode='Markdown', reply_markup=game_blocks_buttons(int(max(gametable.col_values(1)[1:])), data['lang']))

def game_name(game, lang):
    if (lang == "eng" and game[2] == "RU, EN"):
        return game[8]
    else:
        return game[1]

def game_blocks_buttons(n, lang):
    block = {"rus":'БЛОК ', 'eng':"BLOCK "}
    inline_kb = InlineKeyboardMarkup()
    buttons = []
    for b in range(1, n + 1):
        buttons.append(InlineKeyboardButton(block[lang] + str(b), callback_data="block" + str(b)))
        if len(buttons) > 2:
            inline_kb.row(buttons[0], buttons[1], buttons[2])
            buttons = []
    if len(buttons) == 1:
        inline_kb.add(buttons[0])
    else:
        inline_kb.row(buttons[0], buttons[1])
    if (lang == "rus"):
        inline_kb.add(InlineKeyboardButton('↩️ Назад в меню', callback_data='tomenu'))
    else:
        inline_kb.add(InlineKeyboardButton('↩️ Back to main menu', callback_data='tomenu'))
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.takeblock)
async def game_blocks_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == 'tomenu'):
        await Form.menu.set()
        await askmenu(callback_query.message, state)
    elif ("block" in callback_query.data):
        async with state.proxy() as data:
            data['block'] = str(callback_query.data)[5:]
        await askgame(callback_query.message, state)
    elif ("game" in callback_query.data):
        async with state.proxy() as data:
            data['game'] = callback_query.data[4:]
        await Form.selectday.set()
        await selectday(callback_query.message, state)
    await bot.answer_callback_query(callback_query.id)

# ------------ SELECTING GAME -------------

async def askgame(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            await message.answer("Выберите игру из списка ниже", reply_markup=game_buttons(data['game_lang'], data['block'], data['lang']))
        else:
            await message.answer("Select a game from the list below", reply_markup=game_buttons(data['game_lang'], data['block'], data['lang']))

def game_buttons(game_lang, block, lang):
    table = gametable.get_values()
    inline_kb = InlineKeyboardMarkup()
    for i in range(1, len(table)):
        if (table[i][0] == block):
            if (game_lang == 'rus' and table[i][2] != "EN") or (game_lang == 'eng' and table[i][2] != "RU") or (game_lang == 'any'):
                if (table[i][3] == "free"):
                    inline_kb.add(InlineKeyboardButton(game_name(table[i], lang), callback_data=('game' + str(i))))
    if (lang == 'rus'):
        inline_kb.add(InlineKeyboardButton('↩️ Назад в меню', callback_data='tomenu'))
    else:
        inline_kb.add(InlineKeyboardButton('↩️ Back to main menu', callback_data='tomenu'))
    return inline_kb

# ------------ APPROVING GAME -------------

@dp.message_handler(state=Form.selectday)
async def selectday(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            await message.answer('Вы выбрали игру "' + game_name(gametable.get_values()[int(data['game'])], 'rus') + '".\nВыберите день, когда вам будет удобно её получить', reply_markup=day_buttons('rus'))
        else:
            await message.answer('You chose the game "' + game_name(gametable.get_values()[int(data['game'])], 'eng') + '".\nChoose a day when it is convenient for you to pick it up', reply_markup=day_buttons('eng'))

def dateafter(days):
    date = datetime.today() + timedelta(days=days)
    day = str(date.day)
    if len(day) == 1:
        day = "0" + day
    month = str(date.month)
    year = str(date.year)
    if len(month) == 1:
        month = '0' + month
    return (day + "." + month + '.' + year)

def day_buttons(lang):
    table = timetable.get_values()[1:]
    potential = [dateafter(i) for i in range(100)]
    inline_kb = InlineKeyboardMarkup()
    buttons = []
    for i in range(len(potential)):
        for slot in table:
            if slot[0] == potential[i] and slot[2] == "—":
                if (lang == "rus"):
                    buttons.append(InlineKeyboardButton(potential[i], callback_data=('day' + potential[i])))
                else:
                    buttons.append(InlineKeyboardButton(potential[i], callback_data=('day' + potential[i])))
                if len(buttons) == 3:
                    inline_kb.row(buttons[0], buttons[1], buttons[2])
                    buttons = []
                break
    if len(buttons) == 1:
        inline_kb.add(buttons[0])
    elif len(buttons) == 2:
        inline_kb.row(buttons[0], buttons[1])
    if (lang == 'rus'):
        inline_kb.add(InlineKeyboardButton('↩️ Назад к выбору игр', callback_data=('tomenu')))
    else:
        inline_kb.add(InlineKeyboardButton('↩️ Back to game selection', callback_data=('tomenu')))
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.selectday)
async def day_timeslot_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == 'tomenu'):
        await Form.takeblock.set()
        await askblock(callback_query.message, state)
    elif ("day" in callback_query.data):
        async with state.proxy() as data:
            data['day'] = str(callback_query.data)[3:]
            if data['lang'] == 'rus':
                await callback_query.message.answer("Вы выбрали " + data['day'] + ".\nВыберите удобный тайм слот.", reply_markup=time_buttons('rus', data['day']))
            else:
                await callback_query.message.answer("You chose " + data['day'] + ".\nChoose a convenient time slot.", reply_markup=time_buttons('eng', data['day']))
    elif ("button" in callback_query.data):
        success = False
        async with state.proxy() as data:
            data['timeslot'] = str(callback_query.data)[6:]
            row_index = int(data['game']) + 1
            if gametable.get("D" + str(row_index), [])[0][0] == "free":
                gametable.update(f'D{row_index}:H{row_index}', [["reserved", data['name'], data['day'] + ", " + str(timetable.get("B" + data['timeslot'], [])[0][0]) , "", callback_query.from_user.id]])
                timetable.update('C' + data['timeslot'], [[str(callback_query.from_user.id)]])
                for ad in admins:
                    await bot.send_message(ad, "Новая запись:\n" + data['name'] + "\n" + data['day'] + ", " + str(timetable.get("B" + data['timeslot'], [])[0][0]))
                if data['lang'] == 'rus':
                    await callback_query.message.answer("Вы успешно записаны.")
                else:
                    await callback_query.message.answer("You have been successfully enrolled.")
                success = True
            else:
                if data['lang'] == 'rus':
                    await callback_query.message.answer("К сожалению, игра недоступна.")
                else:
                    await callback_query.message.answer("Unfortunately, the game is unavailable.")
        if (success):
            await Form.mygames.set()
            await mygames(callback_query.message, state)
        else:
            await Form.menu.set()
            await askmenu(callback_query.message, state)
    await bot.answer_callback_query(callback_query.id)

def time_buttons(lang, day):
    table = timetable.get_values()
    inline_kb = InlineKeyboardMarkup()
    buttons = []
    for slot in range(1, len(table)):
        if table[slot][0] == day and table[slot][2] == '—':
            buttons.append(InlineKeyboardButton(table[slot][1], callback_data=('button' + str(slot + 1))))
            if (len(buttons) > 1):
                inline_kb.row(buttons[0], buttons[1])
                buttons = []
    if (len(buttons) == 1):
        inline_kb.add(buttons[0])
    if (lang == "rus"):
        inline_kb.add(InlineKeyboardButton('↩️ Назад к выбору игр', callback_data=('tomenu')))
    else:
        inline_kb.add(InlineKeyboardButton('↩️ Back to game selection', callback_data=('tomenu')))
    return inline_kb

# --------------- MY GAMES ----------------

async def mygames(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        games = gametable.get_values()
        onhand = [i for i in range(1, len(games)) if games[i][3] == "on hand" and games[i][4] == data['name']]
        reserved = [i for i in range(1, len(games)) if games[i][3] == "reserved" and games[i][4] == data['name']]
        if (data['lang'] == "rus"):
            mess = "*Игры на руках*\n"
            if (len(onhand) == 0):
                mess += "У вас нет игр на руках.\n"
            else:
                for i in onhand:
                    mess += "▫️ " + games[i][1] + ",\nдо " + games[i][6] + "\n"
                    if len(games[i]) >= 10 and games[i][9] != '':
                        mess += "Возврат запланирован на " + games[i][9] + "\n"
            mess += "\n*Зарезервированные игры*\n"
            if len(reserved) == 0:
                mess += "У вас нет зарезервированных игр.\n"
            else:
                for i in reserved:
                    mess += "▫️ " + games[i][1] + ",\nзабрать " + games[i][5] + "\n"
            if (len(onhand) > 0) or (len(reserved) > 0):
                mess += "\nНажмите на игру ниже, если вы хотите вернуть игру (🔙) или отменить бронирование (✖️):"
        else:
            mess = "*Games on hand*\n"
            if (len(onhand) == 0):
                mess += "You don't have any games on your hands.\n"
            else:
                for i in onhand:
                    mess += "▫️ " + games[i][1] + ",\nuntil " + games[i][6] + "\n"
                    if len(games[i]) >= 10 and games[i][9] != '':
                        print(games[i])
                        date = games[i][9]
                        mess += "The return is scheduled for " + date + "\n"
            mess += "\n*Reserved games*\n"
            if len(reserved) == 0:
                mess += "You don't have any reserved games.\n"
            else:
                for i in reserved:
                    date = games[i][5]
                    mess += "▫️ " + game_name(games[i], 'eng') + ",\npick up on " + date + "\n"
            if (len(onhand) > 0) or (len(reserved) > 0):
                mess += "\nClick on the game below if you would like to return the game (🔙) or cancel your reservation (✖️):"
        await message.answer(mess, parse_mode='Markdown', reply_markup=mygames_buttons(onhand, reserved, data['lang']))

def mygames_buttons(onhand, reserved, lang):
    games = gametable.get_values()
    buttons = []
    for i in onhand:
        buttons.append(InlineKeyboardButton("🔙 " + game_name(games[i], lang), callback_data=('back' + str(i))))
    for i in reserved:
        buttons.append(InlineKeyboardButton("✖️ " + game_name(games[i], lang), callback_data=('reserv' + str(i))))
    buttons.append(InlineKeyboardButton('↩️ Назад в меню' if lang == 'rus' else '↩️ Back to main menu', callback_data=('tomenu')))
    inline_kb = InlineKeyboardMarkup()
    for but in buttons:
        inline_kb.add(but)
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.mygames)
async def day_timeslot_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == 'tomenu'):
        await Form.menu.set()
        await askmenu(callback_query.message, state)
    elif ("back" in callback_query.data):
        async with state.proxy() as data:
            data['game_back'] = callback_query.data[4:]
        await Form.selectday_back.set()
        await selectday_back(callback_query.message, state)
    elif ("reserv" in callback_query.data):
        games = gametable.get_values()
        gameid = int(callback_query.data[6:])
        async with state.proxy() as data:
            if data['lang'] == 'rus':
                if games[gameid][3] == 'reserved':
                    await callback_query.message.answer('Вы уверены, что хотите отменить бронирование игры?', reply_markup=cancel_reserve_buttons(data['lang'], gameid))
                elif games[gameid][3] == 'on hand':
                    await callback_query.message.answer('Игра уже выдана.')
                    await mygames(callback_query.message, state)
                else:
                    await callback_query.message.answer('Бронирование не найдено.')
                    await mygames(callback_query.message, state)
            else:
                if games[gameid][3] == 'reserved':
                    await callback_query.message.answer('Are you sure you want to cancel your game reservation?', reply_markup=cancel_reserve_buttons(data['lang'], gameid))
                elif games[gameid][3] == 'on hand':
                    await callback_query.message.answer('The game has already been given away.')
                    await mygames(callback_query.message, state)
                else:
                    await callback_query.message.answer('Reservation not found.')
                    await mygames(callback_query.message, state)
    elif ('cancel_yes' in callback_query.data):
        games = gametable.get_values()
        gameid = int(callback_query.data[10:])
        async with state.proxy() as data:
            if games[gameid][3] == 'reserved':
                row_index = gameid + 1
                day = games[gameid][5][:(games[gameid][5].find(','))]
                slot = games[gameid][5][(games[gameid][5].find(',') + 2):]
                remove_timeslot(games[gameid][5])
                gametable.update(f'D{row_index}:H{row_index}', [["free", '', '', "", '']])
                for ad in admins:
                    await bot.send_message(ad, "Бронирование отменено.\n" + day + ", " + slot)
                await callback_query.message.answer('Бронирование отменено.' if data['lang'] == 'rus' else 'Reservation has been canceled.')
                await mygames(callback_query.message, state)
            elif games[gameid][3] == 'on hand':
                await callback_query.message.answer('Игра уже выдана.' if data['lang'] == 'rus' else 'The game has already been given away.')
                await mygames(callback_query.message, state)
            else:
                await callback_query.message.answer('Бронирование не найдено.' if data['lang'] == 'rus' else 'Reservation not found.')
                await mygames(callback_query.message, state)
    elif ('cancel_no' in callback_query.data):
        await mygames(callback_query.message, state)

    await bot.answer_callback_query(callback_query.id)

def cancel_reserve_buttons(lang, game):
    yes = InlineKeyboardButton("Да" if lang == 'rus' else "Yes", callback_data=('cancel_yes' + str(game)))
    no = InlineKeyboardButton("Нет" if lang == 'rus' else "No", callback_data=('cancel_no' + str(game)))
    inline_kb = InlineKeyboardMarkup().row(yes, no)
    return inline_kb

# -------- RETURNING GAME BACK ------------

@dp.message_handler(state=Form.selectday_back)
async def selectday_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if (data['lang'] == "rus"):
            await message.answer('Вы хотите вернуть игру "' + game_name(gametable.get_values()[int(data['game_back'])], 'rus') + '".\nВыберите день, когда вам будет удобно её вернуть', reply_markup=day_buttons_back('rus'))
        else:
            await message.answer('You want to get back the game "' + game_name(gametable.get_values()[int(data['game_back'])], 'eng') + '".\nChoose a day when it will be convenient for you to return it', reply_markup=day_buttons_back('eng'))

def day_buttons_back(lang):
    potential = [dateafter(i) for i in range(100)]
    table = timetable.get_values()[1:]
    inline_kb = InlineKeyboardMarkup()
    buttons = []
    for i in range(len(potential)):
        for slot in table:
            if slot[0] == str(potential[i]) and slot[2] == "—":
                if (lang == 'rus'):
                    buttons.append(InlineKeyboardButton(potential[i], callback_data=('day' + potential[i])))
                else:
                    buttons.append(InlineKeyboardButton(potential[i], callback_data=('day' + potential[i])))
                if len(buttons) == 3:
                    inline_kb.row(buttons[0], buttons[1], buttons[2])
                    buttons = []
                break
    if len(buttons) == 1:
        inline_kb.add(buttons[0])
    elif len(buttons) == 2:
        inline_kb.row(buttons[0], buttons[1])
    inline_kb.add(InlineKeyboardButton('↩️ Назад в меню' if lang == 'rus' else '↩️ Back to main menu', callback_data=('tomenu')))
    return inline_kb

@dp.callback_query_handler(lambda c: c.data, state=Form.selectday_back)
async def day_timeslot_back_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == 'tomenu'):
        await Form.menu.set()
        await askmenu(callback_query.message, state)
    elif ("day" in callback_query.data):
        async with state.proxy() as data:
            data['day'] = str(callback_query.data)[3:]
            if data['lang'] == 'rus':
                await callback_query.message.answer("Вы выбрали " + data['day'] + ".\nВыберите удобный тайм слот.", reply_markup=time_buttons_back('rus', data['day']))
            else:
                await callback_query.message.answer("You chose " + data['day'] + ".\nChoose a convenient time slot.", reply_markup=time_buttons_back('eng', data['day']))
    elif ("button" in callback_query.data):
        flag = 0
        async with state.proxy() as data:
            data['timeslot'] = str(callback_query.data)[6:]
            gameid = int(data['game_back'])
            row_index = gameid + 1
            games = gametable.get_values()
            if games[gameid][3] == "on hand" and games[gameid][7] == str(data['id']):
                if len(games[7]) >= 10 and games[7][9] != "":
                    remove_timeslot(games[gameid][9])
                timetable.update('C' + data['timeslot'], [[str(callback_query.from_user.id)]])
                gametable.update('J' + str(row_index), [[data['day'] + ", " + str(timetable.get("B" + data['timeslot'], [])[0][0])]])
                for ad in admins:
                    await bot.send_message(ad, "Новая запись:\n" + data['name'] + "\n" + data['day'] + ", " + str(timetable.get("B" + data['timeslot'], [])[0][0]))
                if data['lang'] == 'rus':
                    await callback_query.message.answer("Вы успешно записаны.")
                else:
                    await callback_query.message.answer("You have been successfully enrolled.")
                flag = 1
            else:
                if data['lang'] == 'rus':
                    await callback_query.message.answer("У вас нет такой игры.")
                else:
                    await callback_query.message.answer("You don't have this game")
        if (flag):
            await Form.mygames.set()
            await mygames(callback_query.message, state)
        else:
            await Form.menu.set()
            await askmenu(callback_query.message, state)
    await bot.answer_callback_query(callback_query.id)

def time_buttons_back(lang, day):
    table = timetable.get_values()
    inline_kb = InlineKeyboardMarkup()
    buttons = []
    for slot in range(1, len(table)):
        if table[slot][0] == day and table[slot][2] == '—':
            buttons.append(InlineKeyboardButton(table[slot][1], callback_data=('button' + str(slot + 1))))
            if (len(buttons) > 1):
                inline_kb.row(buttons[0], buttons[1])
                buttons = []
    if len(buttons) == 1:
        inline_kb.add(buttons[0])
    if (lang == "rus"):
        inline_kb.add(InlineKeyboardButton('↩️ Назад в меню', callback_data=('tomenu')))
    else:
        inline_kb.add(InlineKeyboardButton('↩️ Back to the main menu', callback_data=('tomenu')))
    return inline_kb

# ------------- NOTIFICATIONS -------------

# async def notify():
    # while True
    #   просчитываем, сколько времени до 30 / 60
    #   спим столько времени
    #   проверяем слоты в таблице и отправляем сообщения

if __name__ == '__main__':
    # dp.loop.create_task(notify())
    executor.start_polling(dp, skip_updates=True)
