import os

class Config(object):
    # get a token from https://chatbase.com
    CHAT_BASE_TOKEN = os.environ.get('CHAT_BASE_TOKEN', None)
    # get a token from @BotFather
    TG_BOT_TOKEN = os.environ.get('TOKEN', None)
    # required for running on Heroku
    URL = os.environ.get('URL', "")
    PORT = int(os.environ.get('PORT', 5000))
