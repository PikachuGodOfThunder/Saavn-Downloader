#!/usr/bin/python3
# https://github.com/Python-shyam/Saavn-Downloader
# coded by Shyam Sunder Suthar

import os
from json import JSONDecoder
import base64
import logging
import requests
from pyDes import *
from bs4 import BeautifulSoup
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

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

TG_BOT_TOKEN = ""

base_url = 'http://h.saavncdn.com'

json_decoder = JSONDecoder()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
        url_array[obj['album'] + '-' + obj['title'] + '-' + obj['duration']] = dec_url
    return url_array

# this method will save the url with the mp3 to the current working directory
# with the name provided.
def download_song(url, filenameToSave):
    import urllib
    testfile = urllib.URLopener()
    testfile.retrieve(url, filenameToSave)

## The telegram Specific Functions
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi!, please send me a valid Saavn url I will upload to telegram as an audio.")

def echo(bot, update):
    if(update.message.text.startswith("http")):
        url = update.message.text
        a = GetJSONInfo(url)
        b = GetSongURLsArray(a)
        for k in b:
            album, title, duration = k.split("-")
            durl = b[k]
            caption = "Performer: " + album + "\r\nTitle: " + title + "\r\nDownloaded by @SaavnDlBot"
            bot.sendAudio(
                chat_id=update.message.chat_id,
                audio=durl,
                caption=caption,
                duration=duration,
                performer=album,
                title=title,
                timeout=60
            )
    else:
        bot.send_message(chat_id=update.message.chat_id, text="please send me a valid Saavn URL!")

if __name__ == "__main__" :
    updater = Updater(token=TG_BOT_TOKEN)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()
