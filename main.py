import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QRadioButton, QProgressBar, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from process_option1 import process_option1
from process_option2 import process_option2
from process_option3 import process_option3
from process_option4 import process_option4

class ProcessingThread(QThread):
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    processing_finished = pyqtSignal(bool)

    def __init__(self, option, filenames):
        super().__init__()
        self.option = option
        self.filenames = filenames

    def run(self):
        if self.option == "option4":
            total_files = len(self.filenames)
            for i, filename in enumerate(self.filenames):
                self.status_update.emit(f"Processing file {i+1}/{total_files}: {filename}")
                result = process_option4(filename, self.progress_update, self.status_update)
                self.progress_update.emit(int((i + 1) / total_files * 100))
            self.processing_finished.emit(True)
        else:
            # Implement other options here
            pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Processor")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # File selection
        self.file_label = QLabel("Selected Files:")
        layout.addWidget(self.file_label)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_files)
        layout.addWidget(self.browse_button)

        # Processing options
        options_layout = QHBoxLayout()
        self.option1 = QRadioButton("Option 1 (JSON)")
        self.option2 = QRadioButton("Option 2 (JSON)")
        self.option3 = QRadioButton("Option 3 (JSONL)")
        self.option4 = QRadioButton("Option 4 (Image Processing)")
        self.option1.setChecked(True)
        options_layout.addWidget(self.option1)
        options_layout.addWidget(self.option2)
        options_layout.addWidget(self.option3)
        options_layout.addWidget(self.option4)
        layout.addLayout(options_layout)

        # Process button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_files)
        layout.addWidget(self.process_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Status updates
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

        self.filenames = []

    def browse_files(self):
        file_dialog = QFileDialog()
        self.filenames, _ = file_dialog.getOpenFileNames(self, "Select Files")
        self.file_label.setText(f"Selected Files: {len(self.filenames)}")

    def process_files(self):
        if not self.filenames:
            self.status_text.append("Please select files first.")
            return

        option = "option1"
        if self.option2.isChecked():
            option = "option2"
        elif self.option3.isChecked():
            option = "option3"
        elif self.option4.isChecked():
            option = "option4"

        self.processing_thread = ProcessingThread(option, self.filenames)
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.status_update.connect(self.update_status)
        self.processing_thread.processing_finished.connect(self.processing_done)
        
        self.process_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.processing_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_text.append(message)

    def processing_done(self, success):
        self.process_button.setEnabled(True)
        if success:
            self.status_text.append("Processing completed successfully.")
        else:
            self.status_text.append("Processing completed with errors. Check the log for details.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())