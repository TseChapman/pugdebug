# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic and fork's contributors
    license: GNU GPL v3, see LICENSE for more details
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QToolBar, QMenuBar, QDockWidget,
                             QAction)
from PyQt5.QtGui import QKeySequence

from pugdebug.gui.search import PugdebugFileSearchWindow
from pugdebug.gui.documents import PugdebugDocumentViewer
from pugdebug.gui.variables import PugdebugVariableViewer
from pugdebug.gui.stacktraces import PugdebugStacktraceViewer
from pugdebug.gui.breakpoints import PugdebugBreakpointViewer
from pugdebug.gui.expressions import PugdebugExpressionViewer
from pugdebug.gui.statusbar import PugdebugStatusBar
from pugdebug import settings, file_browser, projects


class PugdebugMainWindow(QMainWindow):

    search_file_selected_signal = pyqtSignal(str)

    def __init__(self):
        super(PugdebugMainWindow, self).__init__()
        self.setObjectName("pugdebug")

        self.file_browser = file_browser.FileBrowserView()
        self.projects_browser = projects.ProjectsBrowserView()
        self.document_viewer = PugdebugDocumentViewer()
        self.variable_viewer = PugdebugVariableViewer()
        self.breakpoint_viewer = PugdebugBreakpointViewer()
        self.stacktrace_viewer = PugdebugStacktraceViewer()
        self.expression_viewer = PugdebugExpressionViewer()
        self.file_search_window = PugdebugFileSearchWindow(self)

        self.setCentralWidget(self.document_viewer)

        self.setup_gui_elements()

        self.restoreGeometry(settings.value('window/geometry'))
        self.restoreState(settings.value('window/state'))

        self.update_window_title()
        projects.active_project_changed().connect(self.update_window_title)

    def closeEvent(self, event):
        settings.set_value('window/geometry', self.saveGeometry())
        settings.set_value('window/state', self.saveState())

        super(PugdebugMainWindow, self).closeEvent(event)

    def setup_gui_elements(self):
        self.setup_docks()

        self.setup_file_actions()

        self.setup_actions()
        self.toggle_actions(False)

        self.setup_search_actions()

        self.setup_toolbar()
        self.setup_menubar()
        self.setup_statusbar()

    def setup_statusbar(self):
        self.permanent_statusbar = PugdebugStatusBar()
        self.statusBar().addPermanentWidget(self.permanent_statusbar)
        self.set_debugging_status(0)

    def setup_docks(self):
        self.__add_dock_widget(
            self.file_browser,
            "File Browser",
            Qt.LeftDockWidgetArea
        )

        self.__add_dock_widget(
            self.projects_browser,
            "Projects Browser",
            Qt.LeftDockWidgetArea
        )

        self.__add_dock_widget(
            self.variable_viewer,
            "Variables",
            Qt.RightDockWidgetArea
        )

        self.__add_dock_widget(
            self.expression_viewer,
            "Expressions",
            Qt.RightDockWidgetArea
        )

        self.__add_dock_widget(
            self.breakpoint_viewer,
            "Breakpoints",
            Qt.BottomDockWidgetArea
        )

        self.__add_dock_widget(
            self.stacktrace_viewer,
            "Stacktraces",
            Qt.BottomDockWidgetArea
        )

    def setup_file_actions(self):
        self.new_project_action = QAction("&New project...", self)
        self.new_project_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_project_action.triggered.connect(projects.show_add_dialog)

        self.show_settings_action = QAction("&Settings", self)
        self.show_settings_action.triggered.connect(settings.show_edit_dialog)

        self.quit_action = QAction("&Quit", self)
        self.quit_action.setShortcut(QKeySequence("Alt+F4"))
        self.quit_action.triggered.connect(self.close)

    def setup_actions(self):
        self.start_listening_action = QAction("Start listening", self)
        self.start_listening_action.setToolTip(
            "Start listening for new connections (F1)"
        )
        self.start_listening_action.setStatusTip(
            "Start listening for incomming connections. Shortcut: F1"
        )
        self.start_listening_action.setShortcut(QKeySequence("F1"))

        self.stop_listening_action = QAction("Stop listening", self)
        self.stop_listening_action.setToolTip(
            "Stop listening for new connections (F2)"
        )
        self.stop_listening_action.setStatusTip(
            "Stop listening to incomming connections. Shortcut: F2"
        )
        self.stop_listening_action.setShortcut(QKeySequence("F2"))

        self.stop_debug_action = QAction("Stop", self)
        self.stop_debug_action.setToolTip("Stop debugging (F3)")
        self.stop_debug_action.setStatusTip(
            "Stop debugging the current request. Shortcut: F3"
        )
        self.stop_debug_action.setShortcut(QKeySequence("F3"))

        self.detach_debug_action = QAction("Detach", self)
        self.detach_debug_action.setToolTip("Detach debugger (F4)")
        self.detach_debug_action.setStatusTip(
            "Detach debugger from the current request."
            " Shortcut: F4"
        )
        self.detach_debug_action.setShortcut(QKeySequence("F4"))

        self.run_debug_action = QAction("Run", self)
        self.run_debug_action.setToolTip("Start/resume the script (F5)")
        self.run_debug_action.setStatusTip(
            "Start or resume the script until a new breakpoint is reached, "
            "or the end of the script is " "reached. Shortcut: F5"
        )
        self.run_debug_action.setShortcut(QKeySequence("F5"))

        self.step_over_action = QAction("Step Over", self)
        self.step_over_action.setToolTip("Step over the next statement (F6)")
        self.step_over_action.setStatusTip(
            "Step to the next statement, if "
            "there is a function call involved it will break on the statement "
            "after the function call in the same scope as from where the "
            "command was issued. Shortcut: F6"
        )
        self.step_over_action.setShortcut(QKeySequence("F6"))

        self.step_into_action = QAction("Step In", self)
        self.step_into_action.setToolTip("Step into the next statement (F7)")
        self.step_into_action.setStatusTip(
            "Step to the next statement, if there is a function call involved "
            "it will break on the first statement in that function. "
            "Shortcut: F7"
        )
        self.step_into_action.setShortcut(QKeySequence("F7"))

        self.step_out_action = QAction("Step Out", self)
        self.step_out_action.setToolTip("Step out of the current scope (F8)")
        self.step_out_action.setStatusTip(
            "Step out of the current scope and breaks on the next statement. "
            "Shortcut: F8"
        )
        self.step_out_action.setShortcut(QKeySequence("F8"))

    def setup_search_actions(self):
        self.file_search_action = QAction("&File search...", self)
        self.file_search_action.setToolTip(
            "Search for files in the current project"
        )
        self.file_search_action.setStatusTip(
            "Search for files. Shortcut: Ctrl+T"
        )
        self.file_search_action.setShortcut(QKeySequence("Ctrl+T"))
        self.file_search_action.triggered.connect(self.file_search_window.exec)

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setObjectName("main-toolbar")

        toolbar.addAction(self.start_listening_action)
        toolbar.addAction(self.stop_listening_action)
        toolbar.addSeparator()
        toolbar.addAction(self.stop_debug_action)
        toolbar.addAction(self.detach_debug_action)
        toolbar.addSeparator()
        toolbar.addAction(self.run_debug_action)
        toolbar.addAction(self.step_over_action)
        toolbar.addAction(self.step_into_action)
        toolbar.addAction(self.step_out_action)

        self.addToolBar(toolbar)

    def setup_menubar(self):
        menu_bar = QMenuBar()

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.new_project_action)
        file_menu.addAction(self.show_settings_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        view_menu = menu_bar.addMenu("&View")

        dockWidgets = self.findChildren(QDockWidget)
        for widget in dockWidgets:
            view_menu.addAction(widget.toggleViewAction())

        debug_menu = menu_bar.addMenu("&Debug")
        debug_menu.addAction(self.start_listening_action)
        debug_menu.addAction(self.stop_listening_action)
        debug_menu.addSeparator()
        debug_menu.addAction(self.stop_debug_action)
        debug_menu.addAction(self.detach_debug_action)
        debug_menu.addSeparator()
        debug_menu.addAction(self.run_debug_action)
        debug_menu.addAction(self.step_over_action)
        debug_menu.addAction(self.step_into_action)
        debug_menu.addAction(self.step_out_action)

        search_menu = menu_bar.addMenu("&Search")
        search_menu.addAction(self.file_search_action)

        self.setMenuBar(menu_bar)

    def toggle_actions(self, enabled):
        self.stop_debug_action.setEnabled(enabled)
        self.detach_debug_action.setEnabled(enabled)
        self.run_debug_action.setEnabled(enabled)
        self.step_over_action.setEnabled(enabled)
        self.step_into_action.setEnabled(enabled)
        self.step_out_action.setEnabled(enabled)

        self.start_listening_action.setEnabled(not enabled)

    def get_file_browser(self):
        return self.file_browser

    def get_projects_browser(self):
        return self.projects_browser

    def get_document_viewer(self):
        return self.document_viewer

    def get_variable_viewer(self):
        return self.variable_viewer

    def get_stacktrace_viewer(self):
        return self.stacktrace_viewer

    def get_breakpoint_viewer(self):
        return self.breakpoint_viewer

    def get_expression_viewer(self):
        return self.expression_viewer

    def update_window_title(self):
        self.setWindowTitle("pugdebug / " + projects.active())

    def set_debugging_status(self, status):
        self.permanent_statusbar.set_debugging_status(status)

    def __add_dock_widget(self, widget, title, area):
        dw = QDockWidget(title, self)
        object_name = "dock-widget-%s" % title.lower().replace(" ", "-")
        dw.setObjectName(object_name)
        dw.setWidget(widget)
        self.addDockWidget(area, dw)
