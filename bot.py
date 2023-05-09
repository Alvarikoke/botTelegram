import os
import telebot
# import requests
# import json

BOT_TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
# url = "https://api.telegram.org/" + BOT_TOKEN + "/getFile"

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    fileID = message.photo[-1].file_id
    print (message)
    print("------------")
    print(fileID)
    file_info = bot.get_file(fileID)
    bot.reply_to (message, 'file.file_path =' + file_info.file_path)
    # Taggear las fotos con las imagenes

# Function to handle messages
@bot.message_handler(func = lambda message: True)
def handle_message(message):
    print(message)
    # Check if the message is a command
    if message.text.startswith('/'):
        handle_command(message)
    else:
        bot.reply_to(message, "Por favor, introduzca un comando.")

# Define a function to handle commands
def handle_command(message):
    command = message.text[1:].lower()
    if command == 'start':
        bot.reply_to(message, "¿Quieres crear un nuevo viaje o gestionar uno ya existente?")
        if command == 'nuevo':
            bot.reply_to(message, "¿Cómo quieres llamar al viaje?")

bot.polling()
