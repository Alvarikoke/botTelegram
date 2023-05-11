import os
import requests
import telebot

BOT_TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

trips = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(message)

    if message.text.startswith('/'):
        handle_command(message)
    elif message.photo:
        handle_photo(message)
    elif message.location:
        chat_id = message.chat.id
        trip_name = trips[chat_id]['name']
        handle_live_location(message, chat_id, trip_name)
    else:
        bot.reply_to(message, "Por favor, introduzca un comando.")


def handle_command(message):
    command = message.text[1:].lower()

    if command == 'start':
        bot.reply_to(message, "¿Quieres crear un nuevo viaje o gestionar uno ya existente?")
    
    elif command == 'nuevo':
        chat_id = message.chat.id
        bot.reply_to(message, "¿Cómo se llama el nuevo viaje?")
        trips[chat_id] = {'name': '', 'location': None, 'photo_num': 0}
        bot.register_next_step_handler(message, handle_new_trip)

def handle_new_trip(message):
    chat_id = message.chat.id
    trip_name = message.text
    trips[chat_id]['name'] = trip_name
    bot.reply_to(message, "Por favor, active la ubicación en tiempo real.")

def handle_live_location(message):
    chat_id = message.chat.id
    location = message.location
    trips[chat_id]['location'] = location
    bot.send_message(chat_id, "Se ha registrado su ubicación actual.")

def handle_photo(message):
    chat_id = message.chat.id
    trip_name = trips[chat_id]['name']
    if trips[chat_id]['location']:
        photo_num = trips[chat_id]['photo_num'] + 1
        trips[chat_id]['photo_num'] = photo_num

        # Obtener información del archivo de la foto
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Construir la URL del archivo de la foto
        url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        # Descargar y almacenar la foto
        response = requests.get(url)
        if response.status_code == 200:
            file_name = f"{chat_id}_{trip_name}_{photo_num}.jpg"
            with open(file_name, "wb") as f:
                f.write(response.content)
            bot.reply_to(message, "La foto ha sido almacenada.")
        else:
            bot.reply_to(message, "Error al descargar la foto.")
    else:
        bot.reply_to(message, "Por favor, active la ubicación en tiempo real antes de enviar fotos.")

bot.polling()
