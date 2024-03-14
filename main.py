import os
import subprocess
from sys import argv as sys_argv
from sys import platform
from datetime import timedelta
from functools import partial
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QProgressBar,
    QFileDialog,
    QApplication,
    QLineEdit,
    QDialog
)


class MainWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audacity Timestamp Converter")
        main_layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        file_label = QLabel("Labels File:")
        file_layout.addWidget(file_label)
        file_param = QLineEdit()
        file_param.setReadOnly(True)
        file_layout.addWidget(file_param)
        file_button = QPushButton("📂")
        file_button.setFixedWidth(30)
        file_button.clicked.connect(partial(open_file, file_param))
        file_layout.addWidget(file_button)
        main_layout.addLayout(file_layout)

        options_layout = QVBoxLayout()
        end_time_bool = QCheckBox("Include end time")
        end_time_bool.setChecked(False)
        hour_bool = QCheckBox("Always include hour in timestamp")
        hour_bool.setChecked(False)
        new_file_bool = QCheckBox("Write to new file.")
        new_file_bool.setChecked(True)
        options_layout.addWidget(end_time_bool)
        options_layout.addWidget(hour_bool)
        options_layout.addWidget(new_file_bool)
        main_layout.addLayout(options_layout)

        # progress_bar = QProgressBar()
        # main_layout.addWidget(progress_bar)

        run_button = QPushButton("Convert to Timestamps")
        run_button.clicked.connect(partial(convert_timestamps, file_param, end_time_bool, hour_bool, new_file_bool))
        main_layout.addWidget(run_button)

        file_param.setText("/Users/sndr/PycharmProjects/AudacityLabels2TimeStamps/Labels 1.txt")

        self.setLayout(main_layout)
        self.setFixedWidth(420)
        self.setFixedHeight(self.sizeHint().height())
        self.show()


def open_file(file_param: QLineEdit):
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    file_dialog.setNameFilter("Text Files (*.txt *.rtf)")
    if file_dialog.exec():
        file_name = file_dialog.selectedFiles()
        file_param.setText(file_name[0])


def convert_timestamps(file_param: QLineEdit, end_time_param: QCheckBox, hour_param: QCheckBox, new_file_param: QCheckBox):
    file_name = file_param.text()
    end_time_bool = end_time_param.isChecked()
    hour_bool = hour_param.isChecked()
    new_file_bool = new_file_param.isChecked()

    if file_name == "":
        print("no file selected")
    else:
        file = open(file_name, mode="r+")
        file_content = file.readlines()
        timestamp_list = []
        for line in file_content:
            timestamp_list.append(line.split("\t"))

        if float(timestamp_list[-1][1]) >= 3600.0 or hour_bool:
            print("duration is longer than an hour")
            timestamp_list_converted = convert_timestamp_list(timestamp_list=timestamp_list,
                                                              include_end_time=end_time_bool,
                                                              include_hour=True)
        else:
            print("duration is less than an hour")
            timestamp_list_converted = convert_timestamp_list(timestamp_list=timestamp_list,
                                                              include_end_time=end_time_bool,
                                                              include_hour=False)

        for line in timestamp_list_converted:
            print(line)

        if new_file_bool:
            file.close()
            new_file_name = f"{file_name.split(".")[0]}_converted.txt"
            new_file = open(new_file_name, "w+")
            new_file.writelines(timestamp_list_converted)
            new_file.close()

            open_result(new_file_name)

        else:
            file.seek(0)
            file.writelines(timestamp_list_converted)
            file.truncate()
            file.close()
            open_result(file_name)


def open_result(file_path):
    # Mac OS
    print(platform)
    if platform == "darwin":
        subprocess.call(["open", "-a", "TextEdit", file_path])
    elif platform == "win32":
        subprocess.Popen(["notepad", file_path])
    elif platform == "linux":
        print("I don't know what the command to open a text file in linux is")
    else:
        print("unknown OS")

def convert_timestamp_list(timestamp_list: list, include_end_time: bool, include_hour: bool):
    converted_list = []
    for line in timestamp_list:
        start_time = seconds_to_timestamp(input_seconds=float(line[0]), include_hour=include_hour)
        end_time = seconds_to_timestamp(input_seconds=float(line[1]), include_hour=include_hour)
        description = line[2]
        if include_end_time:
            converted_list.append(f"{start_time}-{end_time} - {description}")
        else:
            converted_list.append(f"{start_time} - {description}")

    return converted_list


def seconds_to_timestamp(input_seconds: float, include_hour: bool):
    timestamp_raw = str(timedelta(seconds=input_seconds)).split(":")
    hour = timestamp_raw[0]
    minute = timestamp_raw[1]
    second = round(float(timestamp_raw[2]))
    if include_hour:
        timestamp = f"{hour}:{minute}:{second}"
    else:
        timestamp = f"{minute}:{second}"

    return timestamp


if __name__ == '__main__':
    app = QApplication(sys_argv)
    w = MainWindow()
    app.exec()
