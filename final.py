#-*-coding: utf-8-*-
import time
import telebot
import json
import os
import os.path
import re
from telebot import types


bot = telebot.TeleBot("1747737968:AAHQm4cfnw54SK2a6M6sUWU7G0ZyzgrJlWA")

user_fridge = {}
product = ""
amount = ""
unclickable_choices = []
list_of_choices = types.InlineKeyboardMarkup()

@bot.message_handler(commands=["start"])
def hello(message):
    if message.text == "/start":
        bot.send_message (message.from_user.id, "Привет! Этот бот сделает твое утро волшебным и замечательным \u2728" + "\n" + "Используй команду /help, чтобы узнать, что я умею делать \u263a\ufe0f")

@bot.message_handler(commands=["add"])
def add_fridge(message):
    if message.text == "/add":
        bot.send_message (message.from_user.id, "Добавим покупочки \U0001F4DD")
        bot.send_message (message.from_user.id, "Введите название продукта")
        bot.register_next_step_handler(message, u_product)

def u_product(message):
    global product
    if message.text.startswith("/"):
        bot.send_message (message.from_user.id,"Команды нельзя класть в холодильник, они невкусные, я точно знаю!")
        bot.send_message (message.from_user.id, "Введите название съедобного продукта \U0001F4DD")
        bot.register_next_step_handler(message, u_product)
    elif input_is_correct(message.text) == False:
        product = message.text.lower()
        bot.send_message (message.from_user.id,"Введите количество продукта, например, _100 кг_. Я измеряю в _шт, л, мл, кг, г_", parse_mode="Markdown")
        bot.register_next_step_handler(message, u_amount)
    else:
        bot.send_message (message.from_user.id,"Число нельзя положить в холодильник!")
        bot.send_message (message.from_user.id, "Введите название съедобного продукта \U0001F4DD")
        bot.register_next_step_handler(message, u_product)

def u_amount(message):
    global amount
    global user_fridge
    if input_is_correct(message.text):
        amount = message.text.lower()
        amount_converted = unit_converter(amount)
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text="Нет", callback_data="no")
        keyboard.add(key_no)
        question = "Хочешь добавить еще?"
        bot.send_message(message.from_user.id, text = question, reply_markup=keyboard)

        user_id = message.from_user.id
        user_file = str(user_id) + ".txt"
        check_file = os.path.exists(user_file)
        if check_file == True:
            f = open (user_file, "r", encoding = "utf-8")
            if os.stat(user_file).st_size!=0:
                user_fridge = json.load(f)
            f.close()
        if product in user_fridge:
            user_fridge[product][0] = float(user_fridge[product][0]) + float(amount_converted[0])
        else:
            user_fridge[product] = amount_converted
        if float(user_fridge[product][0])<=0:
            del user_fridge[product]

        again_f = open (user_file, "w", encoding = "utf-8")
        json.dump(user_fridge, again_f, ensure_ascii=False)
        again_f.close()
    else:
        bot.send_message(message.from_user.id, "Ты вводишь количество продукта в некорректном формате, и я не могу тебя понять \U0001F622 \nИспользуй следующий формат: _100 кг_. Я измеряю в _шт, л, мл, кг, г_ ", parse_mode="Markdown")
        bot.send_message(message.from_user.id, "Введите название продукта")
        bot.register_next_step_handler(message, u_product)
def input_is_correct(line):
    is_correct = False
    pattern = '-?[0-9]+\.?([0-9]+)? (шт|л|г|кг|мл)$'
    res = re.match(pattern, line)
    if res != None:
        is_correct = True
    return is_correct

