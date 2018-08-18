#!/usr/bin/python3
# https://github.com/Python-shyam/Saavn-Downloader
# coded by Shyam Sunder Suthar

import os
import sys
from json import JSONDecoder
import base64
import logging
import requests
import re
from pyDes import *
from bs4 import BeautifulSoup
from uuid import uuid4
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity
from telegram.ext import Updater, MessageHandler, Filters, InlineQueryHandler, CommandHandler

# the secret configuration specific things
ENV = bool(os.environ.get('ENV', False))
if ENV:
    from sample_config import Config
else:
    from config import Config

# Key and IV are coded in plaintext in the app when decompiled
# and its preety insecure to decrypt urls to the mp3 at the client side
# these operations should be performed at the server side.
des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0",
                 pad=None, padmode=PAD_PKCS5)

proxy_ip = ''
# set http_proxy from environment
if('http_proxy' in os.environ):
    proxy_ip = os.environ['http_proxy']

proxies = {
    'http': proxy_ip,
    'https': proxy_ip,
}
# proxy setup end here

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
}

TG_BOT_TOKEN = Config.TG_BOT_TOKEN

base_url = 'http://h.saavncdn.com'

json_decoder = JSONDecoder()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def SearchSongs(search_query) :
    search_results = []
    input_url = "https://www.saavn.com/search/" + search_query
    try:
        res = requests.get(input_url, proxies=proxies, headers=headers)
    except Exception as e:
        print('Error accesssing website error: ' + e)
        sys.exit()
    soup = BeautifulSoup(res.text, "lxml")
    a = soup.find_all('li', {'class': 'song-wrap'})
    for k in a:
        b = {}
        songs_json = k.find_all('div', {'class': 'hide song-json'})[0].contents[0]
        obj = json_decoder.decode(songs_json)
        title = obj['title']
        album = obj['album']
        perma_url = obj['perma_url']
        image_url = obj['image_url']
        language = obj['language']
        starring = obj['starring']
        singers = obj['singers']
        music = obj['music']
        year = obj['year']
        tiny_url = obj['tiny_url']
        twitter_url = obj['twitter_url']
        album_url = obj['album_url']
        label = obj['label']
        b["title"] = title + " " + language + " " + year
        b["description"] = album + " " + starring + " " + singers
        b["url"] = perma_url
        b["thumb_url"] = image_url
        search_results.append(b)
    return search_results


def GetJSONInfo(input_url) :
    try:
        res = requests.get(input_url, proxies=proxies, headers=headers)
    except Exception as e:
        print('Error accesssing website error: ' + e)
        sys.exit()
    soup = BeautifulSoup(res.text, "lxml")
    # Encrypted url to the mp3 are stored in the webpage
    songs_json = soup.find_all('div', {'class': 'hide song-json'})
    return songs_json


def GetSongURLsArray(songs_json) :
    url_array = {}
    for song in songs_json:
        # obj has the song info
        obj = json_decoder.decode(song.text)
        # this is that part which fetches the audio file
        enc_url = base64.b64decode(obj['url'].strip())
        dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
        dec_url = base_url + dec_url.replace('mp3:audios', '') + '.mp3'
        # returning it in appropriate format
        url_array[
            obj['album'] + ':=:' +
            obj['title'] + ':=:' +
            obj['duration'] + ':=:' +
            obj['image_url']
        ] = dec_url
    return url_array


# this method will save the url with the mp3 to the current working directory
# with the name provided.
def DownLoadFile(url, file_name):
    if not os.path.exists(file_name):
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=Config.CHUNK_SIZE):
                fd.write(chunk)
    return file_name


# the Telegram trackings
from chatbase import Message

def TRChatBase(chat_id, message_text, intent):
    msg = Message(api_key=Config.CBTOKEN,
              platform="Telegram",
              version="1.3",
              user_id=chat_id,
              message=message_text,
              intent=intent)
    resp = msg.send()


## The telegram Specific Functions
def start(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "start")
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        text="Hi! 🤓 , please send me a valid Saavn url I will upload to telegram as an audio 😉. Use @SaavnDLRobot inline for searching songs. 🤒 "
    )
def about(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "about")
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        text="A Bot By @AbinPauIZackariah ❤️"
    )

def echo(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "echo")
    if(update.message.text.startswith("http")):
        url = update.message.text
        a = GetJSONInfo(url)
        b = GetSongURLsArray(a)
        for k in b:
            album, title, duration, image_url = k.split(":=:")
            durl = b[k]
            local_file_name = str(update.message.chat_id) + ".mp3"
            local_thumb_name = str(update.message.chat_id) + ".jpg"
            real_local_file_name = DownLoadFile(durl, local_file_name)
            real_local_thumb_image = DownLoadFile(image_url, local_thumb_name)
            caption = "Performer: " + album + "\r\nTitle: " + title + "\r\nDownloaded by @SaavnDLRoBot"
            bot.send_audio(
                chat_id=update.message.chat_id,
                audio=open(real_local_file_name, "rb"),
                caption=caption,
                duration=duration,
                performer=album,
                title=title,
                thumb=open(real_local_thumb_image, "rb"),
                reply_to_message_id=update.message.message_id
            )
            # clean up after send
            os.remove(real_local_file_name)
            os.remove(real_local_thumb_image)
            # so many media files are being send
            # we only need the first result
            break
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text="please send me a valid Saavn URL!"
        )


def inlinequery(bot, update):
    TRChatBase(update.inline_query.from_user.id, update.inline_query.query, "InLine")
    """Handle the inline query."""
    query = update.inline_query.query
    search_results = SearchSongs(query)
    results = []
    for k in search_results:
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=k["title"],
                description=k["description"],
                thumb_url=k["thumb_url"],
                # thumb_width=,
                # thumb_height=,
                input_message_content=InputTextMessageContent(k["url"])
            )
        )
    update.inline_query.answer(results)


if __name__ == "__main__" :
    updater = Updater(token=TG_BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(
        Filters.entity(MessageEntity.URL) |
        Filters.entity(MessageEntity.TEXT_LINK),
        echo
    ))
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    if ENV:
        updater.start_webhook(listen="0.0.0.0", port=Config.PORT, url_path=TG_BOT_TOKEN)
        updater.bot.set_webhook(url=Config.URL + TG_BOT_TOKEN)
    else:
        updater.start_polling()
    updater.idle()
