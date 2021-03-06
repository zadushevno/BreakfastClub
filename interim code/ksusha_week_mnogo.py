#-*-coding: utf-8-*-
import telebot
import json
import os
import os.path
from telebot import types

bot = telebot.TeleBot("1747737968:AAHQm4cfnw54SK2a6M6sUWU7G0ZyzgrJlWA")

user_fridge = {}
product = ""
amount = ""
unclickable_choices = []

@bot.message_handler(commands=["start"])
def hello(message):
    if message.text == "/start":
        bot.send_message (message.from_user.id, 'Привет! Этот бот сделает твое утро волшебным и замечательным! Выбери команду /add, чтобы добавить продукты в холодильник. Команду /fridge, чтобы посмотреть, что в нем есть. Команжду /breakfast, чтобы я мог предложить тебе рецепты :)')

@bot.message_handler(commands=["add"])    
def add_fridge(message):
    if message.text == "/add":
        bot.send_message (message.from_user.id, "Добавим покупочки!")
        bot.send_message (message.from_user.id, "Введите название продукта")
        bot.register_next_step_handler(message, u_product)   

def u_product(message):
    global product
    product = message.text
    bot.send_message (message.from_user.id,"Введите количество продукта")
    bot.register_next_step_handler(message, u_amount)

def u_amount(message):
    global amount
    amount = message.text            
    amount_converted = unit_converter(amount)
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = "Хочешь добавить еще?"
    bot.send_message(message.from_user.id, text = question, reply_markup=keyboard)

    user_fridge[product] = amount_converted
    
    user_id = message.from_user.id
    user_file = str(user_id) + ".txt"
    
    with open (user_file, "w", encoding = "utf-8") as f:
        json.dump(user_fridge, f, ensure_ascii=False)


@bot.message_handler(commands=["fridge"])  
def add_fridge(message):
    if message.text == "/fridge":
        bot.send_message (message.from_user.id, "Давай откроем холодильник и посмотрим, что там есть..)")
        user_id = message.from_user.id
        user_file = str(user_id) + ".txt"
        check_file = os.path.exists(user_file)
        if check_file == True:
            with open (user_file, "r", encoding = "utf-8") as f:
                if os.stat(user_file).st_size==0:
                    bot.send_message(message.from_user.id, "Ой-ой, совсем пусто( когда купишь чего-нибудь, выбери команду /a")
                else:
                    user_file_content = json.load(f)
                    fr_products = ""
                    fr_text = ""
                    for key, value in user_file_content.items():
                        value_str = str(int(value[0])) + ' ' + value[1]
                        fr_products = fr_products + key + ' ' + value_str + '\n'
                        fr_text = "*На твоих полочках:* \n" + fr_products
                    bot.send_message(message.from_user.id, fr_text, parse_mode="Markdown")
        else:
            bot.send_message(message.from_user.id, "Ой-ой, совсем пусто( когда купишь чего-нибудь, выбери команду /add")          




@bot.message_handler(commands=["breakfast"])
def send_recipes(message):
    if message.text == "/breakfast":
        global unclickable_choices
        unclickable_choices = []
        list_of_recipes = types.InlineKeyboardMarkup()
        list_of_choices = types.InlineKeyboardMarkup()
        f = open('recipes.json', 'r', encoding='utf-8')
        user_id = message.from_user.id
        user_file = str(user_id) + ".txt"
        input_base = open(user_file, 'r', encoding='utf-8')
        user_fridge = json.load(input_base)
        data = json.load(f)
        breakfasts_are_available = False
        for key in data:
            if compare_dict(user_fridge, data[key][0]):
                callback_button = types.InlineKeyboardButton(text=key, callback_data=key)
                another_callback_button = types.InlineKeyboardButton(text=key+" +", callback_data=" " + key)
                list_of_recipes.add(callback_button)
                list_of_choices.add(another_callback_button)
                unclickable_choices.append(" " + key)
                breakfasts_are_available = True
        input_base.close()
        f.close()
        if breakfasts_are_available:
            bot.send_message(message.chat.id, "Вот список доступных завтраков:", reply_markup=list_of_recipes)
            bot.send_message(message.chat.id, "Что ты решил приготовить?", reply_markup=list_of_choices)

#????????????????бот не может узнать тыкнул ли чел или нет?

        else:
            bot.send_message(message.chat.id, 'В твоем холодильнике пока не хватает продуктов для приготовления завтрака. Используй команду /add, чтобы пополнить холодильник :)')

def compare_dict(dict1, dict2): #эта функция сравнивает элементы двух словарей
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    is_in_dict = False
    if keys2.issubset(keys1):
        for key in list(keys2):
            if int(dict1[key][0]) >= int(dict2[key][0]):
                is_in_dict = True
            else:
                is_in_dict = False
    return is_in_dict

def unit_converter(my_unit): #эта функция переводит введенную величину в граммы и миллилитры, штуки не трогает
    units_coeff = {'л': 1000, 'мл': 1, 'кг': 1000, 'г': 1}
    my_unit_splitted = my_unit.split()
    if my_unit_splitted[1] != 'шт':
        my_unit_splitted[0] = float(my_unit_splitted[0]) * units_coeff[my_unit_splitted[1]]
        if my_unit_splitted[1] == 'л':
            my_unit_splitted[1] = 'мл'
        if my_unit_splitted[1] == 'кг':
            my_unit_splitted[1] = 'г'
    return my_unit_splitted

#КОЛБЭКЕР

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    for choice in unclickable_choices:
        if call.data == choice:    
    
            user_file = str(call.from_user.id) + ".txt"
            f_rec = open ('recipes.json', 'r', encoding='utf-8')
            f_us = open (user_file, "r", encoding = "utf-8")
            if os.stat(user_file).st_size==0:
                bot.send_message(call.from_user.id, "Ой-ой, в холодильнике пусто( Когда купишь чего-нибудь, выбери команду /add")
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
                                    if user_file_fridge[prod][0] == 0:
                                        not_exist_products.append(prod) 
                for product in not_exist_products: 
                    del user_file_fridge[product]							
									#когда равно 0, удаляем ключ
                                    									
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
        f = open('recipes.json', 'r', encoding='utf-8')
        data = json.load(f)
        ingredients = ""
        description = ""
        for key, value in data[call.data][0].items():
            value_str = str(value[0]) + ' ' + value[1]
            ingredients = ingredients + key + ' ' + value_str + '\n'
        description = data[call.data][1]
        recipes_text = '*Ингредиенты:*\n' + ingredients + '\n' + '*Способ приготовления:* \n' + description
        bot.send_message(call.message.chat.id, recipes_text, parse_mode="Markdown")
        f.close()

bot.polling()
