import os
import requests
import telebot

BOT_TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

trips = {}

@bot.message_handler(func=lambda message: True, content_types = ['text'])
def handle_message(message):
    print(message)

    if message.text.startswith('/'):
        handle_command(message)
    else:
        bot.reply_to(message, "Por favor, introduzca un comando.")

@bot.message_handler(func=lambda message: True, content_types = ['photo'])
def handle_photo(message):
    photo(message)

@bot.message_handler(func=lambda message: True, content_types = ['location'])
def handle_location(message):
    live_location(bot, message)


def handle_command(message):
    command = message.text[1:].lower()

    if command == 'start':
        bot.reply_to(message, "¿Quieres crear un nuevo viaje o gestionar uno ya existente?")
    
    elif command == 'nuevo':
        chat_id = message.chat.id
        bot.reply_to(message, "¿Cómo se llama el nuevo viaje?")
        trips[chat_id] = {'name': '', 'location': None, 'photo_num': 0}
        bot.register_next_step_handler(message, new_trip)

# Creacion de un nuevo viaje
def new_trip(message):
    print('-------------')
    print('Handle New Trip')
    chat_id = message.chat.id
    trip_name = message.text
    trips[chat_id]['name'] = trip_name
    bot.reply_to(message, "Por favor, active la ubicación en tiempo real.")

# Procesamiento de la ubicacion en tiempo real
def live_location(bot, message):
    print('-------------')
    print('Handle Live Location')
    chat_id = message.chat.id
    current_pos = (message.location.latitude, message.location.longitude)
    print(current_pos)
    trips[chat_id]['location'] = current_pos
    bot.send_message(chat_id, "Se ha registrado su ubicación actual.")

# Procesamiento de la imagen enviada por el usuario
def photo(message):
    print('-------------')
    print('Handle photo')
    chat_id = message.chat.id
    trip_name = trips[chat_id]['name']
    # Aunque la ubicacion en tiempo real ya este activada de antes te requerira activarla de nuevo. Telegram no tiene forma de saber si esta o no esta activada
    if trips[chat_id]['location']:
        photo_num = trips[chat_id]['photo_num'] + 1
        trips[chat_id]['photo_num'] = photo_num

        # Obtener información del archivo de la foto
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Construir la URL del archivo de la foto
        url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        print('URL de la foto: ' + url)

        # Descargar y almacenar la foto
        response = requests.get(url)
        if response.status_code == 200:
            file_name = f"{chat_id}_{trip_name}_{photo_num}.jpg"
            print(file_name)
            with open(file_name, "wb") as f:
                f.write(response.content)
            bot.reply_to(message, "La foto ha sido almacenada.")
        else:
            bot.reply_to(message, "Error al descargar la foto.")
    else:
        bot.reply_to(message, "Por favor, active la ubicación en tiempo real antes de enviar fotos.")

bot.polling()
