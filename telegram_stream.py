import json
import subprocess
from telethon import TelegramClient, events
from telethon.tl.custom import Button

with open("urls.json", "r") as url_read:
    urls = json.load(url_read)

api_id = int(urls["api_id"])
api_hash = urls["api_hash"]
bot_token = urls["bot_token"]

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
print("Телеграм бота було запущено.")
# Словник для відстеження активних трансляцій
active_streams = {}

stream_url = urls["stream_url"]
telegram_url = urls["telegram_url"]
youtube_url = urls["youtube_url"]
tiktok_url = urls["tiktok_url"]
twitch_url = urls["twitch_url"]
instagram_url = urls["instagram_url"]


async def start_streaming(source_url, rtmp_url):
    command = [
        'ffmpeg',
        '-i', source_url,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-ar', '48000',
        '-async', '1',
        '-f', 'flv',
        rtmp_url
    ]
    process = subprocess.Popen(command)
    return process


old_message = None


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    global old_message
    # Видалення попереднього повідомлення з кнопками, якщо воно існує
    if old_message:
        await client.delete_messages(event.chat_id, [old_message])
    # Відправка нового повідомлення з кнопками
    old_message = await event.respond('Ласкаво просимо до зали трансляцій!', buttons=[
        [Button.inline('Ввімкнути трансляцію', b'turn_on')],
        [Button.inline('Вимкнути трансляцію', b'turn_off')],
        [Button.inline('Статус трансляцій', b'status')],
        [Button.inline('Змінити джерела', b'set_urls')]
    ])


@client.on(events.CallbackQuery())
async def callback_query_handler(event):
    callback_data = event.data
    if callback_data == b'turn_on':
        await event.edit('Виберіть опцію:', buttons=[
            [Button.inline('Ввімкнути всі трансляції', b'stream_all')],
            [Button.inline('Ввімкнути Telegram', b'stream_telegram')],
            [Button.inline('Ввімкнути YouTube', b'stream_youtube')],
            [Button.inline('Ввімкнути Twitch', b'stream_twitch')],
            [Button.inline('Ввімкнути TikTok', b'stream_tiktok')],
            [Button.inline('Ввімкнути Instagram', b'stream_instagram')],
            [Button.inline('Назад', b'back_main')]
        ])
    elif callback_data == b'turn_off':
        await event.edit('Виберіть опцію:', buttons=[
            [Button.inline('Вимкнути всі трансляції', b'stop_all')],
            [Button.inline('Вимкнути Telegram', b'stop_telegram')],
            [Button.inline('Вимкнути YouTube', b'stop_youtube')],
            [Button.inline('Вимкнути Twitch', b'stop_twitch')],
            [Button.inline('Вимкнути TikTok', b'stop_tiktok')],
            [Button.inline('Вимкнути Instagram', b'stop_instagram')],
            [Button.inline('Назад', b'back_main')]
        ])
    elif callback_data in [b'stream_all', b'stream_telegram', b'stream_youtube',
                           b'stream_tiktok', b'stream_twitch', b'stream_instagram']:
        # Викликайте тут відповідну функцію для ввімкнення трансляції
        # Наприклад, для ввімкнення всіх трансляцій:
        if callback_data == b'stream_all':
            await stream_all(event)
        elif callback_data == b'stream_telegram':
            await stream_telegram(event)
        elif callback_data == b'stream_youtube':
            await stream_youtube(event)
        elif callback_data == b'stream_tiktok':
            await stream_tiktok(event)
        elif callback_data == b'stream_twitch':
            await stream_twitch(event)
        elif callback_data == b'stream_instagram':
            await stream_instagram(event)
    elif callback_data in [b'stop_all', b'stop_telegram', b'stop_youtube',
                           b'stop_tiktok', b'stop_twitch', b'stop_instagram']:
        # Викликайте тут відповідну функцію для вимкнення трансляції
        if callback_data == b'stop_all':
            await stop_all(event)
        elif callback_data == b'stop_telegram':
            await stop_telegram(event)
        elif callback_data == b'stop_youtube':
            await stop_youtube(event)
        elif callback_data == b'stop_tiktok':
            await stop_tiktok(event)
        elif callback_data == b'stop_twitch':
            await stop_twitch(event)
        elif callback_data == b'stop_instagram':
            await stop_instagram(event)
    elif callback_data == b'status':
        await status(event)
        await start(event)
    elif callback_data == b'set_urls':
        await event.edit('Оберіть яке значення поміняти:', buttons=[
            [Button.inline('Першоджерело трансляції', b'stream_url')],
            [Button.inline('Джерело для Telegram', b'telegram_url')],
            [Button.inline('Джерело для Twitch', b'twitch_url')],
            [Button.inline('Джерело для YouTube', b'youtube_url')],
            [Button.inline('Джерело для TikTok', b'tiktok_url')],
            [Button.inline('Джерело для Instagram', b'instagram_url')],
            [Button.inline('Зберегти зміни(❗️❗️❗️)', b'save_urls')],
            [Button.inline('Назад', b'back_main')]
        ])
    elif callback_data in [b'youtube_url', b'instagram_url', b'twitch_url', b'tiktok_url',
                           b'telegram_url']:
        if callback_data == b'youtube_url':
            await set_youtube_url(event)
        elif callback_data == b'instagram_url':
            await set_instagram_url(event)
        elif callback_data == b'tiktok_url':
            await set_tiktok_url(event)
        elif callback_data == b'twitch_url':
            await set_twitch_url(event)
        elif callback_data == b'telegram_url':
            await set_telegram_url(event)

    elif callback_data == b'save_urls':
        await save_urls(event)
        await start(event)
    elif callback_data == b'back_main':
        await start(event)


