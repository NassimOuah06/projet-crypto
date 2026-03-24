from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QComboBox, QHeaderView, QScrollArea, 
                             QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests

class DoctorsPage(QWidget):
    BASE_API_URL = "http://127.0.0.1:8000/api/admin/meds/"
    ADD_API_URL = f"{BASE_API_URL}add/"
    UPDATE_API_URL = f"{BASE_API_URL}update/"
    DELETE_API_URL = f"{BASE_API_URL}delete/"

    def __init__(self, theme_manager, token):
        super().__init__()
        self.theme_manager = theme_manager
        self.token = token
        self.all_doctors = []
        self.total_doctors = 0
        self.total_spec = 0
        # Liste complète des spécialités médicales en français
        self.specialites = [
            "Toutes spécialités",
            "Cardiologie",
            "Neurologie",
            "Pédiatrie",
            "Dermatologie",
            "Orthopédie",
            "Ophtalmologie",
            "Gastro-entérologie",
            "Endocrinologie",
            "Rhumatologie",
            "Pneumologie",
            "Néphrologie",
            "Urologie",
            "Oncologie",
            "Hématologie",
            "Maladies infectieuses",
            "Psychiatrie",
            "Radiologie",
            "Anesthésiologie",
            "Médecine d'urgence",
            "Médecine générale",
            "Médecine interne",
            "Chirurgie générale",
            "Autre"
        ]
        self.setup_ui()
        self.load_doctors_data()

    def load_doctors_data(self):
        try:
            response = requests.get(self.BASE_API_URL, headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                self.all_doctors = response.json()
                self.total_doctors = len(self.all_doctors)
                self.update_stat_cards()
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
        
        title = QLabel("Gestion des Médecins")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        subtitle = QLabel("Gérez et surveillez tous les dossiers des médecins")
        subtitle.setObjectName("subtitle")
        
        welcome_layout.addWidget(title)
        welcome_layout.addWidget(subtitle)
        layout.addWidget(welcome_frame)
        
        # Cartes Statistiques
        stats_layout = QHBoxLayout()
        self.stat_cards = [
            self.create_stat_card("Médecins Totaux", "0", "👨⚕️", "Informations de la base de données")
        ]
        for card in self.stat_cards:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)
        
        # Recherche et Filtre
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher médecins par nom, spécialité ou email...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.apply_filters)
        
        self.specialty_combo = QComboBox()
        self.specialty_combo.addItems(self.specialites)
        self.specialty_combo.setObjectName("filterCombo")
        self.specialty_combo.currentTextChanged.connect(self.apply_filters)
        
        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(self.specialty_combo, 2)
        layout.addWidget(search_frame)
        
        # Tableau des Médecins
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        
        table_header = QHBoxLayout()
        table_title = QLabel("Dossiers des Médecins")
        table_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        table_header.addWidget(table_title)
        table_header.addStretch()
        table_layout.addLayout(table_header)
        
        self.table = QTableWidget()
        self.table.setObjectName("doctorsTable")
        self.setup_table()
        table_layout.addWidget(self.table)
        
        # Actions Tableau
        actions_layout = QHBoxLayout()
        add_doctor_btn = QPushButton("➕ New Patient")
        add_doctor_btn.setObjectName("primaryButton")
        add_doctor_btn.setFixedWidth(150)
        add_doctor_btn.clicked.connect(self.add_doctor)
        actions_layout.addWidget(add_doctor_btn)
        
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
            str(self.total_doctors),
        ]
        for card, value in zip(self.stat_cards, stats_data):
            value_label = card.findChild(QLabel, "cardValue")
            if value_label:
                value_label.setText(value)

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        specialite_filtre = self.specialty_combo.currentText()
        
        filtered = []
        for doctor in self.all_doctors:
            user = doctor.get("user", {})
            nom_complet = f"{user.get('first_name', '')} {user.get('last_name', '')}".lower()
            specialite = doctor.get("specialite", "").lower()
            email = user.get("email", "").lower()
            
            # Vérifier la correspondance avec la recherche
            correspond_recherche = (search_text in nom_complet or 
                                  search_text in email or 
                                  search_text in specialite)
            
            # Vérifier la correspondance avec la spécialité
            correspond_specialite = (specialite_filtre == "Toutes spécialités" or 
                                   specialite_filtre.lower() == doctor.get("specialite", "").lower())
            
            if correspond_recherche and correspond_specialite:
                filtered.append(doctor)
                
        self.update_doctors_display(filtered)
        
    def update_doctors_display(self, doctors):
        self.total_doctors = len(doctors)
        self.populate_table(doctors)
        self.update_stat_cards() 
        
    def setup_table(self):
        headers = ["ID", "Nom", "Email", "Spécialité", "Actions"]
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

    def populate_table(self, doctors):
        self.table.setRowCount(len(doctors))
        for row, doctor in enumerate(doctors):
            user = doctor.get("user", {})
            cells = [
                str(doctor.get("id", "N/A")),
                f"{user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}",
                user.get("email", "N/A"),
                doctor.get("specialite", "N/A")
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
            
            # Boutons d'action
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, d=doctor: self.view_doctor(d))
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, d=doctor: self.edit_doctor(d))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Supprimer")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, d=doctor: self.delete_doctor(d))

            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 4, actions_widget)

    def add_doctor(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un médecin")
        dialog.setFixedSize(600, 600)
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
                padding: 3px;
                selection-background-color: #3498db;
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

        title = QLabel("AJOUTER UN MÉDECIN")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #3498db;
                padding-bottom: 2px;
                border-bottom: 1px solid #3498db;
            }
        """)
        layout.addWidget(title)

        # Champs du formulaire
        fields = [
            ("Prénom:", QLineEdit()),
            ("Nom:", QLineEdit()),
            ("Email:", QLineEdit()),
            ("Nom d'utilisateur:", QLineEdit()),
            ("Mot de passe:", QLineEdit(echoMode=QLineEdit.EchoMode.Password)),
            ("Spécialité:", QComboBox())
        ]
        # Ajouter toutes les spécialités sauf "Toutes spécialités"
        fields[-1][1].addItems(self.specialites[1:])
        for label_text, field in fields:
            layout.addWidget(QLabel(label_text))
            layout.addWidget(field)
            
        submit_btn = QPushButton("Enregistrer")
        submit_btn.clicked.connect(lambda: self.submit_doctor(dialog, fields))
        layout.addWidget(submit_btn)
        dialog.exec()

    def submit_doctor(self, dialog, fields):
        data = {
            "first_name": fields[0][1].text().strip(),
            "last_name": fields[1][1].text().strip(),
            "email": fields[2][1].text().strip(),
            "username": fields[3][1].text().strip(),
            "password": fields[4][1].text().strip(),
            "specialite": fields[5][1].currentText()
        }
            
        # Validation des champs
        if not all(data.values()):
            QMessageBox.warning(dialog, "Erreur", "Tous les champs sont obligatoires")
            return
                
        try:
            response = requests.post(
                self.ADD_API_URL,
                headers={"Authorization": f"Token {self.token}"},
                json=data
            )
                
            if response.status_code == 201:
                QMessageBox.information(dialog, "Succès", "Médecin ajouté avec succès")
                dialog.close()
                self.load_doctors_data()
                self.apply_filters()
            else:
                error = response.json().get('detail', 'Erreur inconnue')
                QMessageBox.critical(dialog, "Erreur", f"Échec de l'ajout: {error}")
                    
        except Exception as e:
            QMessageBox.critical(dialog, "Erreur", f"Connexion impossible: {str(e)}")

    def view_doctor(self, doctor):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Détails du Dr {doctor.get('user', {}).get('last_name', '')}")
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

        # Titre
        title = QLabel("DÉTAILS DU MÉDECIN")
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

        user = doctor.get("user", {})
        details = {
            "ID Médecin": str(doctor.get('id', 'N/A')),
            "Prénom": user.get('first_name', 'N/A'),
            "Nom": user.get('last_name', 'N/A'),
            "Email": user.get('email', 'N/A'),
            "Spécialité": doctor.get('specialite', 'N/A')
        }

        # Cadre pour les détails
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

    def edit_doctor(self, doctor):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Modifier Dr {doctor.get('user', {}).get('last_name', '')}")
        dialog.setFixedSize(500, 500)
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
        user = doctor.get("user", {})
        title = QLabel("MODIFIER LE MÉDECIN")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #3498db;
                padding-bottom: 2px;
                border-bottom: 1px solid #3498db;
            }
        """)
        layout.addWidget(title)
        fields = [
            ("Prénom:", QLineEdit(user.get("first_name", ""))),
            ("Nom:", QLineEdit(user.get("last_name", ""))),
            ("Email:", QLineEdit(user.get("email", ""))),
            ("Spécialité:", QComboBox())
        ]
        # Ajouter toutes les spécialités sauf "Toutes spécialités"
        fields[-1][1].addItems(self.specialites[1:])
        fields[-1][1].setCurrentText(doctor.get("specialite", ""))
        for label_text, field in fields:
            layout.addWidget(QLabel(label_text))
            layout.addWidget(field)
            
        save_btn = QPushButton("Sauvegarder")
        save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                }
                QPushButton:hover {
                    background-color: #219653;
                }
                """)
        save_btn.clicked.connect(lambda: self.save_doctor_changes(doctor['id'], fields, dialog))
        layout.addWidget(save_btn)
        dialog.exec()

    def save_doctor_changes(self, doctor_id, fields, dialog):
    # Structurer les données comme attendu par le serializer
        data = {
            "user": {
                "first_name": fields[0][1].text().strip(),
                "last_name": fields[1][1].text().strip(),
                "email": fields[2][1].text().strip()
            },
            "specialite": fields[3][1].currentText()
        }
        
        try:
            response = requests.put(
                f"{self.UPDATE_API_URL}{doctor_id}/",
                headers={"Authorization": f"Token {self.token}"},
                json=data
            )
            if response.status_code == 200:
                QMessageBox.information(dialog, "Succès", "Modifications enregistrées")
                dialog.close()
                self.load_doctors_data()  # Recharger les données
            else:
                error = response.json().get('detail', response.text)
                QMessageBox.critical(dialog, "Erreur", f"Erreur du serveur: {error}")
        except Exception as e:
            QMessageBox.critical(dialog, "Erreur", f"Connexion impossible: {str(e)}")

    def delete_doctor(self, doctor):
        confirm = QMessageBox.question(
            self,
            "Confirmer suppression",
            f"Supprimer définitivement le Dr {doctor.get('user', {}).get('last_name', '')} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete(
                    f"{self.DELETE_API_URL}{doctor['id']}/",
                    headers={"Authorization": f"Token {self.token}"}
                )
                if response.status_code == 204:
                    self.load_doctors_data()
                    QMessageBox.information(self, "Succès", "Médecin supprimé")
                else:
                    error = response.json().get('detail', 'Erreur inconnue')
                    QMessageBox.critical(self, "Erreur", error)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Connexion impossible: {str(e)}")