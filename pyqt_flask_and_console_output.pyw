







from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from flask import Flask, render_template, redirect, url_for, request, send_from_directory, render_template_string, jsonify
import os
import webbrowser
import sys
import time

HOST_CONST, PORT_CONST = '127.0.0.1', 5188

class WebThread(QThread):

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        app = Flask(__name__)

        @app.route('/')
        def index():
            time_stamp = time.time()
            return f"Hello, World! {time_stamp}"

        app.run(host=HOST_CONST, port=int(PORT_CONST))

        self.exec_()

if __name__ == "__main__":

    if sys.executable.endswith("pythonw.exe") or sys.stdout is None:
        # если нет стандартного ввода-вывода, то подсовываем фейковый,
        # чтобы приложение не упало при попытке веб-сервера
        # написать что-нибудь в стандартный ввод-вывод
        f = open(os.devnull, 'w')
        sys.stdout = f
        sys.stderr = f
        sys.stdin = f
        sys.__stdout__ = f
        sys.__stderr__ = f
        sys.__stdin__ = f

    app = QApplication(sys.argv)

    web_thread = WebThread()
    web_thread.start()

    webbrowser.open('http://{}:{}/'.format(HOST_CONST, str(PORT_CONST)))

    app.exec_()
    web_thread.exit()
    sys.exit(0)
