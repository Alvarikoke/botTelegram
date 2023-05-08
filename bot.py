import os
import telebot

BOT_TOKEN = os.getenv('TOKEN')
print(BOT_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)

# Function to handle messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Check if the message is a command
    if message.text.startswith('/'):
        handle_command(message)
    else:
        bot.reply_to(message, "Por favor, introduzca un comando.")

# Define a function to handle commands
def handle_command(message):
    command = message.text[1:].lower()
    if command == 'start':
        bot.reply_to(message, "Vale, vamos a empezar.")

bot.polling()