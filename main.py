from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel
)
from PySide6.QtCore import Qt, QTimer, QCoreApplication, QThread
from PySide6.QtGui import QFont, QColor
import sys
import subprocess
import os

# --- Splash Screen Widget ---

class SplashScreen(QWidget):
    """
    A simple splash screen that runs for a set duration before launching the main application.
    """
    def __init__(self, main_app_script="main.py"):
        super().__init__()
        self.main_app_script = main_app_script
        self.setWindowTitle("CFL IDE Loading")
        self.setGeometry(300, 300, 500, 200)

        # Remove window frame, use a custom background, and center it
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.center_window()

        self.init_ui()
        self.show()

        # Setup 4-second loading simulation
        self.loading_duration_ms = 4000 
        
        # 1. Timer to close the splash screen and start main.py
        self.launch_timer = QTimer(self)
        self.launch_timer.timeout.connect(self.close_splash_and_start_main)
        self.launch_timer.start(self.loading_duration_ms)
        
        # 2. Timer to animate the progress bar smoothly
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(40) # Update every 40ms for 100 updates total
        
        self.progress_increment = 100 / (self.loading_duration_ms / 40)
        self.current_progress = 0


    def init_ui(self):
        """Sets up the UI elements and styling for the splash screen."""
        self.setStyleSheet("""
            QWidget {
                background-color: white; /* Dark background similar to IDE theme */
                border-radius: 15px;
            }
            QLabel#title_label {
                color: #61afef; /* Light blue */
                font-size: 24pt;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #56b6c2; 
                border-radius: 7px;
                text-align: center;
                background-color: #3e4451;
            }
            QProgressBar::chunk {
                background-color: #56b6c2; /* Teal color */
                border-radius: 7px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title Label
        title_label = QLabel("CFLide v1.0.1")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Status Label
        self.status_label = QLabel("Initializing core modules...")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #abb2bf;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def center_window(self):
        """Centers the splash screen on the desktop."""
        qr = self.frameGeometry()
        # Use the primary screen to get centering reference
        cp = QApplication.primaryScreen().availableGeometry().center() 
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_progress(self):
        """Updates the progress bar value and status label based on time elapsed."""
        if self.current_progress < 100:
            self.current_progress += self.progress_increment
            self.progress_bar.setValue(min(100, int(self.current_progress))) # Max 100
            
            # Simple status updates
            if self.current_progress < 30:
                 self.status_label.setText("Initializing core modules...")
            elif self.current_progress < 60:
                 self.status_label.setText("Loading plugins and settings...")
            elif self.current_progress < 90:
                 self.status_label.setText("Compiling UI...")
            else:
                 self.status_label.setText("Ready to launch.")
        else:
            # If timer is still running, ensure progress is maxed out
            self.progress_bar.setValue(100)


    def close_splash_and_start_main(self):
        """
        Closes the splash screen, stops the timers, and starts the main application.
        """
        # Stop timers
        self.launch_timer.stop()
        self.progress_timer.stop()

        # Execute main.py in a separate process
        try:
            # Use the same Python executable that is running the splash screen
            python_executable = sys.executable
            
            # Launch main.py in a new, non-blocking process
            subprocess.Popen([python_executable, self.main_app_script])
            print(f"Successfully launched: {python_executable} {self.main_app_script}")

        except Exception as e:
            print(f"Failed to launch main application ({self.main_app_script}): {e}")
            # Optionally show an error message box here

        # Close the splash application process
        QCoreApplication.instance().quit()


if __name__ == '__main__':
    # NOTE: Ensure your main CFL class application is in a file named 'main.py' 
    # and placed in the same directory as this script.
    app = QApplication(sys.argv)
    
    splash = SplashScreen(main_app_script="app.py") 
    sys.exit(app.exec())