async def handle_stream_start(event, rtmp_url, source_name):
    # Перевірка, чи вже існує активний процес для даної URL
    if stream_url == "0":
        await event.respond("Відсутнє посилання на першоджерело трансляції.")
    else:
        if rtmp_url in active_streams or rtmp_url == "0":
            await event.respond(f'Трансляція до {source_name} вже запущена або посилання не існує.')
        else:
            process = await start_streaming(stream_url, rtmp_url)
            active_streams[rtmp_url] = process
            await event.respond(f'Починаю трансляцію до {rtmp_url}... Трансляція запущена!')


@client.on(events.NewMessage(pattern='/stream_telegram'))
async def stream_telegram(event):
    await handle_stream_start(event, telegram_url, "Telegram")


@client.on(events.NewMessage(pattern='/status'))
async def status(event):
    streams = list(active_streams.keys())
    answer = ""
    for i in streams:
        if i == telegram_url:
            answer += "Telegram транслюється.\n"
        if i == youtube_url:
            answer += "YouTube транслюється.\n"
        if i == instagram_url:
            answer += "Instagram транслюється.\n"
        if i == twitch_url:
            answer += "Twitch транслюється.\n"
        if i == tiktok_url:
            answer += "TikTok транслюється.\n"

    if answer == "":
        answer = "Нема активних трансляцій."
    await event.respond(answer)


@client.on(events.NewMessage(pattern='/stream_youtube'))
async def stream_youtube(event):
    await handle_stream_start(event, youtube_url, "YouTube")


@client.on(events.NewMessage(pattern='/stream_tiktok'))
async def stream_tiktok(event):
    await handle_stream_start(event, tiktok_url, "TikTok")


@client.on(events.NewMessage(pattern='/stream_twitch'))
async def stream_twitch(event):
    await handle_stream_start(event, twitch_url, "Twitch")


@client.on(events.NewMessage(pattern='/stream_instagram'))
async def stream_instagram(event):
    await handle_stream_start(event, instagram_url, "Instagram")


@client.on(events.NewMessage(pattern='/stream_all'))
async def stream_all(event):
    await stream_youtube(event)
    await stream_tiktok(event)
    await stream_twitch(event)
    await stream_telegram(event)
    await stream_instagram(event)


