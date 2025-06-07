import sys
import cv2
import threading

from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QVBoxLayout,
    QWidget, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from playsound3 import playsound


model_path = "./models/hand_landmarker.task"
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


def play_music():
    playsound("./audios/piano_piece.mp3")


class VideoStreamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Video Stream")
        self.setFixedSize(640, 560)

        # Main widget
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(640, 480)

        # Buttons
        self.btn_play = QPushButton("Play")
        self.btn_pause = QPushButton("Pause")
        self.btn_capture = QPushButton("Capture")

        self.btn_play.clicked.connect(self.start_stream)
        self.btn_pause.clicked.connect(self.stop_stream)
        self.btn_capture.clicked.connect(self.capture_frame)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_play)
        button_layout.addWidget(self.btn_pause)
        button_layout.addWidget(self.btn_capture)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # OpenCV Video Capture
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.streaming = True
        self.timer.start(30)

    def start_stream(self):
        if not self.timer.isActive():
            self.timer.start(30)
            self.streaming = True

    def stop_stream(self):
        if self.timer.isActive():
            self.timer.stop()
            self.streaming = False

    def capture_frame(self):
        if self.streaming:
            ret, frame = self.cap.read()
            if ret:
                cv2.imwrite("capture.jpg", frame)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            options = HandLandmarkerOptions(
                        base_options=BaseOptions(model_asset_path= model_path),
                        running_mode=VisionRunningMode.IMAGE
                        )
            with HandLandmarker.create_from_options(options) as landmarker:
                hand_landmarker_result = landmarker.detect(mp_image)
                # print(hand_landmarker_result)
                if hand_landmarker_result.hand_landmarks:
                    for landmarks in hand_landmarker_result.hand_landmarks:
                        for lm in landmarks:
                            x = int(lm.x * frame.shape[1])
                            y = int(lm.y * frame.shape[0])
                            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
                        index_finger_y = [
                                    landmarks[5].y,
                                    landmarks[6].y,
                                    landmarks[7].y,
                                    landmarks[8].y,
                                ]

                        is_straight = all(index_finger_y[i] > index_finger_y[i + 1] for i in range(len(index_finger_y) - 1))
                        if is_straight:
                            print("Index figure is straight!")
                            threading.Thread(target=play_music, daemon=True).start()


            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoStreamApp()
    window.show()
    sys.exit(app.exec())
