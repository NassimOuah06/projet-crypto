from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QLineEdit, QTableWidget, 
                           QTableWidgetItem, QComboBox, QHeaderView, QScrollArea, 
                           QMessageBox, QDialog, QDateTimeEdit)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
import requests

class AppointmentsPage(QWidget):
    BASE_API_URL = "http://127.0.0.1:8000/api/pat/consultations/"

    def __init__(self, theme_manager, token, user_id):
        super().__init__()
        self.theme_manager = theme_manager
        self.user_id = user_id
        self.token = token
        self.all_appointments = []
        self.setup_ui()
        self.load_appointments_data()

    def load_appointments_data(self):
        try:
            response = requests.get(
                self.BASE_API_URL, params={"id": self.user_id},
                headers={"Authorization": f"Token {self.token}"
                })
            if response.status_code == 200:
                self.all_appointments = response.json()
                self.apply_filters()
            else:
                QMessageBox.critical(self, "Erreur", f"Échec de récupération des données: {response.status_code}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Impossible de se connecter au serveur: {str(e)}")

    def setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Section Bienvenue
        welcome_frame = QFrame()
        welcome_frame.setObjectName("welcomeFrame")
        welcome_layout = QVBoxLayout(welcome_frame)
        
        title = QLabel("Gestion des Rendez-vous")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        subtitle = QLabel("Gérez et surveillez tous les rendez-vous médicaux")
        subtitle.setObjectName("subtitle")
        
        welcome_layout.addWidget(title)
        welcome_layout.addWidget(subtitle)
        layout.addWidget(welcome_frame)
        
        # Cartes Statistiques
        stats_layout = QHBoxLayout()
        self.stat_cards = [
            self.create_stat_card("Rendez-vous Totaux", "0", "📅", "Total des consultations"),
            self.create_stat_card("Aujourd'hui", "0", "🕒", "Rendez-vous du jour"),
            self.create_stat_card("À venir", "0", "🔜", "Prochains rendez-vous")
        ]
        for card in self.stat_cards:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)
        
        # Recherche et Filtre
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par patient, médecin ou ID...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.apply_filters)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Tous statuts", "Planifié", "Confirmé", "Terminé", "Annulé"])
        self.status_combo.setObjectName("filterCombo")
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        
        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(self.status_combo, 2)
        layout.addWidget(search_frame)
        
        # Tableau des Rendez-vous
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        
        table_header = QHBoxLayout()
        table_title = QLabel("Liste des Rendez-vous")
        table_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        table_header.addWidget(table_title)
        table_header.addStretch()
        table_layout.addLayout(table_header)
        
        self.table = QTableWidget()
        self.table.setObjectName("appointmentsTable")
        self.setup_table()
        table_layout.addWidget(self.table)
        
        # Actions Tableau
        actions_layout = QHBoxLayout()
        for btn_text in ["📊 Exporter", "🖨️ Imprimer"]:
            btn = QPushButton(btn_text)
            btn.setObjectName("secondaryButton")
            btn.setFixedWidth(120)
            actions_layout.addWidget(btn)
        
        actions_layout.addStretch()
        table_layout.addLayout(actions_layout)
        layout.addWidget(table_frame)
        
        scroll_area.setWidget(main_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

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
        value_label.setObjectName("cardValue")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("cardSubtitle")
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        
        return card
    
    def update_stat_cards(self, appointments):
        total = len(appointments)
        today = len([a for a in appointments if a.get("date_deb", "").startswith(QDateTime.currentDateTime().toString("yyyy-MM-dd"))])
        upcoming = len([a for a in appointments if QDateTime.fromString(a.get("date_deb", ""), "yyyy-MM-dd HH:mm:ss") > QDateTime.currentDateTime()])
        
        stats_data = [str(total), str(today), str(upcoming)]
        for card, value in zip(self.stat_cards, stats_data):
            value_label = card.findChild(QLabel, "cardValue")
            if value_label:
                value_label.setText(value)

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        status_filter = self.status_combo.currentText()
        
        filtered = []
        for appointment in self.all_appointments:
            med = appointment.get("medecin", {}).get("user", {})
            pat = appointment.get("patient", {}).get("user", {})
            
            med_name = f"{med.get('first_name', '')} {med.get('last_name', '')}".lower()
            pat_name = f"{pat.get('first_name', '')} {pat.get('last_name', '')}".lower()
            
            matches_search = (search_text in str(appointment.get("id", "") or 
                            search_text in med_name or 
                            search_text in pat_name))
            
            matches_status = (status_filter == "Tous statuts" or 
                            status_filter.lower() in appointment.get("observation", "").lower())
            
            if matches_search and matches_status:
                filtered.append(appointment)
                
        self.update_appointments_display(filtered)
        
    def update_appointments_display(self, appointments):
        self.update_stat_cards(appointments)
        self.populate_table(appointments)
        
    def setup_table(self):
        headers = ["ID", "Médecin", "Patient", "Date Début", "Date Fin", "Observation", "Condition", "Actions"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        header_style = f"""
            QHeaderView::section {{
                background-color: {self.theme_manager.current_theme['bg_secondary']};
                color: {self.theme_manager.current_theme['text_primary']};
                padding: 5px;
                font-weight: bold;
                border: 1px solid {self.theme_manager.current_theme['border']};
            }}
        """
        self.table.horizontalHeader().setStyleSheet(header_style)
        self.table.setMinimumHeight(300)

    def populate_table(self, appointments):
        self.table.setRowCount(len(appointments))

        if not appointments:
            self.table.setRowCount(1)
            item = QTableWidgetItem("Aucune consultation disponible")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, self.table.columnCount())
            return

        for row, appointment in enumerate(appointments):
            med = appointment.get("medecin", {}).get("user", {})
            pat = appointment.get("patient", {}).get("user", {})

            cells = [
                str(appointment.get("id", "N/A")),
                f"Dr {med.get('first_name', 'N/A')} {med.get('last_name', 'N/A')}",
                f"{pat.get('first_name', 'N/A')} {pat.get('last_name', 'N/A')}",
                appointment.get("date_deb", "N/A"),
                appointment.get("date_fin", "N/A"),
                appointment.get("observation", "N/A"),
                appointment.get("condition_medicale", "N/A")
            ]

            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

            # Boutons d'action
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, a=appointment: self.view_appointment(a))
            actions_layout.addWidget(view_btn)

            self.table.setCellWidget(row, len(cells), actions_widget)

    def view_appointment(self, appointment):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Détails Rendez-vous #{appointment.get('id', '')}")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: white;
                font-family: Arial;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("DÉTAILS DU RENDEZ-VOUS")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #3498db;
                padding-bottom: 10px;
                border-bottom: 1px solid #3498db;
            }
        """)
        layout.addWidget(title)

        med = appointment.get("medecin", {}).get("user", {})
        pat = appointment.get("patient", {}).get("user", {})

        details = {
            "ID": str(appointment.get("id", "N/A")),
            "Médecin": f"Dr {med.get('first_name', 'N/A')} {med.get('last_name', 'N/A')}",
            "Patient": f"{pat.get('first_name', 'N/A')} {pat.get('last_name', 'N/A')}",
            "Date Début": appointment.get("date_deb", "N/A"),
            "Date Fin": appointment.get("date_fin", "N/A"),
            "Observation": appointment.get("observation", "N/A"),
            "Condition Médicale": appointment.get("condition_medicale", "N/A")
        }

        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(10)

        for label, value in details.items():
            h_layout = QHBoxLayout()

            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-weight: bold;")
            h_layout.addWidget(lbl)

            val = QLabel(value)
            val.setStyleSheet("""
                QLabel {
                    background-color: #34495e;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
            h_layout.addWidget(val)

            frame_layout.addLayout(h_layout)

        layout.addWidget(frame)
        layout.addStretch()

        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()