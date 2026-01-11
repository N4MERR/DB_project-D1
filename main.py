import mysql.connector.locales.eng.client_error
from mysql.connector.plugins import mysql_native_password

import sys
import os
import traceback
from datetime import datetime
from PyQt5 import QtWidgets

from src.data_access_layer.database_connector import DatabaseConnector
from src.presentation_layer.main_window import MainWindow


def excepthook(exc_type, exc_value, exc_tb):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    if getattr(sys, 'frozen', False):
        log_dir = os.path.dirname(sys.executable)
    else:
        log_dir = os.path.dirname(os.path.abspath(__file__))

    log_path = os.path.join(log_dir, "crash_log.txt")

    try:
        with open(log_path, "a") as f:
            f.write(f"\n--- Crash at {datetime.now()} ---\n")
            f.write(error_msg)
            f.write("\n")
    except Exception:
        pass

    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    error_box = QtWidgets.QMessageBox()
    error_box.setIcon(QtWidgets.QMessageBox.Critical)
    error_box.setWindowTitle("Critical Error")
    error_box.setText("An unexpected error occurred.")
    error_box.setInformativeText(f"See crash_log.txt for details.\n\nPath: {log_path}")
    error_box.setDetailedText(error_msg)
    error_box.exec_()

    sys.exit(1)


if __name__ == "__main__":
    sys.excepthook = excepthook

    app = QtWidgets.QApplication(sys.argv)

    try:
        connection = DatabaseConnector().connect()

    except Exception as e:
        sys.excepthook(type(e), e, e.__traceback__)
        sys.exit(1)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())