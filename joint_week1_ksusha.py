#-*-coding: utf-8-*-
import telebot
import json
from telebot import types

bot = telebot.TeleBot("1747737968:AAHQm4cfnw54SK2a6M6sUWU7G0ZyzgrJlWA")

user_fridge = {}
product = ""
amount = ""

@bot.message_handler(commands=["start"])
def hello(message):
    if message.text == "/start":
        bot.send_message (message.from_user.id, 'Привет! Этот бот сделает твое утро волшебным и замечательным! Выбери команду /a, чтобы добавить продукты в холодильник. Команду /h, чтобы посмотреть, что в нем есть. Напиши "хочу завтрак", чтобы я мог предложить тебе рецепты :)')

@bot.message_handler(commands=["a"])    
def add_fridge(message):
    if message.text == "/a":
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
    
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = "Хочешь добавить еще?"
    bot.send_message(message.from_user.id, text = question, reply_markup=keyboard)

    user_fridge[product] = amount
    
    user_id = message.from_user.id
    user_file = str(user_id) + ".txt"
    
    with open (user_file, "w", encoding = "utf-8") as f:
        json.dump(user_fridge, f, ensure_ascii=False)


@bot.message_handler(commands=["h"])  
def add_fridge(message):
    if message.text == "/h":
        bot.send_message (message.from_user.id, "Давай откроем холодильник и посмотрим, что там есть..)") #если холодильник пустой, код ломается
        user_id = message.from_user.id
        user_file = str(user_id) + ".txt"
        with open (user_file, "r", encoding = "utf-8") as f:
            user_file_content = json.load(f)
        fr_products = ""
        fr_text = ""
    for key, value in user_file_content.items():
            fr_products = fr_products + key + ' ' + value + '\n'
    fr_text = "*На твоих полочках:* \n" + fr_products
    bot.send_message(message.from_user.id, fr_text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "no":
        bot.send_message(call.message.chat.id, "Окей")
    elif call.data == "yes":
        bot.send_message (call.from_user.id, "Введите название продукта")
        bot.register_next_step_handler(call.message, u_product)
    else:
        f = open('recipes.json', 'r', encoding='utf-8')
        data = json.load(f)
        ingredients = ""
        description = ""
        for key, value in data[call.data][0].items():
            ingredients = ingredients + key + ' ' + value + '\n'
        description = data[call.data][1]
        recipes_text = '*Ингредиенты:*\n' + ingredients + '\n' + '*Способ приготовления:* \n' + description
        bot.send_message(call.message.chat.id, recipes_text, parse_mode="Markdown")
        f.close()

@bot.message_handler(content_types=["text"])
def send_recipes(message):
    if message.text == 'хочу завтрак':
        list_of_recipes = types.InlineKeyboardMarkup()
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
                list_of_recipes.add(callback_button)
                breakfasts_are_available = True
        input_base.close()
        f.close()
        if breakfasts_are_available:
            bot.send_message(message.chat.id, "Вот список доступных завтраков:", reply_markup=list_of_recipes)
        else:
            bot.send_message(message.chat.id, 'В твоем холодильнике пока не хватает продуктов для приготовления завтрака. Используй команду /a, чтобы пополнить холодильник :)')

def compare_dict(dict1, dict2):
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    is_in_dict = False
    if keys2.issubset(keys1):
        for key in list(keys2):
            if int(dict1[key]) >= int(dict2[key]):
                is_in_dict = True
            else:
                is_in_dict = False
    return is_in_dict

bot.polling()
