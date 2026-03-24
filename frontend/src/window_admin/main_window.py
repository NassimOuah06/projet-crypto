from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from utils.theme_manager import ThemeManager
from .patients_page import PatientsPage
from .doctors_page import DoctorsPage
from .appointments_page import AppointmentsPage
from .repports_page import RepportsPage
import requests
import json

class AdminMainWindow(QMainWindow):
    logout_signal = pyqtSignal()
    def __init__(self, token, user_data):
        self.user_data = user_data
        self.token = token
        super().__init__()
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)
        
        self.setWindowTitle("Hospital Management System")
        self.setMinimumSize(1200, 800)
        
        # central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_dashboard_page())
        self.stacked_widget.addWidget(PatientsPage(self.theme_manager, self.token))
        self.stacked_widget.addWidget(DoctorsPage(self.theme_manager, self.token))
        self.stacked_widget.addWidget(AppointmentsPage(self.theme_manager, self.token))
        self.stacked_widget.addWidget(RepportsPage(self.theme_manager, self.token ,self.user_data))
        main_layout.addWidget(self.stacked_widget)
        
        # layout proportions
        main_layout.setStretch(0, 1)  # Sidebar
        main_layout.setStretch(1, 5)  # Content area
        
        # initial theme
        self.apply_theme(self.theme_manager.is_dark)

        # Charger les données du backend
        self.load_dashboard_data()
        
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # logo section
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 20, 20, 20)
        
        logo_label = QLabel("HMS")
        logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        logo_label.setObjectName("logoLabel")
        logo_layout.addWidget(logo_label)
        
        theme_button = QPushButton("🌙" if self.theme_manager.is_dark else "☀️")
        theme_button.setFixedSize(36, 36)
        theme_button.setObjectName("themeButton")
        theme_button.clicked.connect(self.theme_manager.toggle_theme)
        logo_layout.addWidget(theme_button)
        
        layout.addWidget(logo_frame)
        
        # navigation buttons
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Patients", self.show_patients),
            ("👨‍⚕️ Doctors", self.show_doctors),
            ("📅 Appointments", self.show_appointments),
            ("📈 Reports", self.show_repports)
        ]
        
        for text, callback in nav_items:
            button = QPushButton(text)
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(callback)
            layout.addWidget(button)
        
        layout.addStretch()
        
        # user profile section
        profile_frame = QFrame()
        profile_frame.setObjectName("profileFrame")
        profile_layout = QVBoxLayout(profile_frame)
        
        name_label = QLabel(f"{self.user_data['first_name']} {self.user_data['last_name']}")
        name_label.setObjectName("profileName")
        role_label = QLabel("Administrator")
        role_label.setObjectName("profileRole")

        # Add disconnect button
        disconnect_button = QPushButton("🚪 Disconnect",self)
        disconnect_button.setObjectName("disconnectButton")
        disconnect_button.setCursor(Qt.CursorShape.PointingHandCursor)
        disconnect_button.clicked.connect(self.handle_disconnect)
        
        profile_layout.addWidget(name_label)
        profile_layout.addWidget(role_label)
        profile_layout.addSpacing(10)  # Add some space before the button
        profile_layout.addWidget(disconnect_button)
        
        layout.addWidget(profile_frame)
        return sidebar
    
    def handle_disconnect(self):
        self.logout_signal.emit()  # Emit signal instead of calling LoginWindow
        self.close()  # Close the admin window
    
    def create_dashboard_page(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        
        # welcome section
        welcome_frame = QFrame()
        welcome_frame.setObjectName("welcomeFrame")
        welcome_layout = QVBoxLayout(welcome_frame)
        
        welcome_label = QLabel("Welcome back, Admin")
        welcome_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        date_label = QLabel("Today's Overview")
        date_label.setObjectName("dateLabel")
        
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(date_label)
        layout.addWidget(welcome_frame)
        
        # Statistics section (with placeholders)
        self.stats_layout = QHBoxLayout()
        self.total_patients_label = self.create_stat_card("Total Patients", "Loading...", "👥", "")
        self.total_appointments_label = self.create_stat_card("Today's Appointments", "Loading...", "📅", "")
        self.available_doctors_label = self.create_stat_card("Available Doctors", "Loading...", "👨‍⚕️", "")
        self.revenue_label = self.create_stat_card("Revenue", "Loading...", "💰", "")

        self.stats_layout.addWidget(self.total_patients_label)
        self.stats_layout.addWidget(self.total_appointments_label)
        self.stats_layout.addWidget(self.available_doctors_label)
        self.stats_layout.addWidget(self.revenue_label)

        layout.addLayout(self.stats_layout)
        
        # recent activities section
        activities_frame = self.create_activities_section()
        layout.addWidget(activities_frame)
        
        # bottom section with appointments and tasks
        bottom_layout = QHBoxLayout()
        
        appointments = self.create_appointments_section()
        tasks = self.create_tasks_section()
        
        bottom_layout.addWidget(appointments)
        bottom_layout.addWidget(tasks)
        layout.addLayout(bottom_layout)
        
        scroll_area.setWidget(content)
        return scroll_area
    
    def load_dashboard_data(self):
        """Charge les données depuis le backend et met à jour le dashboard."""
        try:
            response = requests.get('http://127.0.0.1:8000/api/admin/dashboard/', headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                data = response.json()
                self.update_dashboard(data)
            else:
                print(f"Erreur : {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau : {e}")

    def update_dashboard(self, data):
        """Met à jour les statistiques du dashboard avec les données récupérées."""
        self.total_patients_label.value_label.setText(f"{data.get('total_patients', 'N/A')}")
        self.total_appointments_label.value_label.setText(f"{data.get('total_consultations', 'N/A')}")
        self.available_doctors_label.value_label.setText(f"{data.get('total_medecins', 'N/A')}")
        self.revenue_label.value_label.setText(f"{data.get('Total Dossier ', 'N/A')}")
    
    def create_stat_card(self, title, value, icon, subtitle):
        card = QFrame()
        card.setObjectName("statCard")
        layout = QVBoxLayout(card)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 24))
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setObjectName("valueLabel")
        card.value_label = value_label  # Store reference to the label
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("cardSubtitle")
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        
        return card
    
    def create_activities_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        
        title = QLabel("Recent Activities")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        activities = [
            ("🏥 New patient admitted", "Room 302", "10 mins ago"),
            ("💊 Medicine stock updated", "Pharmacy", "1 hour ago"),
            ("📝 Dr. Smith updated patient records", "Cardiology", "2 hours ago"),
            ("💰 Payment received", "Reception", "3 hours ago")
        ]
        
        for activity, location, time in activities:
            activity_widget = self.create_activity_item(activity, location, time)
            layout.addWidget(activity_widget)
        
        return frame
    
    def create_appointments_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        
        title = QLabel("Today's Appointments")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        appointments = [
            ("John Doe", "09:00 AM", "Dr. Smith", "Cardiology"),
            ("Jane Smith", "10:30 AM", "Dr. Johnson", "Pediatrics"),
            ("Robert Brown", "02:00 PM", "Dr. Davis", "Orthopedics")
        ]
        
        for name, time, doctor, dept in appointments:
            appt_widget = self.create_appointment_item(name, time, doctor, dept)
            layout.addWidget(appt_widget)
        
        return frame
    
    def create_tasks_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        
        title = QLabel("Tasks")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        tasks = [
            ("Review patient reports", "High", "Today"),
            ("Update medicine inventory", "Medium", "Tomorrow"),
            ("Staff meeting", "Normal", "Next Week")
        ]
        
        for task, priority, deadline in tasks:
            task_widget = self.create_task_item(task, priority, deadline)
            layout.addWidget(task_widget)
        
        return frame
    
    def create_activity_item(self, activity, location, time):
        widget = QFrame()
        widget.setObjectName("activityItem")
        layout = QHBoxLayout(widget)
        
        text_layout = QVBoxLayout()
        activity_label = QLabel(activity)
        location_label = QLabel(location)
        location_label.setObjectName("itemSubtext")
        
        text_layout.addWidget(activity_label)
        text_layout.addWidget(location_label)
        
        time_label = QLabel(time)
        time_label.setObjectName("timeLabel")
        
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(time_label)
        
        return widget
    
    def create_appointment_item(self, name, time, doctor, dept):
        widget = QFrame()
        widget.setObjectName("appointmentItem")
        layout = QHBoxLayout(widget)
        
        text_layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        details_label = QLabel(f"{doctor} - {dept}")
        details_label.setObjectName("itemSubtext")
        
        text_layout.addWidget(name_label)
        text_layout.addWidget(details_label)
        
        time_label = QLabel(time)
        time_label.setObjectName("timeLabel")
        
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(time_label)
        
        return widget
    
    def create_task_item(self, task, priority, deadline):
        widget = QFrame()
        widget.setObjectName("taskItem")
        layout = QHBoxLayout(widget)
        
        text_layout = QVBoxLayout()
        task_label = QLabel(task)
        deadline_label = QLabel(deadline)
        deadline_label.setObjectName("itemSubtext")
        
        text_layout.addWidget(task_label)
        text_layout.addWidget(deadline_label)
        
        priority_label = QLabel(priority)
        priority_label.setObjectName(f"priority{priority}")
        
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(priority_label)
        
        return widget
    
    
    def show_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def show_patients(self):
        self.stacked_widget.setCurrentIndex(1)
    
    def show_doctors(self):
        self.stacked_widget.setCurrentIndex(2)
    
    def show_appointments(self):
        self.stacked_widget.setCurrentIndex(3)
    
    def show_repports(self):
        self.stacked_widget.setCurrentIndex(4)
    
    def apply_theme(self, is_dark):
        theme = self.theme_manager.current_theme
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg_primary']};
            }}
            
            QLabel {{
                color: {theme['text_primary']};
            }}
            
            QFrame#sidebar {{
                background-color: {theme['bg_secondary']};
                border-right: 1px solid {theme['border']};
            }}
            
            QLabel#logoLabel {{
                color: {theme['accent']};
            }}
            
            QPushButton#navButton {{
                background-color: transparent;
                color: {theme['text_primary']};
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 16px;
                border-radius: 0;
            }}
            
            QPushButton#navButton:hover {{
                background-color: {theme['accent']};
                color: white;
            }}
            
            QFrame#statCard {{
                background-color: {theme['card_bg']};
                border-radius: 15px;
                padding: 20px;
            }}
            
            QFrame#statCard QLabel {{
                color: {theme['text_primary']};
            }}
            
            QFrame#sectionFrame {{
                background-color: {theme['card_bg']};
                border-radius: 15px;
                padding: 20px;
            }}
            
            QFrame#sectionFrame QLabel {{
                color: {theme['text_primary']};
            }}
            
            QLabel#cardTitle, QLabel#itemSubtext {{
                color: {theme['text_secondary']};
            }}
            
            QLabel#timeLabel {{
                color: {theme['accent']};
            }}
            
            QFrame#activityItem, QFrame#appointmentItem, QFrame#taskItem {{
                border-bottom: 1px solid {theme['border']};
                padding: 10px 0;
            }}
            
            QFrame#activityItem QLabel, 
            QFrame#appointmentItem QLabel, 
            QFrame#taskItem QLabel {{
                color: {theme['text_primary']};
            }}
            
            QLabel#priorityHigh {{
                color: #e74c3c;
                font-weight: bold;
            }}
            
            QLabel#priorityMedium {{
                color: #f39c12;
                font-weight: bold;
            }}
            
            QLabel#priorityNormal {{
                color: #2ecc71;
                font-weight: bold;
            }}
            
            QFrame#profileFrame {{
                background-color: {theme['bg_primary']};
                padding: 20px;
                margin: 10px;
                border-radius: 10px;
            }}
            
            QLabel#profileName {{
                color: {theme['text_primary']};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QLabel#profileRole {{
                color: {theme['text_secondary']};
            }}
            
            QPushButton#themeButton {{
                background-color: {theme['accent']};
                color: white;
                border-radius: 18px;
                font-size: 16px;
            }}
            
            QPushButton#themeButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            QFrame#welcomeFrame {{
                background-color: {theme['bg_secondary']};
                border-radius: 15px;
                padding: 20px;
            }}
            
            QLabel#subtitle {{
                color: {theme['text_secondary']};
                font-size: 14px;
            }}
            
            QPushButton#primaryButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            QPushButton#secondaryButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
            }}
            
            QPushButton#secondaryButton:hover {{
                background-color: {theme['accent']};
                color: white;
                border: none;
            }}
            
            QLineEdit#searchInput {{
                padding: 12px;
                border: 1px solid {theme['border']};
                border-radius: 8px;
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                font-size: 14px;
            }}
            
            QComboBox#filterCombo {{
                padding: 12px;
                border: 1px solid {theme['border']};
                border-radius: 8px;
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                font-size: 14px;
            }}
            
            QFrame#tableFrame {{
                background-color: {theme['bg_secondary']};
                border-radius: 15px;
                padding: 20px;
            }}
            
            QTableWidget {{
                background-color: transparent;
                border: none;
                gridline-color: {theme['border']};
            }}
            
            QTableWidget::item {{
                padding: 12px;
                color: {theme['text_primary']};
            }}
            
            QHeaderView::section {{
                background-color: transparent;
                color: {theme['text_primary']};
                padding: 12px;
                border: none;
                border-bottom: 1px solid {theme['border']};
                font-weight: bold;
            }}
            
            QFrame#searchFrame {{
                background-color: {theme['bg_secondary']};
                border-radius: 8px;
                padding: 10px;
            }}
            
            QPushButton#iconButton {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                font-size: 16px;
            }}
            
            QPushButton#iconButton:hover {{
                background-color: {theme['accent']};
                color: white;
                border: none;
            }}

            QPushButton#disconnectButton {{
                padding: 12px;
                background-color: #D32F2F; /* Red color */
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}

            QPushButton#disconnectButton:hover {{
                background-color: #B71C1C; /* Darker red on hover */
            }}

            QPushButton#disconnectButton:pressed {{
                background-color: #9A0007; /* Even darker red when clicked */
            }}
            
        """)