@client.on(events.NewMessage(pattern='/stop_telegram'))
async def stop_telegram(event):
    if telegram_url in active_streams:
        active_streams[telegram_url].terminate()
        del active_streams[telegram_url]
        await event.respond('Трансляцію до Telegram було зупинено.')
    else:
        await event.respond('Відсутня активна трансляція на Telegram, котру можна зупинити.')


@client.on(events.NewMessage(pattern='/stop_youtube'))
async def stop_youtube(event):
    if youtube_url in active_streams:
        active_streams[youtube_url].terminate()
        del active_streams[youtube_url]
        await event.respond('Трансляцію до YouTube було зупинено.')
    else:
        await event.respond('Відсутня активна трансляція на YouTube, котру можна зупинити.')


@client.on(events.NewMessage(pattern='/stop_twitch'))
async def stop_twitch(event):
    if twitch_url in active_streams:
        active_streams[twitch_url].terminate()
        del active_streams[twitch_url]
        await event.respond('Трансляцію до Twitch було зупинено.')
    else:
        await event.respond('Відсутня активна трансляція на Twitch, котру можна зупинити.')


@client.on(events.NewMessage(pattern='/stop_tiktok'))
async def stop_tiktok(event):
    if tiktok_url in active_streams:
        active_streams[tiktok_url].terminate()
        del active_streams[tiktok_url]
        await event.respond('Трансляцію до TikTok було зупинено.')
    else:
        await event.respond('Відсутня активна трансляція на TikTok, котру можна зупинити.')


@client.on(events.NewMessage(pattern='/stop_instagram'))
async def stop_instagram(event):
    if tiktok_url in active_streams:
        active_streams[instagram_url].terminate()
        del active_streams[instagram_url]
        await event.respond('Трансляцію до TikTok було зупинено.')
    else:
        await event.respond('Відсутня активна трансляція на TikTok, котру можна зупинити.')


@client.on(events.NewMessage(pattern='/stop_all'))
async def stop_all(event):
    if active_streams:
        for rtmp_url, process in active_streams.items():
            process.terminate()
        active_streams.clear()
        await event.respond('Всі трансляції зупинено.')
    else:
        await event.respond('Відсутні активні трансляції, котрі можна зупинити.')


@client.on(events.NewMessage(pattern='/save_urls'))
async def save_urls(event):
    urls["stream_url"] = stream_url
    urls["telegram_url"] = telegram_url
    urls["youtube_url"] = youtube_url
    urls["tiktok_url"] = tiktok_url
    urls["twitch_url"] = twitch_url
    urls["instagram_url"] = instagram_url
    with open("urls.json", "w") as url_write:
        json.dump(urls, url_write)
    await event.respond('Зміни було збережено.')


# Словник для тимчасового збереження відповідей користувача
user_responses = {}


@client.on(events.NewMessage(pattern='/set_telegram_url'))
async def set_telegram_url(event):
    global user_responses, telegram_url

    await event.respond("Ваше теперішнє посилання на Telegram: " + telegram_url)
    await event.respond('Будь ласка, введіть посилання до Telegram:')

    async def handle_response(response_event):
        global telegram_url

        if response_event.sender_id == event.sender_id and response_event.message:
            if response_event.message.message != "-":
                user_responses[event.sender_id] = response_event.message.message

                await response_event.respond(f'Отримане посилання на Telegram: {user_responses[event.sender_id]}')
                telegram_url = user_responses[event.sender_id]
                user_responses.pop(event.sender_id, None)
            else:
                await response_event.respond("Ви скасували зміну посилання.")
            client.remove_event_handler(handle_response)

    client.add_event_handler(handle_response, events.NewMessage(from_users=event.sender_id))


