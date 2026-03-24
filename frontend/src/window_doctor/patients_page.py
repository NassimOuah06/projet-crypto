from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QLineEdit, QTableWidget, 
                           QTableWidgetItem, QComboBox, QHeaderView, QScrollArea, 
                           QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests

class PatientsPage(QWidget):
    BASE_API_URL = "http://127.0.0.1:8000/api/med/patients/"
    ADD_API_URL = f"{BASE_API_URL}add/"
    UPDATE_API_URL = f"{BASE_API_URL}update/"
    DELETE_API_URL = f"{BASE_API_URL}delete/"
    
    def __init__(self, theme_manager, token):
        super().__init__()
        self.theme_manager = theme_manager
        self.token = token
        self.all_patients = []
        self.total_patients = 0
        self.treated_patients = 0
        self.untreated_patients = 0
        self.stat_cards = []
        self.setup_ui()
        self.load_patients_data()
    
    def load_patients_data(self):
        try:
            response = requests.get(self.BASE_API_URL, headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                self.all_patients = response.json()
                self.apply_filters()  # Applique les filtres existants
            else:
                QMessageBox.critical(self, "Error", f"Failed to fetch data: {response.status_code}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to server: {str(e)}")
    
    def setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Welcome Section
        welcome_frame = QFrame()
        welcome_frame.setObjectName("welcomeFrame")
        welcome_layout = QVBoxLayout(welcome_frame)
        
        title = QLabel("Patients Management")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        subtitle = QLabel("Manage and monitor all patient records")
        subtitle.setObjectName("subtitle")
        
        welcome_layout.addWidget(title)
        welcome_layout.addWidget(subtitle)
        layout.addWidget(welcome_frame)
        
        # Statistics Cards
        stats_layout = QHBoxLayout()
        self.stat_cards = [
            self.create_stat_card("Total Patients", "0", "👥", "Data_Base Info"),
            self.create_stat_card("Treated Patients", "0", "✅", "Data_Base Info"),
            self.create_stat_card("Untreated Patients", "0", "⚠️", "Data_Base Info")
        ]
        for card in self.stat_cards:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)
        
        # Search and Filter
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search patients by name, ID, or contact...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.apply_filters)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Status", "traité", "non_traité"])
        self.status_combo.setObjectName("filterCombo")
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        
        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(self.status_combo, 2)
        layout.addWidget(search_frame)
        
        # Patients Table
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        
        table_header = QHBoxLayout()
        table_title = QLabel("Patient Records")
        table_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        table_header.addWidget(table_title)
        table_header.addStretch()
        table_layout.addLayout(table_header)
        
        self.table = QTableWidget()
        self.table.setObjectName("patientsTable")
        self.setup_table()
        table_layout.addWidget(self.table)
        
        # Table Actions
        actions_layout = QHBoxLayout()
        # add_patient_btn = QPushButton("➕ New Patient")
        # add_patient_btn.setObjectName("primaryButton")
        # add_patient_btn.setFixedWidth(150)
        # add_patient_btn.clicked.connect(self.add_patient)
        # actions_layout.addWidget(add_patient_btn)
        
        for btn_text in ["📊 Export Data", "🖨️ Print Report"]:
            btn = QPushButton(btn_text)
            btn.setObjectName("secondaryButton")
            btn.setFixedWidth(150)
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
    
    def update_stat_cards(self):
        stats_data = [
            str(self.total_patients),
            str(self.treated_patients),
            str(self.untreated_patients)
        ]
        
        for card, value in zip(self.stat_cards, stats_data):
            value_label = card.findChild(QLabel, "cardValue")
            if value_label:
                value_label.setText(value)
    
    def apply_filters(self):
        search_text = self.search_input.text().lower()
        status_filter = self.status_combo.currentText()
        
        filtered_patients = []
        
        for patient in self.all_patients:
            user_data = patient.get("user", {})
            name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".lower()
            email = user_data.get("email", "").lower()
            patient_id = str(patient.get("id", "")).lower()
            status = patient.get("etat_traitement", "")
            
            matches_search = (search_text in name or search_text in email or search_text in patient_id)
            matches_status = (status_filter == "All Status" or status == status_filter)
            
            if matches_search and matches_status:
                filtered_patients.append(patient)
        
        self.update_patients_display(filtered_patients)
    
    def update_patients_display(self, patients):
        self.total_patients = len(patients)
        self.treated_patients = sum(1 for p in patients if p.get("etat_traitement") == "traité")
        self.untreated_patients = self.total_patients - self.treated_patients
        self.populate_table(patients)
        self.update_stat_cards()
    
    def setup_table(self):
        headers = ["ID", "Name", "Email", "Etat du Traitement", "Actions"]
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
    
    def populate_table(self, data):
        self.table.setRowCount(len(data))
        
        for row, patient in enumerate(data):
            user_data = patient.get("user", {})
            values = [
                str(patient.get("id", "N/A")),
                f"{user_data.get('first_name', 'N/A')} {user_data.get('last_name', 'N/A')}",
                user_data.get("email", "N/A"),
                patient.get("etat_traitement", "N/A")
            ]
            
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 3:
                    item.setForeground(Qt.GlobalColor.green if value == "traité" else Qt.GlobalColor.red)
                self.table.setItem(row, col, item)
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            # Bouton Voir
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir détails")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda _, p=patient: self.view_patient(p))
            
            # Bouton Modifier
            # edit_btn = QPushButton("✏️")
            # edit_btn.setToolTip("Modifier")
            # edit_btn.setFixedSize(30, 30)
            # edit_btn.clicked.connect(lambda _, p=patient: self.edit_patient(p))
            
            # Bouton Supprimer
            # delete_btn = QPushButton("🗑️")
            # delete_btn.setToolTip("Supprimer")
            # delete_btn.setFixedSize(30, 30)
            # delete_btn.clicked.connect(lambda _, p=patient: self.delete_patient(p))
            
            for btn in [view_btn]:
                btn.setObjectName("iconButton")
                actions_layout.addWidget(btn)
            
            self.table.setCellWidget(row, len(values), actions_widget)
        
    def view_patient(self, patient):
        dialog = QDialog(self)
        dialog.setWindowTitle("Détails du Patient")
        dialog.setFixedSize(500, 400)
        
        # Appliquer un style global à la boîte de dialogue
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

        # Titre
        title = QLabel("DÉTAILS DU PATIENT")
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

        user_data = patient.get("user", {})
        details = {
            "ID Patient": str(patient.get('id', 'N/A')),
            "Nom": user_data.get('first_name', 'N/A'),
            "Prénom": user_data.get('last_name', 'N/A'),
            "Email": user_data.get('email', 'N/A'),
            "Nom d'utilisateur": user_data.get('username', 'N/A'),
            "Statut": patient.get('etat_traitement', 'N/A')
        }

        # Créer un cadre pour les détails
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

        # Bouton Fermer
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()
    
    def edit_patient(self, patient):
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier Patient")
        dialog.setFixedSize(500, 450)  # Taille ajustée
        
        # Appliquer le style cohérent
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
            QLineEdit, QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #3498db;
                min-height: 30px;
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

        # Titre stylisé
        title = QLabel("MODIFIER LE PATIENT")
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

        user_data = patient.get("user", {})
        
        # Frame pour les champs
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Champs de formulaire
        first_name = QLineEdit(user_data.get("first_name", ""))
        last_name = QLineEdit(user_data.get("last_name", ""))
        email = QLineEdit(user_data.get("email", ""))
        
        status_combo = QComboBox()
        status_combo.addItems(["traité", "non_traité"])
        status_combo.setCurrentText(patient.get("etat_traitement", "non_traité"))

        # Organisation des champs
        fields = [
            ("Prénom:", first_name),
            ("Nom:", last_name),
            ("Email:", email),
            ("Statut:", status_combo)
        ]
        
        for label_text, field in fields:
            field_layout = QVBoxLayout()
            
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            field_layout.addWidget(label)
            
            field.setMinimumHeight(35)
            field_layout.addWidget(field)
            
            form_layout.addLayout(field_layout)

        layout.addWidget(form_frame)
        layout.addStretch()

        # Bouton Sauvegarder (en vert pour l'action positive)
        save_btn = QPushButton("Sauvegarder les modifications")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_patient_changes(
            patient["id"],
            {
                "user": {
                    "first_name": first_name.text(),
                    "last_name": last_name.text(),
                    "email": email.text()
                },
                "etat_traitement": status_combo.currentText()
            },
            dialog
        ))
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()
    
    def save_patient_changes(self, patient_id, data, dialog):
    # Structurer les données correctement pour le serializer
        request_data = {
            "user": {
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": data["email"]
            },
            "etat_traitement": data["etat_traitement"]
        }
        
        try:
            response = requests.put(
                f"{self.UPDATE_API_URL}{patient_id}/",
                headers={"Authorization": f"Token {self.token}"},
                json=request_data  # Envoyer les données structurées
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Patient updated successfully!")
                dialog.close()
                self.load_patients_data()
            else:
                error = response.json()
                QMessageBox.critical(self, "Error", f"Update failed: {error}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def delete_patient(self, patient):
            reply = QMessageBox.question(
                self,
                "Confirmer suppression",
                f"Voulez-vous vraiment supprimer {patient.get('user', {}).get('first_name')} {patient.get('user', {}).get('last_name')}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    response = requests.delete(
                        f"{self.DELETE_API_URL}{patient['id']}/",
                        headers={"Authorization": f"Token {self.token}"}
                    )
                    
                    if response.status_code == 204:
                        QMessageBox.information(self, "Succès", "Patient supprimé avec succès!")
                        self.load_patients_data()
                    else:
                        error = response.json().get('detail', 'Erreur inconnue')
                        QMessageBox.critical(self, "Erreur", f"Échec de la suppression: {error}")
                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur de connexion: {str(e)}")