import os
from PyQt5 import QtWidgets, uic, QtCore


class OrderWidget(QtWidgets.QWidget):
    pay_clicked = QtCore.pyqtSignal(object)
    delete_clicked = QtCore.pyqtSignal(object)

    def __init__(self, order, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'order_widget.ui')
        uic.loadUi(ui_path, self)

        self.order = order

        self.lbl_name.setText(f"{order.name}")
        self.lbl_price.setText(f"Total: {order.total_price:.2f}")

        self.btn_pay.clicked.connect(self.on_pay_clicked)
        self.btn_delete.clicked.connect(self.on_delete_clicked)

    def on_pay_clicked(self):
        """
        Emits the pay_clicked signal.
        :return:
        """
        self.pay_clicked.emit(self.order)

    def on_delete_clicked(self):
        """
        Emits the delete_clicked signal.
        :return:
        """
        self.delete_clicked.emit(self.order)