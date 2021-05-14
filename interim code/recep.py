import telebot
import json
from telebot import types
bot = telebot.TeleBot("1747737968:AAHQm4cfnw54SK2a6M6sUWU7G0ZyzgrJlWA")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Привет! Напиши "хочу завтрак", чтобы я мог предложить тебе рецепты :)")
@bot.message_handler(content_types=['text'])
def send_recipes(message):
    if message.text == 'хочу завтрак':
        list_of_recipes = types.InlineKeyboardMarkup()
        f = open('recipes.json', 'r', encoding='utf-8')
        data = json.load(f)
        for key in data:
            callback_button = types.InlineKeyboardButton(text=key, callback_data=key)
            list_of_recipes.add(callback_button)
        f.close()
        bot.send_message(message.chat.id, "Вот список доступных завтраков:", reply_markup=list_of_recipes)
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    f = open('recipes.json', 'r', encoding='utf-8')
    data = json.load(f)
    ingredients = ""
    description = ""
    for key, value in data[call.data][0].items():
        ingredients = ingredients + key + ' ' + value + '\n'
    description = data[call.data][1]
    recipes_text = '*Ингредиенты:*\n' + ingredients + '\n' + '*Способ приготовления:* \n'+ description
    bot.send_message(call.message.chat.id, recipes_text, parse_mode="Markdown")
    f.close()
bot.polling()
