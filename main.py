import telebot
from telebot import types
import os
import json  

from PIL import Image, ImageDraw, ImageFont
import io

# Создаем экземпляр бота
bot = telebot.TeleBot('7047635627:AAFl2irjSIwtH0lggAMQu-o2pqJ-gQRW8CA')

media_folder = "media"
if not os.path.exists(media_folder):
    os.makedirs(media_folder)


media_categories = ['цены', 'контакты', 'адрес']

for category in media_categories:
    category_folder = f"{media_folder}/{category}"
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

registered_users_folder = "registered_users"  # Путь к папке с информацией о зарегистрированных пользователях

new_des = {}

user_data = {}

admin_id = [7084395348]

user_data = {}
inline_buttons_dict = {}

inline_keyboard = types.InlineKeyboardMarkup()
registration_button = types.InlineKeyboardButton(text='Регистрация', callback_data='register')
inline_keyboard.add(registration_button)

keyboard_user = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
keyboard_user.add('цены', 'контакты', 'адрес','регистрация')

keyboard_admin = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
keyboard_admin.add('добавить', 'удалить', 'рассылка','данные пользователей', 'E-mail пользователей')



@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id in admin_id:
        user_data[user_id] = {'keyboard': keyboard_admin}
        bot.send_message(user_id, f"Добро пожаловать, администратор {message.from_user.first_name}!", reply_markup=keyboard_admin)
    else:
        user_data.setdefault(user_id, {'keyboard': keyboard_user})
        bot.send_message(user_id, f"Добро пожаловать, {message.from_user.first_name}!", reply_markup=keyboard_user)
    
    # Автоматическое создание папки 'registered_users'
    if not os.path.exists('registered_users'):
        os.makedirs('registered_users')



file_to_delete = ''




# Обработчик для нажатия на кнопку "добавить"
@bot.message_handler(func=lambda message: message.text == 'добавить' and message.chat.id in admin_id)
def add_media_prompt(message):
    user_id = message.chat.id
    user_data.setdefault(user_id, {})
    user_data[user_id]['step'] = 'choose_category'
    user_data[user_id]['inline_keyboard'] = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    user_data[user_id]['text_added'] = False

    # Создаем кнопки для выбора категории
    categories = ['цены', 'контакты', 'адрес']
    user_data[user_id]['inline_keyboard'].row(*[types.KeyboardButton(category) for category in categories])

    # Добавляем кнопку "Назад" в клавиатуру
    back_button = types.KeyboardButton('Назад')
    user_data[user_id]['inline_keyboard'].add(back_button)

    # Проверяем наличие папки 'media' и создаем ее, если она отсутствует
    if not os.path.exists('media'):
        os.mkdir('media')

    bot.send_message(user_id, "Выберите категорию, куда хотите добавить медиа", reply_markup=user_data[user_id]['inline_keyboard'])

# Обработчик для кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == 'Назад' and message.chat.id in admin_id)
def go_back(message):
    user_id = message.chat.id
    user_data[user_id]['step'] = None
    bot.send_message(user_id, "Вы вернулись в главное меню.")
    bot.send_message(user_id, "Выберите одну из кнопок:", reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('step') == 'choose_category')
def choose_category_and_continue(message):
    user_id = message.chat.id
    category = message.text
    media_folder = os.path.join('media', category)

    # Проверяем наличие папки с названием категории и создаем ее, если она отсутствует
    if not os.path.exists(media_folder):
        os.mkdir(media_folder)

    user_data[user_id]['category'] = category

    user_data[user_id]['step'] = 'add_text'  #


    bot.send_message(user_id, f"Вы выбрали категорию '{message.text}'. Теперь отправьте медиа для добавления.")
    
    user_data[user_id]['step'] = 'upload_photo', 'upload_video'
    user_data[user_id]['step'] = 'add_text'





