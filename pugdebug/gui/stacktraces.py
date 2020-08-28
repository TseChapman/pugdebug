# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic and fork's contributors
    license: GNU GPL v3, see LICENSE for more details
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from pugdebug import settings, projects


class PugdebugStacktraceViewer(QTreeWidget):

    item_double_clicked_signal = pyqtSignal(str, int)

    def __init__(self):
        super(PugdebugStacktraceViewer, self).__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(['File', 'Line', 'Where', 'Full filename'])

        self.setColumnWidth(0, 350)
        self.setColumnWidth(1, 100)
        self.setColumnHidden(3, True)

        self.setRootIsDecorated(False)

        self.itemDoubleClicked.connect(self.handle_item_double_clicked)

    def set_stacktraces(self, stacktraces):
        self.clear()

        for stacktrace in stacktraces:
            filename = self.__cut_filename(stacktrace['filename'])
            args = [
                filename,
                stacktrace['lineno'],
                stacktrace['where'],
                stacktrace['filename']
            ]
            item = QTreeWidgetItem(args)
            item.setToolTip(0, stacktrace['filename'])

            self.addTopLevelItem(item)

    def handle_item_double_clicked(self, item, column):
        file = item.text(3)
        line = int(item.text(1))

        self.item_double_clicked_signal.emit(file, line)

    def __cut_filename(self, filename):
        with settings.open_group('project/' + projects.active()):
            path_map = settings.value('path/path_mapping')
            if len(path_map) > 0:
                path_map = path_map.rstrip('/')
                if filename.startswith(path_map):
                    return '~' + filename[len(path_map):]
            else:
                root = settings.value('path/project_root')
                root = root.rstrip('/')
                if filename.startswith(root):
                    return '~' + filename[len(root):]
            return filename
