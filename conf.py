import logging
import os


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename='myapp.log', level=logging.WARNING)
TOKEN = os.environ['TOKEN']
URL = os.environ['URL']