# Обработчик для сохранения фото с подписями
@bot.message_handler(content_types=['photo'])
def save_photo_with_caption(message):
    user_id = message.chat.id
    category = user_data.get(user_id, {}).get('category')

    if category:
        photo_file_id = message.photo[-1].file_id
        caption = message.caption if message.caption else ""

        if not os.path.exists(f'media/{category}'):
            os.makedirs(f'media/{category}')

        existing_photos = os.listdir(f'media/{category}')
        photo_number = len(existing_photos) + 1
        
        photo_data = {
            'image_path': f'media/{category}/photo_{photo_number}.jpg',
            'caption': caption
        }

        with open(photo_data['image_path'], 'wb') as new_file:
            new_file.write(bot.download_file(bot.get_file(photo_file_id).file_path))
        
        with open(f'media/{category}/photo_{photo_number}.json', 'w') as json_file:
            json.dump(photo_data, json_file)
        
        bot.send_message(user_id, f"Фото успешно сохранено вместе с подписью в категории '{category}' под именем 'photo_{photo_number}'.")
        user_data[user_id]['step'] = 'keyboard_admin'

    else:
        bot.send_message(user_id, "Ошибка: не установлена категория для сохранения фотографии.")





####################################################


######################################


# Обработчик для сохранения видео с подписями
@bot.message_handler(content_types=['video'])
def save_video_with_caption(message):
    user_id = message.chat.id
    category = user_data.get(user_id, {}).get('category')
    
    if category:
        video_file_id = message.video.file_id
        caption = message.caption if message.caption else ""
        
        user_data[user_id]['video_file_id'] = video_file_id
        user_data[user_id]['captions'] = user_data.get(user_id, {}).get('captions', {})
        user_data[user_id]['captions'][category] = user_data[user_id]['captions'].get(category, {})
        user_data[user_id]['captions'][category][video_file_id] = caption
        
        # Сохраняем путь к видео
        video_folder = f'media/{category}'
        
        # Определяем следующий номер для видео в категории
        files = os.listdir(video_folder)
        video_number = 1
        while f'video_{video_number}.mp4' in files:
            video_number += 1

        video_path = os.path.join(video_folder, f'video_{video_number}.mp4')

        with open(video_path, 'wb') as new_file:
            new_file.write(bot.download_file(bot.get_file(video_file_id).file_path))

        # Сохраняем JSON файл с информацией о видео и подписи
        video_data = {
            'video_path': video_path,
            'caption': caption
        }

        with open(os.path.join(video_folder, f'video_{video_number}.json'), 'w') as json_file:
            json.dump(video_data, json_file)
        
        bot.send_message(user_id, f"Видео успешно сохранено с подписью в категории '{category}' как video_{video_number}.mp4.")
        user_data[user_id]['step'] = 'keyboard_admin'
    else:
        bot.send_message(user_id, "Ошибка: не установлена категория для сохранения видео.")
    




#######################################################




# Обработчик для сохранения ссылок
@bot.message_handler(func=lambda message: message.entities is not None and message.content_type == 'text')
def save_link(message):
    user_id = message.chat.id
    category = user_data.get(user_id, {}).get('category')
    
    if category:
        for entity in message.entities:
            if entity.type == 'url':
                # Извлекаем текст по сущности из сообщения
                link_url = message.text[entity.offset:entity.offset + entity.length]
                user_data[user_id]['saved_links'] = user_data.get(user_id, {}).get('saved_links', {})
                user_data[user_id]['saved_links'].setdefault(category, []).append(link_url)
                
                # Сохранение ссылки в файл
                file_number = len(user_data[user_id]['saved_links'][category])
                file_path = f'media/{category}/link_{file_number}.txt'
                with open(file_path, 'w') as file:
                    file.write(link_url)
                
                bot.send_message(user_id, f"Ссылка успешно сохранена в категории '{category}'")
                user_data[user_id]['step'] = 'keyboard_admin'

    else:
        bot.send_message(user_id, "Ошибка: не установлена категория для сохранения ссылок.")