@client.on(events.NewMessage(pattern='/set_youtube_url'))
async def set_youtube_url(event):
    global user_responses, youtube_url

    await event.respond("Ваше теперішнє посилання на YouTube:" + youtube_url)
    await event.respond('Будь ласка, введіть посилання до YouTube:')

    async def handle_response(response_event):
        global youtube_url

        if response_event.sender_id == event.sender_id and response_event.message:
            if response_event.message.message != "-":
                user_responses[event.sender_id] = response_event.message.message

                await response_event.respond(f'Отримане посилання на YouTube: {user_responses[event.sender_id]}')
                youtube_url = user_responses[event.sender_id]
                user_responses.pop(event.sender_id, None)
            else:
                await response_event.respond("Ви скасували зміну посилання.")
            client.remove_event_handler(handle_response)

    client.add_event_handler(handle_response, events.NewMessage(from_users=event.sender_id))


@client.on(events.NewMessage(pattern='/set_tiktok_url'))
async def set_tiktok_url(event):
    global user_responses, tiktok_url

    await event.respond("Ваше теперішнє посилання на TikTok: " + tiktok_url)
    await event.respond('Будь ласка, введіть посилання до TikTok:')

    async def handle_response(response_event):
        global tiktok_url

        if response_event.sender_id == event.sender_id and response_event.message:
            if response_event.message.message != "-":
                user_responses[event.sender_id] = response_event.message.message

                await response_event.respond(f'Отримане посилання на TikTok: {user_responses[event.sender_id]}')
                tiktok_url = user_responses[event.sender_id]
                user_responses.pop(event.sender_id, None)
            else:
                await response_event.respond("Ви скасували зміну посилання.")
            client.remove_event_handler(handle_response)

    client.add_event_handler(handle_response, events.NewMessage(from_users=event.sender_id))


@client.on(events.NewMessage(pattern='/set_twitch_url'))
async def set_twitch_url(event):
    global user_responses, twitch_url

    await event.respond("Ваше теперішнє посилання на Twitch: " + twitch_url)
    await event.respond('Будь ласка, введіть посилання до Twitch:')

    async def handle_response(response_event):
        global twitch_url

        if response_event.sender_id == event.sender_id and response_event.message:
            if response_event.message.message != "-":
                user_responses[event.sender_id] = response_event.message.message

                await response_event.respond(f'Отримане посилання на Twitch: {user_responses[event.sender_id]}')
                twitch_url = user_responses[event.sender_id]
                user_responses.pop(event.sender_id, None)
            else:
                await response_event.respond("Ви скасували зміну посилання.")
            client.remove_event_handler(handle_response)

    client.add_event_handler(handle_response, events.NewMessage(from_users=event.sender_id))


@client.on(events.NewMessage(pattern='/set_instagram_url'))
async def set_instagram_url(event):
    global user_responses, instagram_url

    await event.respond("Ваше теперішнє посилання на Instagram: " + instagram_url)
    await event.respond('Будь ласка, введіть посилання до Instagram:')

    async def handle_response(response_event):
        global instagram_url

        if response_event.sender_id == event.sender_id and response_event.message:
            if response_event.message.message != "-":
                user_responses[event.sender_id] = response_event.message.message

                await response_event.respond(f'Отримане посилання на Instagram: {user_responses[event.sender_id]}')
                instagram_url = user_responses[event.sender_id]
                user_responses.pop(event.sender_id, None)
            else:
                await response_event.respond("Ви скасували зміну посилання.")
            client.remove_event_handler(handle_response)

    client.add_event_handler(handle_response, events.NewMessage(from_users=event.sender_id))


@client.on(events.NewMessage(pattern='/dump_json'))
async def dump_json(event):
    try:
        # Читання файлу urls.json
        with open('urls.json', 'r') as file:
            data = json.load(file)

        # Перетворення вмісту файлу у формат JSON та додавання форматування monospace
        json_content = json.dumps(data, indent=4)
        formatted_content = f'```\n{json_content}\n```'

        # Відправка повідомлення з форматованим вмістом файлу
        await event.respond(formatted_content)
    except Exception as e:
        # Відправка повідомлення про помилку
        await event.respond(f"Сталася помилка при читанні файлу: {str(e)}")


client.run_until_disconnected()
