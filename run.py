import app.handlers as handlers
import os
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

if __name__ == "__main__":
    print('TOKEN=', os.environ['BOT_TOKEN'])
    handlers.bot.run(os.environ['BOT_TOKEN'])