@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('step') == 'add_text') 
def save_text(message): 
    user_id = message.chat.id 
    category = user_data.get(user_id, {}).get('category')
    
    if category:
        # Проверяем, был ли уже добавлен текст в этой сессии
        if user_data.get(user_id, {}).get('text_added', False): 
            bot.send_message(user_id, "Ошибка: текст в этой категории уже был добавлен.")
        else:
            text = message.text.strip()
            text_file_number = user_data.get(user_id, {}).get('text_file_number', 1)
    
            while os.path.exists(f'media/{category}/text_{text_file_number}.txt'):
                text_file_number += 1  # Увеличиваем номер до тех пор, пока файл с таким номером существует
            text_filename = f'media/{category}/text_{text_file_number}.txt'

            with open(text_filename, 'w', errors='replace') as text_file:
                text_file.write(text + "\n")
                print(text)

            bot.send_message(user_id, f"Текст успешно добавлен в категорию '{category}' в файл '{text_filename}'.")
    
            # Увеличиваем номер файла для следующего сохранения
            user_data[user_id]['text_file_number'] = text_file_number + 1
            user_data[user_id]['text_added'] = True  # Устанавливаем флаг, что текст уже добавлен
            user_data[user_id]['step'] = 'keyboard_admin'

    
    else:
        bot.send_message(user_id, "Ошибка: не выбрана категория для сохранения текста.")







############################################################################




@bot.message_handler(func=lambda message: message.text in ['цены', 'контакты', 'адрес'])
def handle_keyboard_click(message):
    user_id = message.chat.id
    button_text = message.text

    media_folder_path = f'media/{button_text}'


    if os.path.exists(media_folder_path):
            files = os.listdir(media_folder_path)
            if files:
                for file in files:
                    file_path = os.path.join(media_folder_path, file)
                    if os.path.isfile(file_path):
                        try:
                            if file.endswith('.jpg'):
                                photo_name = os.path.splitext(file)[0]
                                json_file_path = os.path.join(media_folder_path, f'{photo_name}.json')
                                
                                if os.path.exists(json_file_path):
                                    try:
                                        with open(json_file_path, 'r') as json_file:
                                            data = json.load(json_file)
                                            caption = data.get('caption', "")
                                            
                                            with open(os.path.join(media_folder_path, file), 'rb') as photo_file:
                                                bot.send_photo(user_id, photo_file, caption=caption)
                                        
                                    except Exception as e:
                                        bot.send_message(user_id, f"Ошибка при отправке фото с подписью: {str(e)}")


                            elif file.endswith(('.mp4', '.avi', '.mkv')):
                                video_name = os.path.splitext(file)[0]
                                json_file_path = os.path.join(media_folder_path, f'{video_name}.json')

                                if os.path.exists(json_file_path):
                                    try:
                                        with open(json_file_path, 'r') as json_file:
                                            data = json.load(json_file)
                                            caption = data.get('caption', "")

                                            with open(os.path.join(media_folder_path, file), 'rb') as video_file:
                                                bot.send_video(user_id, video_file, caption=caption, timeout=60)


                                    except Exception as e:
                                        bot.send_message(user_id, f"Ошибка при отправке видео с подписью: {str(e)}")

                            elif file.endswith('.txt'):
                                with open(file_path, 'r') as text_file:
                                    link = text_file.read().strip()
                                    bot.send_message(user_id, link)

                            elif file.endswith('.txt'):
                                with open(file_path, 'r') as text_file:
                                    text = text_file.read()
                                    bot.send_message(user_id, text)
                            
                        except Exception as e:
                            bot.send_message(user_id, f"Ошибка при обработке файла {file}: {str(e)}")
                    else:
                        bot.send_message(user_id, f"Невозможно обработать файл: {file}")




#############################################################################




