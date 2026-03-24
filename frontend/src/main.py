import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from window_admin.main_window import AdminMainWindow
import requests
from window_doctor.main_window import DoctorMainWindow
from window_patient.main_window import PatientMainWindow
from utils.theme_manager import ThemeManager

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)
        
        self.setWindowTitle("Hospital Management System")
        self.setFixedSize(400, 650)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 30)
        
        # theme toggle button in top left
        theme_button = QPushButton("🌙" if self.theme_manager.is_dark else "☀️")
        theme_button.setFixedSize(36, 36)
        theme_button.setObjectName("themeButton")
        theme_button.clicked.connect(self.theme_manager.toggle_theme)
        layout.addWidget(theme_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # title
        title = QLabel("HMS Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {self.theme_manager.current_theme['accent']};
            margin: 20px 0;
            padding: 10px;
            letter-spacing: 1px;
            text-transform: uppercase;
            background: transparent;
        """)
        layout.addWidget(title)
        
        # login form
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Add login button
        login_button = QPushButton("Login")
        login_button.setObjectName("loginButton")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)
        
        # status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # small spacer
        spacer = QWidget()
        spacer.setFixedHeight(20)
        layout.addWidget(spacer)
        
        # Credits section
        credits_frame = QFrame()
        credits_frame.setObjectName("creditsFrame")
        credits_layout = QVBoxLayout(credits_frame)
        credits_layout.setSpacing(8)
        
        credits_title = QLabel("Created by:")
        credits_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_title.setObjectName("creditsTitle")
        credits_layout.addWidget(credits_title)
        
        creators = [
            "Akram Lagraa",
            "Koudid Azzedine",
            "Ouahrani Nassim",
            "Riyache Sami"
        ]
        
        for creator in creators:
            label = QLabel(creator)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setObjectName("creditLabel")
            credits_layout.addWidget(label)
        
        layout.addWidget(credits_frame)
        
        # initial theme
        self.apply_theme(self.theme_manager.is_dark)
    
    API_URL = "http://127.0.0.1:8000/api/login/"  # URL du backend (à adapter si nécessaire)
    token = None
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            self.status_label.setText("Please enter username and password")
            self.status_label.setStyleSheet(f"color: {self.theme_manager.current_theme['error']};")
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return

        # Envoi de la requête au backend
        try:
            response = requests.post(self.API_URL, json={"username": username, "password": password})
            data = response.json()
            
            if response.status_code == 200:  # Connexion réussie
                token = data.get("token")
                user_data = data.get("user", {})
                
                role = user_data.get("role", "unknown")  # À adapter selon ton backend

                self.status_label.setText("Login successful!")
                self.status_label.setStyleSheet(f"color: {self.theme_manager.current_theme['success']};")

                # Redirection selon le rôle
                if role == "admin":
                    self.open_admin_main_window(token, user_data)
                elif role == "med":
                    self.open_doctor_main_window(token, user_data)
                elif role == "pat":
                    self.open_patient_main_window(token, user_data)
                else:
                    self.status_label.setText("Invalid role")
                    QMessageBox.warning(self, "Error", "Invalid role")

            else:  # Échec de connexion
                error_message = data.get("error", "Invalid username or password")
                self.status_label.setText(error_message)
                self.status_label.setStyleSheet(f"color: {self.theme_manager.current_theme['error']};")
                QMessageBox.warning(self, "Error", error_message)

        except requests.exceptions.RequestException as e:
            self.status_label.setText("Server error, try again later")
            self.status_label.setStyleSheet(f"color: {self.theme_manager.current_theme['error']};")
            QMessageBox.critical(self, "Error", f"Server error: {e}")
    

    def open_admin_main_window(self, token, user_data):
        self.main_window = AdminMainWindow(token, user_data)
        self.main_window.logout_signal.connect(self.show_login_window)
        self.main_window.show()
        self.close()
    def open_doctor_main_window(self, token, user_data):
        self.main_window = DoctorMainWindow(token, user_data)
        self.main_window.logout_signal.connect(self.show_login_window)
        self.main_window.show()
        self.close()
    def open_patient_main_window(self, token, user_data):
        self.main_window = PatientMainWindow(token, user_data)
        self.main_window.logout_signal.connect(self.show_login_window)
        self.main_window.show()
        self.close()
    
    def show_login_window(self):
        """ Show the login window again when user logs out """
        self.show()
    
    def apply_theme(self, is_dark):
        theme = self.theme_manager.current_theme
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg_primary']};
            }}
            
            QLabel {{
                color: {theme['text_primary']};
            }}
            
            QLineEdit {{
                padding: 12px;
                border: 2px solid {theme['border']};
                border-radius: 8px;
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
            
            QPushButton#loginButton {{
                padding: 12px;
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            
            QPushButton#loginButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            QPushButton#themeButton {{
                background-color: {theme['accent']};
                color: white;
                border-radius: 18px;
                font-size: 16px;
                margin: 0;
                padding: 0;
            }}
            
            QPushButton#themeButton:hover {{
                background-color: {theme['accent_hover']};
            }}

            QFrame#creditsFrame {{
                margin-top: 10px;
                background-color: transparent;
            }}
            
            QLabel#creditsTitle {{
                color: {theme['text_secondary']};
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            QLabel#creditLabel {{
                color: {theme['accent']};
                font-size: 14px;
                font-weight: bold;
                padding: 4px;
                margin: 2px 0;
            }}
            
            QLabel#creditLabel:hover {{
                color: {theme['accent_hover']};
            }}
        """)

def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 