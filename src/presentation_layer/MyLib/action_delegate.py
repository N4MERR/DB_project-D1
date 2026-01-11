from PyQt5 import QtWidgets, QtCore, QtGui


class ActionDelegate(QtWidgets.QStyledItemDelegate):
    edit_clicked = QtCore.pyqtSignal(object)
    delete_clicked = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.btn_spacing = 5
        self.btn_width = 60
        self.btn_height = 25

    def paint(self, painter, option, index):
        if not index.data(QtCore.Qt.UserRole):
            return

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        cell_rect = option.rect
        total_width = (self.btn_width * 2) + self.btn_spacing
        start_x = cell_rect.x() + (cell_rect.width() - total_width) / 2
        start_y = cell_rect.y() + (cell_rect.height() - self.btn_height) / 2

        edit_rect = QtCore.QRect(int(start_x), int(start_y), self.btn_width, self.btn_height)
        delete_rect = QtCore.QRect(int(start_x + self.btn_width + self.btn_spacing), int(start_y), self.btn_width,
                                   self.btn_height)

        path_edit = QtGui.QPainterPath()
        path_edit.addRoundedRect(QtCore.QRectF(edit_rect), 4, 4)
        painter.fillPath(path_edit, QtGui.QColor("#64B5F6"))
        painter.setPen(QtCore.Qt.white)
        painter.drawText(edit_rect, QtCore.Qt.AlignCenter, "Edit")

        path_delete = QtGui.QPainterPath()
        path_delete.addRoundedRect(QtCore.QRectF(delete_rect), 4, 4)
        painter.fillPath(path_delete, QtGui.QColor("#E57373"))
        painter.setPen(QtCore.Qt.white)
        painter.drawText(delete_rect, QtCore.Qt.AlignCenter, "Delete")

        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            obj_data = index.data(QtCore.Qt.UserRole)

            cell_rect = option.rect
            total_width = (self.btn_width * 2) + self.btn_spacing
            start_x = cell_rect.x() + (cell_rect.width() - total_width) / 2
            start_y = cell_rect.y() + (cell_rect.height() - self.btn_height) / 2

            edit_rect = QtCore.QRect(int(start_x), int(start_y), self.btn_width, self.btn_height)
            delete_rect = QtCore.QRect(int(start_x + self.btn_width + self.btn_spacing), int(start_y), self.btn_width,
                                       self.btn_height)

            if edit_rect.contains(event.pos()):
                self.edit_clicked.emit(obj_data)
                return True
            elif delete_rect.contains(event.pos()):
                self.delete_clicked.emit(obj_data)
                return True
        return False