@bot.message_handler(commands=["fridge"])
def add_fridge(message):
    if message.text == "/fridge":
        bot.send_message (message.from_user.id, "Давай откроем холодильник и посмотрим, что там есть \U0001F440")
        user_id = message.from_user.id
        user_file = str(user_id) + ".txt"
        check_file = os.path.exists(user_file)
        if check_file == True:
            with open (user_file, "r", encoding = "utf-8") as f:
                if os.stat(user_file).st_size==0:
                    bot.send_message(message.from_user.id, "Ой-ой, совсем пусто \U0001F622 Когда купишь чего-нибудь, используй команду /add")
                else:
                    user_file_content = json.load(f)
                    if user_file_content == {}:
                        bot.send_message(message.from_user.id, "Ой-ой, совсем пусто \U0001F622 Когда купишь чего-нибудь, используй команду /add")
                    else:
                        fr_products = ""
                        fr_text = ""
                        for key, value in user_file_content.items():

                            value_str = str(int(value[0])) + " " + value[1]
                            fr_products = fr_products + key + " " + value_str + "\n"
                            fr_text = "*На твоих полочках:* \n" + fr_products
                        bot.send_message(message.from_user.id, fr_text, parse_mode="Markdown")
        else:
            bot.send_message(message.from_user.id, "Ой-ой, совсем пусто \U0001F622 Когда купишь чего-нибудь, используй команду /add")


