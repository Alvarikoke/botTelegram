import os
import requests
import telebot
from telebot import types
import hashlib
from dbController import Database

BOT_TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

trips = {}
current_trip_ids = {}  # Dictionary to store the current trip ID for each chat_id
location_sent = False

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    chat_id = str(message.chat.id)
    content = message.content_type
    username = message.chat.username or ''
    first_name = message.chat.first_name or ''
    last_name = message.chat.last_name or ''

    print("Chat ID: " + chat_id + "\nTipo de mensaje: " + content + "\nUsuario: " + username + "\nNombre: " + first_name + "\nApellidos: " + last_name + "\nMensaje: " + message.text)

    if message.text.startswith('/'):
        handle_command(message)
    else:
        bot.reply_to(message, "Por favor, introduce un comando.\n\nPuedes ver una lista de comandos en el \"Menú\" (a la izquierda de donde se escriben los mensajes).\n\nPresiona \"/start\" si quieres ver de nuevo cómo funciona el bot.")

@bot.message_handler(func=lambda message: True, content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    trip_name = current_trip_ids.get(chat_id)

    if trip_name is None or trip_name == '':
        bot.send_message(chat_id, "Por favor, tienes que asignar la fotografía a un nuevo viaje, puedes hacerlo usando el comando /nuevo .")
    else:
        location = trips.get(chat_id, {}).get('location', {})
        if location.get('latitude') is not None and location.get('longitude') is not None:
            check_location_sent(message)
        else:
            bot.send_message(chat_id, "Por favor, active la ubicación en tiempo real antes de enviar fotos.")


@bot.message_handler(func=lambda message: True, content_types=['location'])
def handle_location(message):
    set_location(bot, message)

def handle_command(message):
    command = message.text[1:].lower()
    chat_id = message.chat.id

    if command == 'start':
        chat_id = str(message.chat.id)

        bot.reply_to(message, "Te damos la bienvenida a \"My Trip Memories\", un bot de Telegram con el que podrás enviar las fotos de tu viaje y poder verlas en un vistoso mapa en nuestra web:\nlocalhost:3000/registro.html?id=" + chat_id + "\n\nSi es tu primera vez presiona el comando \"/nuevo\" para crear un nuevo viaje.\n\nRecuerda que tendrás que ponerle un nombre y que éste no puede empezar por \"/\".\n\nUna vez hayas introducido el nombre del viaje tendrás que compartir tu ubicación, lo que nos ayudará a posicionar tus fotos en el mapa.\n\nSi necesitas ayuda para poder enviar la ubicación presiona el comando \"/ayuda\".\n\nUna vez lo hayas hecho simplemente envía tus fotos y disfruta del viaje :)")
    elif command == 'nuevo':
        bot.reply_to(message, "¿Cómo quieres llamar al viaje?")
        trips[chat_id] = {'name': '', 'location': {'latitude': None, 'longitude': None}, 'photo_num': 0}
        bot.register_next_step_handler(message, new_trip)
    elif command == 'ayuda':
        bot.reply_to(message, "Para poder mandarnos tu ubicación en tiempo real dale al clip al lado del cuadro de mensaje y selecciona \"Ubicación\", que tendrá un icono de un globo como el de Google Maps. Una vez le hayas dado a \"Ubicación\" presiona \"Ubicación en tiempo real\". Si es la primera vez que lo haces, probablemente tu dispositivo te pida configurar los permisos, hazlo en el menú de ajustes de tu teléfono y vuelve a la aplicación cuando lo hayas hecho.\n\nEn Apple, cuando le des a compartir la ubicación en tiempo real le tendrás que dar a \"Usar mientras se usa la app\".\n\nSi estás en Android selecciona \"Permitir siempre\".\n\nSi necesitas más ayuda puedes usar el comando \"/android\" si posees un terminal Android; o \"/apple\" si posees un terminal de Apple.")
    elif command == 'android':
        bot.reply_to(message, "Aquí tienes capturas de pantalla explicando cómo activar la ubicación en tiempo real en su dispositivo Android:")

        url = "https://api.telegram.org/bot" + BOT_TOKEN +"/sendPhoto"

        foto1 = {
            "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Android_logo_2019_%28stacked%29.svg/1200px-Android_logo_2019_%28stacked%29.svg.png",
            "disable_notification": False,
            "reply_to_message_id": None,
            "chat_id": chat_id
        }
        foto2 = {
            "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Android_logo_2019_%28stacked%29.svg/1200px-Android_logo_2019_%28stacked%29.svg.png",
            "disable_notification": False,
            "reply_to_message_id": None,
            "chat_id": chat_id
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        responseFoto1 = requests.post(url, json=foto1, headers=headers)
        bot.send_message(chat_id, "Después haga esto:")
        responseFoto2 = requests.post(url, json=foto2, headers=headers)

        print(responseFoto1.text)
        print(responseFoto2.text)

    elif command == 'apple':
        bot.reply_to(message, "Fotos:")

        url = "https://api.telegram.org/bot" + BOT_TOKEN +"/sendPhoto"

        payload = {
            "photo": "https://www.apple.com/ac/structured-data/images/open_graph_logo.png?202209050149",
            "disable_notification": False,
            "reply_to_message_id": None,
            "chat_id": chat_id
        }

        headers = {
            "accept": "application/json",
            "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
    else:
        bot.reply_to(message, "No existe ese comando. Puedes ver una lista de comandos en el \"Menú\" (a la izquierda de donde se escriben los mensajes).")


# Creacion de un nuevo viaje
def new_trip(message):
    print('-------------')
    print('Handle New Trip')
    chat_id = message.chat.id
    trip_name = message.text
    if trip_name.startswith('/'):
        bot.reply_to(message, "Por favor, usa un nombre que no empiece por \"/\".\n\nPulse de nuevo en \"/nuevo\" para intentarlo con otro nombre.")
    else:
        trips[chat_id]['name'] = trip_name
        current_trip_ids[chat_id] = trip_name  # Associate the trip name with the chat_id
        print('Nombre del viaje: ' + trip_name)
        ask_location(message)
        # bot.reply_to(message, "Por favor, active la ubicación en tiempo real.\n\nSi tiene problemas para activarla presione el comando \"/ayuda\".")

def ask_location(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = types.KeyboardButton(text="Pulsa para compartir la localización", request_location=True)
    keyboard.add(button)
    bot.reply_to(message, "Por favor, comparta su localización.", reply_markup=keyboard)

def set_location(bot, message):
    print('-------------')
    print('Handle Live Location')
    chat_id = message.chat.id
    try:
        trip_name = current_trip_ids.get(chat_id)  # Get the trip name associated with the chat_id
        if trip_name is None or trip_name == '':
            bot.send_message(chat_id, "Por favor, antes de enviar una ubicación tienes que crear un viaje, puedes hacerlo usando el comando /nuevo.")
        else:
            latitude = message.location.latitude
            longitude = message.location.longitude
            trips[chat_id]['location']['latitude'] = latitude
            trips[chat_id]['location']['longitude'] = longitude
            global location_sent
            location_sent = True
            bot.send_message(chat_id, "Se ha registrado su ubicación actual.\n\nEnvía una foto.")
    except KeyError:
        bot.send_message(chat_id, "Por favor, antes de enviar una ubicación tienes que crear un viaje, puedes hacerlo usando el comando /nuevo.")

def check_location_sent(message):
    global location_sent
    if location_sent == False:
        ask_location(message)
    else:
        photo(message)

def photo(message):
    print('-------------')
    print('Handle Photo')

    chat_id = message.chat.id

    try:
        trip_name = current_trip_ids.get(chat_id)  # Get the trip name associated with the chat_id
        location = trips.get(chat_id, {}).get('location', {})
        if trip_name is None or trip_name == '':
            bot.send_message(message, "Por favor, tienes que asignar la fotografía a un viaje, puedes hacerlo usando el comando /nuevo .")
        elif location.get('latitude') is not None and location.get('longitude') is not None:
            print(trips)
            photo_num = trips[chat_id]['photo_num'] + 1
            trips[chat_id]['photo_num'] = photo_num

            # Obtener información del archivo de la foto
            file_id = message.photo[-1].file_id
            print(file_id)
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path

            # Get the current live location
            lat = location['latitude']
            lon = location['longitude']

            # Construir la URL del archivo de la foto
            url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            print('URL de la foto: ' + url)

            # Descargar y almacenar la foto
            response = requests.get(url)
            if response.status_code == 200:
                file_name = f"{chat_id}_{trip_name}_{lat}_{lon}_{photo_num}.jpg"
                print(file_name)
                with open(file_name, "wb") as f:
                    f.write(response.content)
                insertPhotoDB(url, file_name)

                # Update the location with the new coordinates
                trips[chat_id]['location']['latitude'] = lat
                trips[chat_id]['location']['longitude'] = lon

                global location_sent
                location_sent = False

                keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                button = types.KeyboardButton(text="Pulsa para compartir la localización", request_location=True)
                keyboard.add(button)
                bot.reply_to(message, "La foto ha sido almacenada.\n\nRecuerda compartir de nuevo la localización antes de enviar otra foto.", reply_markup=keyboard)

            else:
                bot.reply_to(message, "Error al descargar la foto.")
        else:
            bot.reply_to(message, "Por favor, envíe una localización antes de enviar fotos.")
    except KeyError:
        bot.send_message(chat_id, "Por favor, tienes que asignar la fotografía a un viaje, puedes hacerlo usando el comando \"/nuevo\".")

def insertPhotoDB(url, file_name):
    with Database() as db:
        file_name_parts = file_name.split('_')
        trip_name = file_name_parts[1]
        chat_id = file_name_parts[0]

        # Check if the trip name already exists in the trips table
        trips = db.read('trips', f"trip_name = '{trip_name}'")
        if len(trips) == 0:
            # Insert the trip record if it doesn't exist
            tripData = {
                'trip_name': trip_name,
            }
            idTrip = db.create('trips', tripData)
        else:
            idTrip = trips[0][0]  # Get the ID of the existing trip

        # Check if the chat ID already exists in the users table
        users = db.read('users', f"chat_id = '{chat_id}'")
        if len(users) == 0:
            # Insert the user record if it doesn't exist
            userData = {
                'chat_id': chat_id,
            }
            idUser = db.create('users', userData)
        else:
            idUser = users[0][0]  # Get the ID of the existing user

        # Insert the image record
        imageData = {
            'image_url': url,
            'latitude': file_name_parts[2],
            'longitude': file_name_parts[3],
            'image_name': file_name,
        }
        idImage = db.create('images', imageData)

        # Insert the principal record if it doesn't exist
        principal = db.read('principal', f"user_id = {idUser} AND trip_id = {idTrip} AND image_id = {idImage}")
        if len(principal) == 0:
            principalData = {
                'user_id': idUser,
                'trip_id': idTrip,
                'image_id': idImage,
            }
            db.create('principal', principalData)

bot.polling()
