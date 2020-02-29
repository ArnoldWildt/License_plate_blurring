import os
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.input_isset = False
        self.output_isset = False
        self.input_path = ""
        self.output_path = ""

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        MainWindow.setFont(font)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(30, 515, 750, 20))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        self.inputPath = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.inputPath.setGeometry(QtCore.QRect(30, 475, 210, 25))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.inputPath.setFont(font)
        self.inputPath.setObjectName("inputPath")
        self.inputPath.mousePressEvent = self.show_file_dialog
        self.inputPath.setReadOnly(True)
        self.inputPath.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.outputPath = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.outputPath.setGeometry(QtCore.QRect(570, 470, 210, 25))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.outputPath.setFont(font)
        self.outputPath.setObjectName("outputPath")
        self.outputPath.mousePressEvent = self.show_save_dialog
        self.outputPath.setReadOnly(True)
        self.outputPath.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.frame = QtWidgets.QLabel(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(30, 10, 750, 450))
        self.frame.setObjectName("frame")
        self.pixmap = QtGui.QPixmap("./temp.png")
        self.frame.setPixmap(self.pixmap)
        self.frame.setScaledContents(True)

        self.progressLabel = QtWidgets.QLabel(self.centralwidget)
        self.progressLabel.setGeometry(QtCore.QRect(30, 555, 750, 20))
        self.progressLabel.setObjectName("progressLabel")

        self.processButton = QtWidgets.QPushButton(self.centralwidget)
        self.processButton.setGeometry(QtCore.QRect(370, 470, 75, 24))
        self.processButton.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.processButton.setObjectName("processButton")
        self.processButton.setDisabled(True)
        self.processButton.clicked.connect(self.process_video)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuOptions = QtWidgets.QMenu(self.menuBar)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.menuOptions.setFont(font)
        self.menuOptions.setObjectName("menuOptions")
        MainWindow.setMenuBar(self.menuBar)
        self.menuBar.addAction(self.menuOptions.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.inputPath.setPlainText(_translate("MainWindow",
                                               "Select Inputfile.."))
        self.processButton.setText(_translate("MainWindow", "Process"))
        self.outputPath.setPlainText(_translate("MainWindow",
                                                "Select Outputfile.."))
        self.menuOptions.setTitle(_translate("MainWindow", "Options"))

    def is_filled(self):
        if self.input_isset and self.output_isset:
            self.processButton.setDisabled(False)

    def show_file_dialog(self, event):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            MainWindow, "Select Inputfile",
            "", "MP4 File (*.mp4)", options=options)

        if filename:
            self.input_path = filename
            text_field = filename.split("/")
            self.inputPath.setPlainText(f"../{'/'.join(text_field[-2:])}")

            self.input_isset = True
            self.is_filled()

    def show_save_dialog(self, event):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            MainWindow, "Select savelocation",
            "", "MP4 File (*.mp4)", options=options)

        if filename:
            text_field = filename.split("/")
            text_field = '/'.join(text_field[-2:-1])

            save_name = filename
            if ".mp4" not in filename:
                save_name += ".mp4"
            self.output_path = save_name

            text_field += "/" + save_name.split("/")[-1]

            self.outputPath.setPlainText(f"../{text_field}")

            with open(save_name, "w") as temp_file:
                pass

            self.output_isset = True
            self.is_filled()

    def process_video(self):
        self.progressLabel.setText("Loading Yolo Model")
        QtCore.QCoreApplication.processEvents()
        from collections import deque
        from yolo import YOLO
        from yolo3 import utils
        from PIL import Image
        import cv2

        frame_buffer = deque([], 3)

        bridge_buffer = []
        bridge_last = -1

        extended = False

        counter_ = 0
        frame_counter = 0

        yolo_model = YOLO()

        capture = cv2.VideoCapture(self.input_path)

        if not capture.isOpened():
            raise IOError("Couldn't open video")

        video_fps = capture.get(cv2.CAP_PROP_FPS)
        video_size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                      int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        max_frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)

        out = cv2.VideoWriter(self.output_path,
                              cv2.VideoWriter_fourcc(*'DIVX'),
                              video_fps, video_size)

        self.progressLabel.setText("Detecting")
        while (capture.isOpened()):
            ret, frame = capture.read()

            frame_counter += 1

            if ret:
                image = Image.fromarray(frame)
                bboxes_pr = yolo_model.detect_image(image)
                frame_buffer.append([bboxes_pr, frame])

                if len(frame_buffer) >= frame_buffer.maxlen:
                    img_pred = frame_buffer[0][1].copy()

                    if counter_ > 0:
                        extended = False
                        counter_ = 0

                    if extended:
                        counter_ += 1

                        if not extended and len(frame_buffer[1][0]) <= 0:
                            if len(frame_buffer[0][0]) > 0 or len(frame_buffer[2][0]) > 0:
                                if len(frame_buffer[0][0]) > 0:
                                    frame_buffer[1][0] = frame_buffer[0][0]

                                else:
                                    frame_buffer[1][0] = frame_buffer[2][0]

                                extended = True

                    img_pred = utils.blur_img(frame_buffer[0][0], img_pred)

                    height, width, channel = img_pred.shape
                    bytesPerLine = 3 * width
                    qimg = QtGui.QImage(img_pred.data, width, height,
                                        bytesPerLine,
                                        QtGui.QImage.Format_BGR888)
                    self.frame.setPixmap(QtGui.QPixmap(qimg))
                    progress_value = int(frame_counter/max_frame_count * 100)
                    self.progressBar.setProperty("value", progress_value)
                    # Updates Picture + Progressbar
                    QtCore.QCoreApplication.processEvents()

                    bridge_buffer.append([frame_buffer[0][0], img_pred])

                    if len(bridge_buffer) >= 50:
                        if len(frame_buffer[0][0]) == len(frame_buffer[1][0]):
                            bridge_buffer = utils.fill_bridges(bridge_buffer)

                            for list in bridge_buffer:
                                out.write(list[1])
                            bridge_buffer = []
            else:
                bridge_buffer = utils.fill_bridges(bridge_buffer)

                for list in bridge_buffer:
                    out.write(list[1])
                bridge_buffer = []

                capture.release()
                out.release()
                # yolo_model.close_session()

                self.progressLabel.setText("Adding Audio to the Outputfile")
                temp_output = self.output_path.split("/")
                temp_output[-1] = temp_output[-1].split(".")[0] + "_.mp4"
                temp_output = "/".join(temp_output)
                os.system(
                    f'ffmpeg -i "{self.output_path}" -i "{self.input_path}" -map 0:v -map 1:a -c copy -shortest "{temp_output}"')
                os.remove(self.output_path)
                os.rename(temp_output, self.output_path)

                self.progressLabel.setText("Finished")
                break


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    MainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
