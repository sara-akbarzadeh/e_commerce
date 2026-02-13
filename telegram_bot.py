# import telebot
# import os
# from dotenv import load_dotenv

# load_dotenv()

# BOT_TOKEN = os.environ.get("BOT_TOKEN")
# bot = telebot.TeleBot(BOT_TOKEN)

# @bot.message_handler(commands=['start'])
# def send_welcome(message):
#     bot.reply_to(message, "Welcome to the E-Commerce Bot!")


# print("Bot is running...")
# bot.polling(non_stop=True)