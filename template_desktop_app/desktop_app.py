
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os
import sys
import ctypes
import time
import math
import traceback
import locale
import argparse
import subprocess

from on_windows_startup import is_app_in_startup, add_to_startup, remove_from_startup


class Globals():
    DEBUG = True

    AFTERCRASH = False

    VERSION_INFO = "v0.1"
    AUTHOR_INFO = "by Sergei Krumas"

    APP_NAME = "APPLICATION NAME"
    APP_NAME_ID = "APP_NAME" #for filename, only chars, digits and unserscore

class StartWindow(QMainWindow):
    some_signal = pyqtSignal()

    settings_checkbox = """
        QCheckBox {
            font-size: 18px;
            font-family: 'Consolas';
            color: white;
            font-weight: normal;
        }
        QCheckBox::indicator:unchecked {
            background: gray;
        }
        QCheckBox::indicator:checked {
            background: green;
        }
        QCheckBox:checked {
            background-color: rgba(150, 150, 150, 50);
            color: rgb(100, 255, 100);
        }
        QCheckBox:unchecked {
            color: gray;
        }
    """

    def __init__(self, *args):
        super().__init__(*args)


        self.STARTUP_CONFIG = (
            f'{Globals.APP_NAME_ID}_launcher',
            os.path.join(os.path.dirname(__file__), "desktop_app_launcher.pyw")
        )

        self.root_layout = QVBoxLayout()
        self.child_layout = QVBoxLayout()

        self.setStyleSheet("QPushButton{ padding: 10px 20px; font: 11pt; margin: 0 100; }")

        self.title_label = QLabel(f"<center>{Globals.APP_NAME}</center>")
        self.title_label.setStyleSheet("font-weight:bold; font-size: 30pt; color: gray;")

        self.black_text_label = QLabel("<center> black text label</center>" )
        self.black_text_label.setStyleSheet("font-weight:bold; font-size: 18pt; color: black; font-family: consolas;")

        first_btn = QPushButton("                 Start XXXXXX                 ")
        first_btn.clicked.connect( lambda: None )
        second_btn = QPushButton("                 Start VVVVVV                 ")
        second_btn.clicked.connect( self.second_btn_handler )

        self.child_layout.addWidget(self.title_label)
        self.child_layout.addWidget(self.black_text_label)

        self.gray_text_label = QLabel("<center>gray_label text</center>")
        style_sheet = "font: 13pt; font-weight:bold; color: #aaaaaa; font-family: consolas;"
        self.gray_text_label.setStyleSheet(style_sheet)

        self.child_layout.addWidget( self.gray_text_label )
        self.child_layout.addSpacing(35)

        self.child_layout.addWidget(first_btn)
        self.child_layout.addWidget(second_btn)


        chbx_3 = QCheckBox("Запускать при старте Windows")
        chbx_3.setStyleSheet(self.settings_checkbox)
        chbx_3.setChecked(is_app_in_startup(self.STARTUP_CONFIG[0]))
        chbx_3.stateChanged.connect(lambda: self.handle_windows_startup_chbx(chbx_3))
        layout_3 = QVBoxLayout()
        layout_3.setAlignment(Qt.AlignCenter)
        layout_3.addWidget(chbx_3)

        self.child_layout.addSpacing(50)
        self.child_layout.addLayout(layout_3)

        self.root_layout.addSpacing(50)
        self.root_layout.addLayout(self.child_layout)
        self.root_layout.addSpacing(50)

        main_widget = QWidget()
        main_widget.setLayout(self.root_layout)

        self.setWindowTitle(f'{Globals.APP_NAME}')
        self.setCentralWidget(main_widget)
        self.setFont(QFont("Times", 14, QFont.Normal))
        self.show()
        self.afterShow()

        self.some_signal.connect(lambda: None)

    def second_btn_handler(self):
        # crash simulator
        1/0

    def handle_windows_startup_chbx(self, sender):
        if sender.isChecked():
            add_to_startup(*self.STARTUP_CONFIG)
        else:
            remove_from_startup(self.STARTUP_CONFIG[0])

    def afterShow(self):
        self.resize(100, 0)
        app = QApplication.instance()
        # desktop.width()//2 -- because we have two monitors
        m = 1 #first monitor
        # m = 3 #second monitor
        x = (app.desktop().width() // 2*m - self.frameSize().width()) // 2
        y = (app.desktop().height() - self.frameSize().height()) // 2
        self.move(x, y)


def show_system_tray(app, icon):
    sti = QSystemTrayIcon(app)
    sti.setIcon(icon)
    sti.setToolTip(f"{Globals.APP_NAME} {Globals.VERSION_INFO} {Globals.AUTHOR_INFO}")
    app.setProperty("stray_icon", sti)
    @pyqtSlot()
    def on_trayicon_activated(reason):
        if reason == QSystemTrayIcon.Trigger: # левая кнопка мыши
            pass
        if reason == QSystemTrayIcon.Context: # правая кнопка мыши
            menu = QMenu()
            menu.addSeparator()
            quit = menu.addAction('Quit')
            action = menu.exec_(QCursor().pos())
            if action == quit:
                app = QApplication.instance()
                app.quit()
        if reason == QSystemTrayIcon.DoubleClick:
            pass
        if reason == QSystemTrayIcon.MiddleClick:
            pass
    sti.activated.connect(on_trayicon_activated)
    sti.show()
    return sti


def get_crashlog_filepath():
    return os.path.join(os.path.dirname(__file__), "crash.log")

def excepthook(exc_type, exc_value, exc_tb):
    if isinstance(exc_tb, str):
        traceback_lines = exc_tb
    else:
        traceback_lines = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    # locale.setlocale(locale.LC_ALL, "russian")
    datetime_string = time.strftime("%A, %d %B %Y %X").capitalize()
    dt = "{0} {1} {0}".format(" "*15, datetime_string)
    dt_framed = "{0}\n{1}\n{0}\n".format("-"*len(dt), dt)
    with open(get_crashlog_filepath(), "a+", encoding="utf8") as crash_log:
        crash_log.write("\n"*10)
        crash_log.write(dt_framed)
        crash_log.write("\n")
        crash_log.write(traceback_lines)
    print("*** excepthook info ***")
    print(traceback_lines)
    app = QApplication.instance()
    if app:
        stray_icon = app.property("stray_icon")
        if stray_icon:
            stray_icon.hide()
    if not Globals.DEBUG:
        _restart_app(aftercrash=True)
    sys.exit()

def _restart_app(aftercrash=False):
    if aftercrash:
        subprocess.Popen([sys.executable, sys.argv[0], "-aftercrash"])
    else:
        subprocess.Popen([sys.executable, sys.argv[0]])

def _main():

    args = sys.argv
    os.chdir(os.path.dirname(__file__))
    sys.excepthook = excepthook

    if not Globals.DEBUG:
        RERUN_ARG = '-rerun'
        if (RERUN_ARG not in sys.argv) and ("-aftercrash" not in sys.argv):
            subprocess.Popen([sys.executable, "-u", *sys.argv, RERUN_ARG])
            sys.exit()

    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument('default_parm', nargs='?', default=None)
    parser.add_argument('-rerun', help="", action="store_true")
    parser.add_argument('-aftercrash', help="", action="store_true")
    args = parser.parse_args(sys.argv[1:])
    if args.aftercrash:
        Globals.AFTERCRASH = True

    if Globals.AFTERCRASH:
        filepath = get_crashlog_filepath()
        sub_msg = f"Информация о краше сохранена в файл\n\t{filepath}"
        msg = f"Программа упала. Application crash.\n{sub_msg}\n\nПерезапустить? Restart app?"
        ret = QMessageBox.question(None, 'Error', msg, QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            _restart_app()
        sys.exit(0)

    appid = f'sergei_krumas.{Globals.APP_NAME}.client.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    path_icon = os.path.abspath(os.path.join(os.path.dirname(__file__), "icon.png"))
    icon = QIcon(path_icon)
    app.setWindowIcon(icon)

    start_window = StartWindow()

    stray_icon = show_system_tray(app, icon)

    app.exec_()

    # после закрытия апликухи
    stray_icon = app.property("stray_icon")
    if stray_icon:
        stray_icon.hide()

    sys.exit()


def main():
    try:
        _main()
    except Exception as e:
        excepthook(type(e), e, traceback.format_exc())

if __name__ == '__main__':
    main()