@bot.message_handler(func=lambda message: message.text == 'регистрация' and message.chat.id not in admin_id)
def handle_registration(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите ваше имя:")
    bot.register_next_step_handler(message, process_first_name)

def process_first_name(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'first_name': message.text}
    bot.send_message(chat_id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, process_last_name)

def process_last_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['last_name'] = message.text
    bot.send_message(chat_id, "Введите ваш email:")
    bot.register_next_step_handler(message, process_email)

def process_email(message):
    chat_id = message.chat.id
    user_data[chat_id]['email'] = message.text

    # Сохранение данных пользователя
    user_folder = f"{registered_users_folder}/{chat_id}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    with open(f"{user_folder}/info.txt", "w") as file:
        file.write(f"Имя: {user_data[chat_id]['first_name']}\nФамилия: {user_data[chat_id]['last_name']}\nEmail: {user_data[chat_id]['email']}")

    bot.send_message(chat_id, "Регистрация успешно завершена!", reply_markup=keyboard_user)

# Обработчик для кнопки 'Дание полсователей'
@bot.message_handler(func=lambda message: message.text == 'данные пользователей' and message.chat.id in admin_id)
def list_users_info(message):
    user_id = message.chat.id
    users_info = ""
    
    for user_folder in os.listdir(registered_users_folder):
        info_file = f"{registered_users_folder}/{user_folder}/info.txt"
        if os.path.isfile(info_file):
            with open(info_file, 'r') as file:
                user_info = file.read()
                users_info += f"{user_folder}:\n{user_info}\n\n"
    
    if users_info:
        bot.send_message(user_id, users_info)
    else:
        bot.send_message(user_id, "Нет информации о пользователях.")

# Обработчик для кнопки 'емайли'
@bot.message_handler(func=lambda message: message.text == 'E-mail пользователей' and message.chat.id in admin_id)
def list_users_emails(message):
    user_id = message.chat.id
    users_emails = ""
    
    for user_folder in os.listdir(registered_users_folder):
        info_file = f"{registered_users_folder}/{user_folder}/info.txt"
        if os.path.isfile(info_file):
            with open(info_file, 'r') as file:
                user_email = file.readlines()[-1].split(':')[-1].strip()
                users_emails += f"{user_email}\n"
    
    
    if users_emails:
        bot.send_message(user_id, users_emails)
    else:
        bot.send_message(user_id, "Нет доступной информации о email пользователях.")

@bot.message_handler(func=lambda message: message.text == 'рассылка' and message.chat.id in admin_id)
def send_broadcast_options(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Отправьте для рассылки")
    bot.register_next_step_handler(message, process_broadcast_choice)


def process_broadcast_choice(message):
    user_id = message.chat.id
    temp_dir = 'temp'  # Определяем temp_dir
    if message.text:
        broadcast_text = message.text
        for user in user_data:
            if user != admin_id:
                bot.send_message(user, broadcast_text)
        bot.send_message(user_id, "Сообщение отправлено пользователям.")
    
    elif message.photo:
        photo_caption = message.caption
        photo_file_id = message.photo[-1].file_id
        temp_file_path = f'{temp_dir}/{photo_file_id}.jpg'
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        try:
            file_info = bot.get_file(photo_file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(temp_file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            for user in user_data:
                if user != admin_id:
                    bot.send_photo(user, open(temp_file_path, 'rb'), caption=photo_caption)
            
            bot.send_message(user_id, "Фото с подписью отправлено пользователям.")
        
        except Exception as e:
            bot.reply_to(message, "Произошла ошибка при обработке фото.")
            print(e)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    elif message.video:
        video_caption = message.caption
        video_file_id = message.video.file_id
        temp_file_path = f'{temp_dir}/{video_file_id}.mp4'
        
        try:
            file_info = bot.get_file(video_file_id)
            downloaded_file = bot.download_file(file_info.file_path)


            with open(temp_file_path, 'wb') as new_file:
                            new_file.write(downloaded_file)
                        
                            for user in user_data:
                                if user != admin_id:
                                    bot.send_video(user, open(temp_file_path, 'rb'), caption=video_caption)
                            
                            bot.send_message(user_id, "Видео с подписью отправлено пользователям.")
                    
        except Exception as e:
            bot.reply_to(message, "Произошла ошибка при обработке видео.")
            print(e)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    elif message.voice:
        voice_caption = message.caption
        voice_file_id = message.voice.file_id
        temp_file_path = f'{temp_dir}/{voice_file_id}.ogg'  # Задаем расширение ogg для голосовых сообщений
        
        try:
            file_info = bot.get_file(voice_file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(temp_file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            for user in user_data:
                if user != admin_id:
                    bot.send_voice(user, open(temp_file_path, 'rb'), caption=voice_caption)
            
            bot.send_message(user_id, "Голосовое сообщение отправлено пользователям.")
        
        except Exception as e:
            bot.reply_to(message, "Произошла ошибка при обработке голосового сообщения.")
            print(e)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# Обработчик для рассылки фотографии с подписью другим пользователям администратором
@bot.message_handler(func=lambda message: message.text == 'рассылка' and message.chat.id in admin_id)
def send_photo_with_caption_to_users(message):
    user_id = message.chat.id
    if 'photo_file_id' not in user_data[user_id]:
        bot.send_message(user_id, "Пожалуйста, сначала добавьте фотографию с подписью.")
        return

    photo_file_id = user_data[user_id]['photo_file_id']
    caption = user_data[user_id]['captions'][user_data[user_id]['category']][photo_file_id]

    for user in user_data.keys():
        if user != user_id:  # Пропускаем администратора для исключения самому себе
            with open(f'media/{user_data[user_id]["category"]}/{photo_file_id}.jpg', 'rb') as photo:
                bot.send_photo(user, photo, caption=caption)
    
    bot.send_message(user_id, "Фотография успешно отправлена с подписью другим пользователям.")



########################################################################################################





# def create_keyboard(categories_list, include_back_button=False):
#     keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#     buttons = [types.KeyboardButton(category) for category in categories_list]
#     keyboard.add(*buttons)

#     if include_back_button:
#         back_button = types.KeyboardButton('Назад')
#         keyboard.add(back_button)

#     return keyboard




def create_keyboard(buttons):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(buttons), 2):
        button1 = types.InlineKeyboardButton(text=buttons[i], callback_data=buttons[i])
        if i + 1 < len(buttons):
            button2 = types.InlineKeyboardButton(text=buttons[i + 1], callback_data=buttons[i + 1])
            keyboard.add(button1, button2)
        else:
            keyboard.add(button1)
    return keyboard


@bot.message_handler(func=lambda message: message.text == 'удалить' and message.chat.id in admin_id)
def delete_media_files(message):
    user_id = message.chat.id
    categories = ['цены', 'контакты', 'адрес']

    keyboard = create_keyboard(categories)

    bot.send_message(user_id, "Выберите категорию для удаления медиафайлов и подписей:", reply_markup=keyboard)
    user_data[user_id]['step'] = 'choose_category_to_delete'



@bot.callback_query_handler(func=lambda call: user_data.get(call.message.chat.id, {}).get('step') == 'choose_category_to_delete')
def choose_category_to_delete(call):
    user_id = call.message.chat.id
    category = call.data.split("_")[-1]
    media_folder_path = f'media/{category}'

    if os.path.exists(media_folder_path):
        files = [file for file in os.listdir(media_folder_path) if not file.endswith('.json')]
        
        if files:
            inline_keyboard = create_keyboard(files)  # Создание клавиатуры с файлами или ссылками
            bot.send_message(user_id, f"Выберите файл или ссылку для удаления из категории '{category}':", reply_markup=inline_keyboard)
            user_data[user_id]['category_to_delete'] = category
            user_data[user_id]['files_to_delete'] = files
            user_data[user_id]['step'] = 'delete_file_or_link'
        else:
            bot.send_message(user_id, f"Нет файлов или ссылок для удаления в категории '{category}'.")
    else:
        bot.send_message(user_id, f"Ошибка: категория '{category}' не найдена.")


#button
@bot.callback_query_handler(func=lambda call: user_data.get(call.message.chat.id, {}).get('step') == 'delete_file_or_link')
def delete_file_or_link(call):
    user_id = call.message.chat.id
    user_data_entry = user_data.get(user_id, {})
    category = user_data_entry.get('category_to_delete')
    media_folder_path = f'media/{category}'
    file_to_delete = call.data.strip()

    if file_to_delete in os.listdir(media_folder_path):
        file_path = os.path.join(media_folder_path, file_to_delete)
        caption_path = os.path.join(media_folder_path, f'{os.path.splitext(file_to_delete)[0]}.json')

        try:
            os.remove(file_path)
            if os.path.exists(caption_path):
                os.remove(caption_path)
                bot.send_message(user_id, f"Файл и подпись '{file_to_delete}' успешно удалены из категории '{category}'.")
            else:
                bot.send_message(user_id, f"Файл '{file_to_delete}' успешно удален из категории '{category}'.")
        except Exception as e:
            bot.send_message(user_id, f"Произошла ошибка при удалении файла и подписи: {str(e)}. Попробуйте еще раз.")
    else:
        bot.send_message(user_id, f"Файл '{file_to_delete}' не существует в категории '{category}'. Пожалуйста, выберите еще раз.")


bot.polling()