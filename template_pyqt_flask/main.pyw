
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os, sys, ctypes, time, math, traceback, locale
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
import webbrowser, win32api


HOST_CONST, PORT_CONST = '127.0.0.1', 5090
index_page_url = 'http://{}:{}/'.format(HOST_CONST, str(PORT_CONST))
APP_ID = "application_id"



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        on_click = lambda: webbrowser.open(index_page_url)
        on_quit_clicked = lambda: app.exit()
        self.button = QPushButton("Go Web", self)
        self.button.clicked.connect(on_click)
        self.button2 = QPushButton("Quit", self)
        self.button2.clicked.connect(on_quit_clicked)
        self.root_layout = QVBoxLayout()
        self.root_layout.addSpacing(50)
        self.root_layout.addWidget(self.button)
        self.root_layout.addSpacing(10)
        self.root_layout.addWidget(self.button2)
        self.root_layout.addSpacing(50)
        self.resize(400, 200)
        self.setWindowTitle('Title')
        self.setLayout(self.root_layout)
        self.setFont(QFont("Times", 14, QFont.Normal))

    def signal_handler(self, value):
        print("signal recieved")

    def closeEvent(self, event):
        event.ignore()
        self.hide()

class WebThread(QThread):
    signal_example_variable = pyqtSignal(object)
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        app = Flask(__name__) # , template_folder=os.path.abspath("."))

		# redirection
        app.route("/")(lambda: redirect(url_for('index')))

        @app.route("/index")
        def index():
            return render_template("base.html")

        @app.route("/path1/path2")
        def content_history():
            return render_template("template_name.html", entries=[])

        @app.route("/search", methods=['GET', 'POST'])
        def search():
            if 'q' in request.args:
                query = request.args.get('q')
                return render_template("search.html")
            else:
                return render_template("search.html")

        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(app.root_path, 'static'),
                'favicon.ico', mimetype='image/vnd.microsoft.icon')

        @app.route("/entry<string:entry_id>/start_file", methods=['GET','POST'])
        def entry_startfile(entry_id):
            self.signal_example_variable.emit( int(entry_id) )
            rel_path = request.form.get("rel_path")
            return redirect(url_for('entry', entry_id=entry_id, view=0))

        @app.route("/path2/<string:lowercase_name>")
        def bundle(lowercase_name):
            data = {"first": 1, "second": 2}
            return render_template("tag_data.html", template_name=data)

        @app.context_processor
        def example():
            return dict(myexample='Context processor text') # {{ myexample }}

        app.jinja_env.globals.update(key=lambda x: "example")
        app.jinja_env.globals.update(str=str)

        app.config['TEMPLATES_AUTO_RELOAD'] = True

        app.run(host=HOST_CONST, port=int(PORT_CONST))
        self.exec_()

def get_crashlog_filepath():
    return os.path.join(os.path.dirname(__file__), "crash.log")

def excepthook(exc_type, exc_value, exc_tb):
    # пишем инфу о краше
    if type(exc_tb) is str:
        traceback_lines = exc_tb
    else:
        traceback_lines = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    locale.setlocale(locale.LC_ALL, "russian")
    datetime_string = time.strftime("%A, %d %B %Y %X").capitalize()
    dt = "{0} {1} {0}".format(" "*15, datetime_string)
    dt_framed = "{0}\n{1}\n{0}\n".format("-"*len(dt), dt)

    with open(get_crashlog_filepath(), "a+", encoding="utf8") as crash_log:
        crash_log.write("\n"*10)
        crash_log.write(dt_framed)
        crash_log.write("\n")
        crash_log.write(traceback_lines)
    print(traceback_lines)
    sys.exit()

def show_system_tray(app, icon):
    sti = QSystemTrayIcon(app)
    sti.setIcon(icon)
    @pyqtSlot()
    def on_trayicon_activated(reason):
        if reason == QSystemTrayIcon.Trigger: # если кликнул левой кнопкой
            main_window.show()
        if reason == QSystemTrayIcon.Context: # если правой кнопкой
            menu = QMenu()
            element_1 = menu.addAction("MenuItem #1")
            element_2 = menu.addAction("MenuItem #2")
            show_window = menu.addAction("Show Window")
            menu.addSeparator()
            reboot = menu.addAction("Reboot")
            quit = menu.addAction('Quit')
            action = menu.exec_(QCursor().pos())
            if action == quit:
                app.quit()
            if action == reboot:
                win32api.ShellExecute(0, "open", __file__, None, ".", 1)
                app.quit()
            elif action == element_2:
                pass
            elif action == element_1:
                pass
            elif action == show_window:
                main_window.show()
        if reason == QSystemTrayIcon.DoubleClick:
            pass
        if reason == QSystemTrayIcon.MiddleClick:
            pass
    sti.activated.connect(on_trayicon_activated)
    sti.show()
    return sti


if __name__=="__main__":
    try:
        if sys.stdout is None or sys.executable.endswith("pythonw.exe"):
            sys.stdout = open('nul', 'w')

        app = QApplication(sys.argv)
        myappid = f'sergei_krumas.{APP_ID}.client.2'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        app_icon = QIcon()
        app_icon.addFile('icons/favicon-32x32.png', QSize(32,32))
        app.setWindowIcon(app_icon)
        sti = show_system_tray(app, app_icon)

        main_window = MainWindow()
        main_window.show()

        web_thread = WebThread()
        web_thread.start()

        locale.setlocale(locale.LC_ALL, "RU")

        handler = lambda i: main_window.signal_handler(value=i)
        web_thread.signal_example_variable.connect(handler, Qt.QueuedConnection)

        currentExitCode = app.exec_()
        app = None
        web_thread.exit()
        sti.hide()
        sys.exit(currentExitCode)

    except Exception as e:
        excepthook(type(e), e, traceback.format_exc())
