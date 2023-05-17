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
        bot.reply_to(message, "Por favor, introduce un comando.\n\nPuedes ver una lista de comandos en el \"Menú\" (a la izquierda de donde se escriben los mensajes).\n\nPresiona \"/start\" si quieres ver de nuevo cómo funciona el bot.")

@bot.message_handler(func=lambda message: True, content_types = ['photo'])
def handle_photo(message):
    photo(message)

@bot.message_handler(func=lambda message: True, content_types = ['location'])
def handle_location(message):
    live_location(bot, message)

def handle_command(message):
    command = message.text[1:].lower()
    chat_id = message.chat.id

    if command == 'start':
        chat_id_string = str(message.chat.id)
        bot.reply_to(message, "Te damos la bienvenida a \"My Trip Memories\", un bot de Telegram con el que podrás enviar las fotos de tu viaje y poder verlas en un vistoso mapa en nuestra web:\nmytripmemories.x10.bz/user/" + chat_id_string + "\n\nSi es tu primera vez presiona el comando \"/nuevo\" para crear un nuevo viaje.\n\nRecuerda que tendrás que ponerle un nombre y que éste no puede empezar por \"/\".\n\nUna vez hayas introducido el nombre del viaje tendrás que compartir tu ubicación en tiempo real, lo que nos ayudará a posicionar tus fotos en el mapa.\n\nSi necesitas ayuda para poder usar la ubicación en tiempo real en Telegram presiona el comando \"/ayuda\".\n\nUna vez lo hayas hecho simplemente envía tus fotos y disfruta del viaje :)")
    elif command == 'nuevo':
        bot.reply_to(message, "¿Cómo se llama el nuevo viaje?")
        trips[chat_id] = {'name': '', 'location': None, 'photo_num': 0}
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
        print('Nombre del viaje: ' + trip_name)
        bot.reply_to(message, "Por favor, active la ubicación en tiempo real.\n\nSi tiene problemas para activarla presione el comando \"/ayuda\".")

# Procesamiento de la ubicacion en tiempo real
def live_location(bot, message):
    print('-------------')
    print('Handle Live Location')
    chat_id = message.chat.id
    current_pos = str((message.location.latitude, message.location.longitude))
    print('Posición: '+ current_pos)
    trips[chat_id]['location'] = current_pos
    bot.send_message(chat_id, "Se ha registrado su ubicación actual.")

# Procesamiento de la imagen enviada por el usuario
def photo(message):
    print('-------------')
    print('Handle Photo')
    chat_id = message.chat.id

    try:
        trip_name = trips[chat_id]['name']
        if trip_name is None or '':
            bot.send_message(message, "Por favor, tienes que asignar la fotografía a un nuevo viaje, puedes hacerlo usando el comando /nuevo .")
        elif trips[chat_id]['location']:
            photo_num = trips[chat_id]['photo_num'] + 1
            trips[chat_id]['photo_num'] = photo_num

            # Obtener información del archivo de la foto
            file_id = message.photo[-1].file_id
            print(file_id)
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path

            # Obtener la latitud y longitud
            lat = trips[chat_id]['location'].split(',')[0]
            lon = trips[chat_id]['location'].split(',')[1]

            # Eliminar espacios y paréntesis
            trip_name = trip_name.replace(' ', '')
            lat = lat.replace(' ', '')
            lon = lon.replace(' ', '')
            lat = lat.replace('(', '')
            lon = lon.replace(')', '')

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
                bot.reply_to(message, "La foto ha sido almacenada.")
            else:
                bot.reply_to(message, "Error al descargar la foto.")
        else:
            bot.reply_to(message, "Por favor, active la ubicación en tiempo real antes de enviar fotos.")
    except KeyError:
        bot.send_message(chat_id, "Por favor, tienes que asignar la fotografía a un viaje, puedes hacerlo usando el comando \"/nuevo\".")

bot.polling()
