from ApiDataHandler import CApiDataHandler
from GraphicalWindow import CGraphicalWindow

import os
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    API_KEY = os.getenv('API_KEY')

    data_handler = CApiDataHandler(API_KEY)
    graphical_window = CGraphicalWindow(data_handler)
    graphical_window.start_and_run()

