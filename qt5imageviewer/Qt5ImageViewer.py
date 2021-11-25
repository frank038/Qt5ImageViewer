#!/usr/bin/python3
# -*- coding: utf-8 -*-
# V. 0.7.0

from PyQt5.QtCore import Qt, QMimeDatabase, QEvent, QSize
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon, QTransform, QMovie
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog
from PIL import Image, ImageQt

dialog_filters = 'Images (*.tga *.png *.jpeg *.jpg *.bmp *.gif *.svg *.dds *.eps *.ico *.tiff *.tif *.webp *.wmf *.jp2 *.pbm *.pgm *.ppm *.xbm *.xpm);;All files (*)'

# python list e.g. ["gif", "ppm"] - will be used by the pyqt5 decoders
exclude_from_pil = ["gif"]

WW = 800
HH = 600
try:
    with open ("winsize.cfg", "r") as ifile:
        fcontent = ifile.readline()
        WW1, HH1 = fcontent.split(";")
        WW = int(WW1)
        HH = int(HH1.strip())
except:
    try:
        with open("winsize.cfg", "w") as ifile:
            ifile.write("{};{}".format(WW, HH))
    except:
        pass


class QImageViewer(QMainWindow):
    def __init__(self, ipath):
        super().__init__()
        #
        self.WW = WW
        self.HH = HH
        self.resize(self.WW, self.HH)
        #
        self.ipath = ipath
        self.curr_dir = None
        if self.ipath:
            self.curr_dir = os.path.dirname(self.ipath)
        self.printer = QPrinter()
        # actual scaling factor
        self.scaleFactor = 0.0
        # starting scaling factor
        self.scaleFactorStart = 0.0
        #
        # a gif can be animated
        self.is_animated = False
        self.ianimated = None
        #
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        #
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)
        self.scrollArea.installEventFilter(self)
        self.last_time_move_h = 0
        self.last_time_move_v = 0
        self.hscrollbar = self.scrollArea.horizontalScrollBar()
        self.vscrollbar = self.scrollArea.verticalScrollBar()
        #
        self.setCentralWidget(self.scrollArea)
        #
        self.directory_content = []
        if self.curr_dir:
            self.directory_content = os.listdir(self.curr_dir)
        #
        self.directory_current_idx = None
        #
        self.createActions()
        self.createMenus()
        #
        self.setWindowTitle("Image Viewer")
        self.setWindowIcon(QIcon("QImageViewer.svg"))
        #
        self.layout().setContentsMargins(0,0,0,0)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.imageLabel.setContentsMargins(0,0,0,0)
        # 
        if self.ipath:
            ret = self.on_open(self.ipath)
            if ret == -1:
                sys.exit(qApp.closeAllWindows())
        
    
    def open(self):
        options = QFileDialog.Options()
        # fileName, _ = QFileDialog.getOpenFileName(self, 'Open File', os.path.expanduser("~"), dialog_filters, options=options)
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open File', self.curr_dir, dialog_filters, options=options)
        if fileName:
            self.ipath = fileName
            ret = self.on_open(self.ipath)
            if ret == -1:
                sys.exit(qApp.closeAllWindows())
    
    # 
    def on_open(self, fileName):
        ppixmap = None
        self.is_animated = False
        if self.ianimated:
            self.ianimated.stop()
            self.ianimated = None
        try:
            image = Image.open(fileName)
            ppixmap = ImageQt.toqpixmap(image)
        except Exception as E:
            pass
        #
        try:
            if os.path.basename(fileName).split(".")[1] in exclude_from_pil:
                ppixmap = None
        except:
            pass
        #
        if not ppixmap:
            try:
                image = QImage(fileName)
                if image.isNull():
                    QMessageBox.information(self, "Image Viewer", "Cannot load %s" % fileName)
                    return -1
                # 
                image_type = QMimeDatabase().mimeTypeForFile(fileName, QMimeDatabase.MatchContent).name()
                if image_type == "image/gif":
                    self.is_animated = True
                else:
                    ppixmap = QPixmap.fromImage(image)
            except Exception as E:
                QMessageBox.information(self, "Image Viewer", "Error %s." % str(E))
                return -1
        # 
        self.ipath = fileName
        # set the working dir
        self.curr_dir = os.path.dirname(self.ipath)
        # 
        self.directory_content = os.listdir(self.curr_dir)
        # set the picture index in the list
        self.directory_current_idx = self.directory_content.index(os.path.basename(self.ipath))
        #
        self.scaleFactor = 1.0
        #
        if self.is_animated:
            self.ianimated = QMovie(fileName)
            self.imageLabel.setMovie(self.ianimated)
            self.ianimated.start()
            # 
            ppixmap = self.ianimated.currentPixmap()
            self.ianimated.stop()
            #
            image_width = ppixmap.width()
            image_height = ppixmap.height()
            image_depth = ppixmap.depth()
            if image_width >= image_height:
                if image_width > self.WW and not image_height > self.HH:
                    self.scaleFactor = (self.WW-2)/image_width
                elif image_height > self.HH:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
            else:
                if image_height > self.HH and not image_width > self.WW:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
                elif image_width > self.WW:
                    self.scaleFactor = (self.WW-2)/image_width
            self.imageLabel.resize(self.scaleFactor * ppixmap.size())
            self.scaleFactorStart = self.scaleFactor
            #
            self.ianimated.start()
        else:
            self.imageLabel.setPixmap(ppixmap)
            #
            image_width = ppixmap.width()
            image_height = ppixmap.height()
            image_depth = ppixmap.depth()
            if image_width >= image_height:
                if image_width > self.WW and not image_height > self.HH:
                    self.scaleFactor = (self.WW-2)/image_width
                elif image_height > self.HH:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
            else:
                if image_height > self.HH and not image_width > self.WW:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
                elif image_width > self.WW:
                    self.scaleFactor = (self.WW-2)/image_width
            # 
            self.imageLabel.resize(self.scaleFactor * ppixmap.size())
            self.scaleFactorStart = self.scaleFactor
        #
        self.imageLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        #
        self.scrollArea.setVisible(True)
        self.scrollArea.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # 
        self.printAct.setEnabled(True)
        #
        self.updateActions()
        self.infoAct.setEnabled(True)
        # 
        self.setWindowTitle("Image Viewer - {} - x{}".format(os.path.basename(self.ipath), round(self.scaleFactor, 2)))
        
    
    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())
    
    
    def info_(self):
        if self.is_animated:
            pw = ""
            ph = ""
            pd = ""
            try:
                ppixmap = self.ianimated.currentPixmap()
                pw = ppixmap.width()
                ph = ppixmap.height()
                pd = ppixmap.depth()
            except:
                pw = self.ianimated.frameRect().width()
                ph = self.ianimated.frameRect().height()
                pd = "Unknown"
            imime = QMimeDatabase().mimeTypeForFile(self.ipath, QMimeDatabase.MatchDefault)
            imime_name = imime.name()
            QMessageBox.information(self, "Image Info", "Name: {}\nWidth: {}\nHeight: {}\nDepth: {}\nType: {}".format(os.path.basename(self.ipath), pw, ph, pd, imime_name))
            return
        # 
        ppixmap = self.imageLabel.pixmap()
        if not ppixmap.isNull():
            pw = ppixmap.width()
            ph = ppixmap.height()
            pd = ppixmap.depth()
            imime = QMimeDatabase().mimeTypeForFile(self.ipath, QMimeDatabase.MatchDefault)
            imime_name = imime.name()
            QMessageBox.information(self, "Image Info", "Name: {}\nWidth: {}\nHeight: {}\nDepth: {}\nType: {}".format(os.path.basename(self.ipath), pw, ph, pd, imime_name))
    
    
    def zoomIn(self):
        self.scaleImage(1.25)
    
    
    def zoomOut(self):
        self.scaleImage(0.8)
    
    
    def normalSize(self):
        self.scaleImage(self.scaleFactorStart/self.scaleFactor)
    
    
    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
        self.infoAct = QAction("&Info", self, shortcut="Ctrl+I", enabled=False, triggered=self.info_)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
    

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.infoAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        #
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
    

    def updateActions(self):
        self.zoomInAct.setEnabled(True)
        self.zoomOutAct.setEnabled(True)
        self.normalSizeAct.setEnabled(True)


    def scaleImage(self, factor):
        self.scaleFactor *= factor
        if self.is_animated:
            ppixmap = self.ianimated.currentPixmap()
        else:
            ppixmap = self.imageLabel.pixmap()
        self.imageLabel.resize(self.scaleFactor * ppixmap.size())
        #
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)
        #
        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)
        #
        self.setWindowTitle("Image Viewer - {} - x{}".format(os.path.basename(self.ipath), round(self.scaleFactor, 2)))
    
    
    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))
    
    #
    def closeEvent(self, event):
        self.on_close()
    
    #
    def on_close(self):
        new_w = self.size().width()
        new_h = self.size().height()
        if new_w != int(WW) or new_h != int(HH):
            try:
                ifile = open("winsize.cfg", "w")
                ifile.write("{};{}".format(new_w, new_h))
                ifile.close()
            except Exception as E:
                pass
        qApp.quit()
    
    
    # load the next or previous image in the folder
    def keyNav(self, incr_idx):
        if self.ianimated:
            self.ianimated.stop()
            self.ianimated = None
            self.is_animated = False
        #
        len_folder = len(self.directory_content)
        new_idx = self.directory_current_idx + incr_idx
        # 
        if incr_idx == -1:
            ttype = "d"
        else:
            ttype = "i"
        self.on_open2(new_idx, ttype)
    
    # self.keyNav
    def on_open2(self, new_idx, ttype):
        len_folder = len(self.directory_content)
        if ttype == "i":
            incr_idx = 1
        elif ttype == "d":
            incr_idx = -1
        ppixmap = None
        while not ppixmap:
            if new_idx > len_folder - 1:
                new_idx = 0
            elif new_idx < 0:
                new_idx = len_folder - 1
            #
            nitem = self.directory_content[new_idx]
            # fileName = None
            fileName = os.path.join(self.curr_dir, nitem)
            #
            try:
                image = Image.open(fileName)
                ppixmap = ImageQt.toqpixmap(image)
            except Exception as E:
                pass
            # 
            try:
                if os.path.basename(fileName).split(".")[1] in exclude_from_pil:
                    ppixmap = None
            except:
                pass
            #
            if not ppixmap:
                try:
                    image = QImage(fileName)
                    if image.isNull():
                        new_idx += incr_idx
                    else:
                        image_type = QMimeDatabase().mimeTypeForFile(fileName, QMimeDatabase.MatchContent).name()
                        if image_type == "image/gif":
                            self.is_animated = True
                            ppixmap = True
                        else:
                            ppixmap = QPixmap.fromImage(image)
                except Exception as E:
                    pass
        #
        self.ipath = fileName
        # set the new working dir
        if os.path.dirname(self.ipath) != self.curr_dir:
            self.curr_dir = os.path.dirname(self.ipath)
            self.directory_content = os.listdir(self.curr_dir)
        # set the picture index in the list
        self.directory_current_idx = new_idx
        #
        self.scaleFactor = 1.0
        #
        if self.is_animated:
            self.ianimated = QMovie(fileName)
            self.imageLabel.setMovie(self.ianimated)
            self.ianimated.start()
            # 
            ppixmap = self.ianimated.currentPixmap()
            self.ianimated.stop()
            #
            image_width = ppixmap.width()
            image_height = ppixmap.height()
            image_depth = ppixmap.depth()
            if image_width >= image_height:
                if image_width > self.WW and not image_height > self.HH:
                    self.scaleFactor = (self.WW-2)/image_width
                elif image_height > self.HH:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
            else:
                if image_height > self.HH and not image_width > self.WW:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
                elif image_width > self.WW:
                    self.scaleFactor = (self.WW-2)/image_width
            self.imageLabel.resize(self.scaleFactor * ppixmap.size())
            self.scaleFactorStart = self.scaleFactor
            #
            self.ianimated.start()
        else:
            image_width = ppixmap.width()
            image_height = ppixmap.height()
            image_depth = ppixmap.depth()
            #
            if image_width >= image_height:
                if image_width > self.WW and not image_height > self.HH:
                    self.scaleFactor = (self.WW-2)/image_width
                elif image_height > self.HH:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
            else:
                if image_height > self.HH and not image_width > self.WW:
                    self.scaleFactor = (self.HH-2-self.menuBar().size().height())/image_height
                elif image_width > self.WW:
                    self.scaleFactor = (self.WW-2)/image_width
            # 
            self.imageLabel.setPixmap(ppixmap)
            #
            self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())
            self.scaleFactorStart = self.scaleFactor
        # 
        self.imageLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        #
        self.scrollArea.setVisible(True)
        self.scrollArea.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # 
        self.printAct.setEnabled(True)
        # 
        self.updateActions()
        self.infoAct.setEnabled(True)
        #
        self.setWindowTitle("Image Viewer - {} - x{}".format(os.path.basename(self.ipath), round(self.scaleFactor, 2)))
    
    
    # with up or down keys
    def imageRotate(self, ttype):
        if self.is_animated:
            return
        # 
        ppixmap = self.imageLabel.pixmap()
        if ttype == -1:
            image_rotation = 90
        else:
            image_rotation = -90
        # 
        transform = QTransform().rotate(image_rotation)
        ppixmap = ppixmap.transformed(transform, Qt.SmoothTransformation)
        # update the label
        self.imageLabel.setPixmap(ppixmap)
        self.imageLabel.adjustSize()
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())
    
    
    def eventFilter(self, source, event):
        # mouse scrolling
        if event.type() == QEvent.MouseMove:
            if self.last_time_move_v == 0:
                self.last_time_move_v = event.pos().y()
            vdistance = self.last_time_move_v - event.pos().y()
            self.vscrollbar.setValue(self.vscrollbar.value() + vdistance)
            self.last_time_move_v = event.pos().y()
            #
            if self.last_time_move_h == 0:
                self.last_time_move_h = event.pos().x()
            hdistance = self.last_time_move_h - event.pos().x()
            self.hscrollbar.setValue(self.hscrollbar.value() + hdistance)
            self.last_time_move_h = event.pos().x()
            return True
        elif event.type() == QEvent.MouseButtonRelease:
            self.last_time_move_h = 0
            self.last_time_move_v = 0
            return True
        # key navigation
        elif event.type() == QEvent.KeyPress:
            # next or previous file
            if event.key() == Qt.Key_Left:
                self.keyNav(-1)
            elif event.key() == Qt.Key_Right:
                self.keyNav(1)
            # rotate the image
            elif event.key() == Qt.Key_Up:
                self.imageRotate(-1)
            elif event.key() == Qt.Key_Down:
                self.imageRotate(1)
        #
        return super().eventFilter(source, event)


if __name__ == '__main__':
    import sys, os
    from PyQt5.QtWidgets import QApplication
    #
    app = QApplication(sys.argv)
    # 
    if len(sys.argv) > 1:
        ipath = sys.argv[1]
        imageViewer = QImageViewer(os.path.realpath(ipath))
    else:
        imageViewer = QImageViewer(None)
    imageViewer.show()
    sys.exit(app.exec_())