@bot.message_handler(commands=["recipes"])
def send_all_recipes(message):
    if message.text == "/recipes":
        list_of_all_recipes = types.InlineKeyboardMarkup()
        with open ("recipes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for key in data:
                callback_button = types.InlineKeyboardButton(text=key, callback_data=key)
                list_of_all_recipes.add(callback_button)

            bot.send_message(message.chat.id, "Список всех рецептов \U0001F35D", reply_markup=list_of_all_recipes)
@bot.message_handler(commands=["help"])
def send_all_recipes(message):
    if message.text == "/help":
        msg_text = "*Вот что я умею:*\n_/add_ – добавить продукты в холодильник\n_/fridge_ – открыть холодильник и посмотреть имеющиеся продукты\n_/recipes_ – посмотреть список всех рецептов, которые я знаю\n_/breakfast_ – подобрать завтрак по имеющимся продуктам\nПосле того, как ты приготовишь блюдо, я вычту те продукты, которые ты использовал"
        bot.send_message(message.from_user.id, msg_text, parse_mode="Markdown")
@bot.message_handler(commands=["breakfast"])
def send_recipes(message):
    if message.text == "/breakfast":
        breakfasts_are_available = False
        global unclickable_choices
        global list_of_choices
        unclickable_choices = []
        list_of_recipes = types.InlineKeyboardMarkup()
        list_of_choices = types.InlineKeyboardMarkup()
        f = open("recipes.json", "r", encoding="utf-8")
        user_id = message.from_user.id
        user_file = str(user_id) + ".txt"
        check_file = os.path.exists(user_file)
        if check_file == True:
            with open (user_file, "r", encoding = "utf-8") as input_base:
                if os.stat(user_file).st_size==0:
                    bot.send_message(message.from_user.id, "Ой-ой, в холодильнике совсем пусто \U0001F622 Когда купишь чего-нибудь, используй команду /add")
                else:
                    user_fridge = json.load(input_base)
                    recipe_data = json.load(f)
                    breakfasts_are_available = False
                    for key in recipe_data:
                        if compare_dict(user_fridge, recipe_data[key][0]):
                            callback_button = types.InlineKeyboardButton(text = key, callback_data = key)
                            another_callback_button = types.InlineKeyboardButton(text = key + " is preparing", callback_data = " " + key)
                            list_of_recipes.add(callback_button)
                            list_of_choices.add(another_callback_button)
                            unclickable_choices.append(" " + key)
                            breakfasts_are_available = True

        f.close()



        if breakfasts_are_available:
            ready_to_choose = types.InlineKeyboardMarkup()
            choose_yes = types.InlineKeyboardButton(text="Да \ud83d\ude0b", callback_data=" sure")
            ready_to_choose.add(choose_yes)
            choose_no = types.InlineKeyboardButton(text="Еще нет \U0001F622", callback_data=" notsure")
            ready_to_choose.add(choose_no)

            bot.send_message(message.chat.id, "Вот список доступных завтраков \U0001F373", reply_markup = list_of_recipes)
            time.sleep(6)
            bot.send_message(message.chat.id, "Ты решился приготовить что-то из этого?", reply_markup = ready_to_choose)

        else:
            bot.send_message(message.chat.id, "В твоем холодильнике пока не хватает продуктов для приготовления завтрака. Используй команду /add, чтобы пополнить холодильник. ")

def compare_dict(dict1, dict2): #эта функция сравнивает элементы двух словарей
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    is_in_dict = []
    if keys2.issubset(keys1):
        for key in list(keys2):
            if float(dict1[key][0]) >= float(dict2[key][0]):
                is_in_dict.append(True)
            else:
                is_in_dict.append(False)
    if False in is_in_dict or is_in_dict == []:
        return False
    else:
        return True

def unit_converter(my_unit): #эта функция переводит введенную величину в граммы и миллилитры, штуки не трогает

    units_coeff = {"л": 1000, "мл": 1, "кг": 1000, "г": 1}
    my_unit_splitted = my_unit.split()
    if my_unit_splitted[1] != "шт":
        my_unit_splitted[0] = float(my_unit_splitted[0]) * units_coeff[my_unit_splitted[1]]
        if my_unit_splitted[1] == "л":
            my_unit_splitted[1] = "мл"
        if my_unit_splitted[1] == "кг":
            my_unit_splitted[1] = "г"
    return my_unit_splitted

#КОЛБЭКЕР

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):


    if call.data == " notsure":
     bot.send_message(call.message.chat.id, "Я подожду...")
    if call.data == " sure":
     bot.send_message(call.message.chat.id, "Что? Когда ты выберешь блюдо, я вычту из твоего холодильника количество использованных продуктов", reply_markup = list_of_choices)

    for choice in unclickable_choices:
        if call.data == choice:

            user_file = str(call.from_user.id) + ".txt"
            f_rec = open ("recipes.json", "r", encoding="utf-8")
            f_us = open (user_file, "r", encoding = "utf-8")
            if os.stat(user_file).st_size==0:
                bot.send_message(call.from_user.id, "Ой-ой, в холодильнике совсем пусто \U0001F622 Когда купишь чего-нибудь, используй команду /add")
            else:
                user_file_fridge = json.load(f_us)
                rec_data = json.load(f_rec)
                not_exist_products = []
                for key in rec_data:
                    if call.data.strip() == key:
                        for prod in user_file_fridge:
                            for ingredient in rec_data[key][0]:
                                if prod == ingredient:
                                    user_fridge_prod_list = []
                                    user_fridge_prod = int(user_file_fridge[prod][0]) - int(rec_data[key][0][ingredient][0])
                                    user_fridge_prod_list.append(user_fridge_prod)
                                    user_fridge_prod_list.append(user_file_fridge[prod][1])
                                    user_file_fridge[prod] = user_fridge_prod_list
                                    if user_file_fridge[prod][0] <= 0:
                                        not_exist_products.append(prod)
                for product in not_exist_products:
                    del user_file_fridge[product]
                                             #когда равно 0, удаляем ключ
                bot.send_message(call.message.chat.id, "Готово \U0001F609")
            f_rec.close()
            f_us.close()
            with open (user_file, "w", encoding = "utf-8") as f:
                json.dump(user_file_fridge, f, ensure_ascii=False)


    if call.data == "no":
        bot.send_message(call.message.chat.id, "Окей")
    elif call.data == "yes":
        bot.send_message (call.from_user.id, "Введите название продукта")
        bot.register_next_step_handler(call.message, u_product)
    elif not call.data.startswith(" "):
        f = open("recipes.json", "r", encoding="utf-8")
        data = json.load(f)
        ingredients = ""
        description = ""
        for key, value in data[call.data][0].items():
            value_str = str(value[0]) + " " + value[1]
            ingredients = ingredients + key + " " + value_str + "\n"
        description = data[call.data][1]
        picture_path = "./pictures/" + data[call.data][2]
        picture = open(picture_path, 'rb')
        recipes_text = "*Ингредиенты:*\n" + ingredients + "\n" + "*Способ приготовления:* \n" + description
        bot.send_message(call.message.chat.id, recipes_text, parse_mode="Markdown")
        bot.send_photo(call.message.chat.id, picture)
        f.close()

bot.polling()
