import sys
import cv2
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, \
    QCheckBox, QLabel, QGroupBox, QSlider, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from scipy import ndimage

BRIGHT_RANGE_MIN = -100
BRIGHT_RANGE_MAX = 100
CONTRAST_RANGE_MIN = 0
CONTRAST_RANGE_MAX = 20
CONTRAST_VALUE = 10
CONTRAST_DIVIDE_ALPHA = 10.0
ROTATE_RANGE_MIN = 0
ROTATE_RANGE_MAX = 360
PIXMAP_SIZE_WIDTH = 320
PIXMAP_SIZE_HEIGHT = 320
PIXMAP_LABEL_HEIGHT = 360
WINDOW_SIZE_WIDTH = 700
WINDOW_SIZE_HEIGHT = 500


class myImageEdit(QWidget):
    def __init__(self):
        super().__init__()
        self.filename = ''
        # self.tmp_img = cv2.imread(self.filename)
        self.save_filepath = 'saved_img'
        self.img_src = QLabel()
        self.img_dst = QLabel()
        self.bri_slider = QSlider(Qt.Horizontal, self)
        self.con_slider = QSlider(Qt.Horizontal, self)
        self.res_width = QLineEdit()
        self.res_height = QLineEdit()
        self.rot_spin = QSpinBox()
        self.gray_chk = QCheckBox('GrayScale')
        self.prefix_lbl = QLabel('FileName Prefix')
        self.prefix_text = QLineEdit('Prefix')
        self.suffix_lbl = QLabel('FileName Suffix')
        self.suffix_text = QLineEdit('Suffix')
        self.open_btn = QPushButton('Open')
        self.run_btn = QPushButton('Run')
        self.bright_edit = self.brightness_check()
        self.contrast_edit = self.contrast_check()
        self.resize_edit = self.resize_check()
        self.rotate_edit = self.rotate_check()
        self.gray_edit = self.gray_check()
        self.save_edit = self.save_check()
        self.initUI()

    def initUI(self):
        self.show_img()
        grid = QGridLayout()
        grid.addWidget(self.img_src, 0, 0)
        grid.addWidget(self.img_dst, 0, 1)
        grid.addWidget(self.bright_edit, 1, 0)
        grid.addWidget(self.contrast_edit, 2, 0)
        grid.addWidget(self.resize_edit, 3, 0)
        grid.addWidget(self.rotate_edit, 4, 0)
        grid.addWidget(self.gray_edit, 5, 0)
        grid.addWidget(self.save_edit, 1, 1, 4, 1)
        grid.addWidget(self.open_run(), 5, 1)
        self.setLayout(grid)

        self.open_btn.clicked.connect(self.open_file)
        self.run_btn.clicked.connect(self.run_prog)
        self.bri_slider.valueChanged.connect(self.change_status)
        self.con_slider.valueChanged.connect(self.change_status)

        self.setWindowTitle('ImageEditor')
        self.resize(WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT)
        self.show()

    def brightness_check(self):
        bri_box = QGroupBox('Brightness')
        bri_box.setCheckable(True)
        bri_box.setChecked(False)

        self.bri_slider.setTickPosition(1)
        self.bri_slider.setRange(BRIGHT_RANGE_MIN, BRIGHT_RANGE_MAX)

        vbox = QVBoxLayout()
        vbox.addWidget(self.bri_slider)
        bri_box.setLayout(vbox)

        return bri_box

    def contrast_check(self):
        con_box = QGroupBox('Contrast')
        con_box.setCheckable(True)
        con_box.setChecked(False)

        self.con_slider.setTickPosition(1)
        self.con_slider.setRange(CONTRAST_RANGE_MIN, CONTRAST_RANGE_MAX)
        self.con_slider.setValue(CONTRAST_VALUE)

        vbox = QVBoxLayout()
        vbox.addWidget(self.con_slider)
        con_box.setLayout(vbox)

        return con_box

    def resize_check(self):
        res_box = QGroupBox('Resize')
        res_box.setCheckable(True)
        res_box.setChecked(False)

        hbox = QHBoxLayout()
        hbox.addWidget(self.res_width)
        hbox.addWidget(QLabel(' * '))
        hbox.addWidget(self.res_height)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        res_box.setLayout(vbox)

        return res_box

    def rotate_check(self):
        rot_box = QGroupBox('Rotate')
        rot_box.setCheckable(True)
        rot_box.setChecked(False)

        self.rot_spin.setRange(ROTATE_RANGE_MIN, ROTATE_RANGE_MAX)

        vbox = QVBoxLayout()
        vbox.addWidget(self.rot_spin)
        rot_box.setLayout(vbox)

        return rot_box

    def gray_check(self):
        gray_box = QGroupBox()

        vbox = QVBoxLayout()
        vbox.addWidget(self.gray_chk)
        gray_box.setLayout(vbox)

        return gray_box

    def save_check(self):
        save_box = QGroupBox('Save')
        save_box.setCheckable(True)
        save_box.setChecked(False)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.prefix_lbl)
        hbox1.addWidget(self.prefix_text)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.suffix_lbl)
        hbox2.addWidget(self.suffix_text)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        save_box.setLayout(vbox)

        return save_box

    def open_run(self):
        btn_box = QGroupBox()

        hbox = QHBoxLayout()
        hbox.addWidget(self.open_btn)
        hbox.addWidget(self.run_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        btn_box.setLayout(vbox)

        return btn_box

    def open_file(self):
        f_name = QFileDialog.getOpenFileName(self, 'Open file', './', "Image (*.jpg *.png *.bmp)")

        if f_name[0]:
            self.filename = f_name[0]
            self.show_img()
            self.un_checked()

    def un_checked(self):
        self.bright_edit.setChecked(False)
        self.contrast_edit.setChecked(False)
        self.resize_edit.setChecked(False)
        self.rotate_edit.setChecked(False)
        self.gray_chk.setChecked(False)
        self.save_edit.setChecked(False)

    def change_status(self):
        img_org = cv2.imread(self.filename, cv2.IMREAD_COLOR)

        if self.bright_edit.isChecked():
            img_org = self.brightness_chg(img_org)
        if self.contrast_edit.isChecked():
            img_org = self.contrast_chg(img_org)
        if self.resize_edit.isChecked():
            img_org = self.resize_chg(img_org)
        if self.rotate_edit.isChecked():
            img_org = self.rotate_chg(img_org)
        if self.gray_chk.isChecked():
            img_org = self.gray_chg(img_org)

        self.cv2pixmap(img_org)

        return img_org

    def run_prog(self):
        img_org = self.change_status()

        # cv2.imshow('dst', img_org)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        if self.save_edit.isChecked():
            self.save_img(img_org)

    def brightness_chg(self, img):
        dst = cv2.add(img, (self.bri_slider.value(), self.bri_slider.value(), self.bri_slider.value(), 0))

        return dst

    def contrast_chg(self, img):
        alpha = self.con_slider.value() / CONTRAST_DIVIDE_ALPHA
        dst = np.clip((1 + alpha) * img - 128 - alpha, 0, 255).astype(np.uint8)

        return dst

    def resize_chg(self, img):
        if self.res_width.text() and self.res_height.text():
            rw = self.res_width.text()
            rh = self.res_height.text()
        else:
            return img

        dst = cv2.resize(img, dsize=(int(rw), int(rh)), interpolation=cv2.INTER_AREA)

        return dst

    def rotate_chg(self, img):
        angle = self.rot_spin.value()
        # h, w = img.shape[:2]
        # ww = abs((round(np.cos(angle * np.pi / 180), 2) * w) - (round(np.sin(angle * np.pi / 180), 2) * h))
        # hh = abs((round(np.sin(angle * np.pi / 180), 2) * w) + (round(np.cos(angle * np.pi / 180), 2) * h))
        # center = (w/2, h/2)
        # rot = cv2.getRotationMatrix2D(center, angle, min(h/hh, w/ww))
        # dst = cv2.warpAffine(img, rot, (w, h), flags=cv2.INTER_LINEAR)
        dst = ndimage.rotate(img, angle)
        return dst

        # angle = self.rot_spin.value()
        # h, w = img.shape[:2]
        # height_big = h * 2
        # width_big = w * 2
        # image_big = cv2.resize(img, (width_big, height_big))
        # image_center = (width_big / 2, height_big / 2)  # rotation center
        # rot_mat = cv2.getRotationMatrix2D(image_center, angle, 0.5)
        # dst = cv2.warpAffine(image_big, rot_mat, (width_big, height_big), flags=cv2.INTER_LINEAR)
        # return dst

    def gray_chg(self, img):
        dst = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return dst

    def cv2pixmap(self, img):
        dst = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h2, w2 = dst.shape[:2]
        qwe = cv2.imread(self.filename)
        h, w = qwe.shape[:2]
        # print(w2, h2)
        # print(w, h)
        if w >= h:
            if w2 > h2:
                dst = cv2.resize(dst, (w, h))
            else:
                dst = cv2.resize(dst, (h, w))
        else:
            if w2 > h2:
                dst = cv2.resize(dst, (h, w))
            else:
                dst = cv2.resize(dst, (w, h))
        h, w, c = dst.shape
        qdst = QImage(dst.data, w, h, QImage.Format_RGB888)
        pixmapdst = QPixmap.fromImage(qdst)
        pixmap_resized = pixmapdst.scaled(PIXMAP_SIZE_WIDTH, PIXMAP_SIZE_HEIGHT, Qt.KeepAspectRatio)

        self.img_dst.setPixmap(pixmap_resized)

    def show_img(self):
        pixmap = QPixmap()
        pixmap.load(self.filename)
        pixmap_resized = pixmap.scaled(PIXMAP_SIZE_WIDTH, PIXMAP_SIZE_HEIGHT, Qt.KeepAspectRatio)

        self.img_src.setFixedHeight(PIXMAP_LABEL_HEIGHT)
        self.img_dst.setFixedHeight(PIXMAP_LABEL_HEIGHT)

        self.img_src.setPixmap(pixmap_resized)
        self.img_dst.setPixmap(pixmap_resized)

    def save_img(self, img):
        if not os.path.isdir(self.save_filepath):
            os.mkdir(self.save_filepath)

        f_name = self.filename.split('/')
        f_name = f_name[-1].split('.')
        file_fullpath = self.save_filepath + '/' + self.prefix_text.text() + '_' + f_name[0] + '_' + \
                        self.suffix_text.text() + '.' + f_name[1]
        cv2.imwrite(file_fullpath, img)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    img_edit = myImageEdit()
    sys.exit(app.exec_())

