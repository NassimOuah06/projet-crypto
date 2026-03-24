from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QLineEdit, QTableWidget, 
                           QTableWidgetItem, QComboBox, QHeaderView, QScrollArea, 
                           QMessageBox, QDialog, QDateTimeEdit, QTextEdit)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
import requests

class AppointmentsPage(QWidget):
    BASE_API_URL = "http://127.0.0.1:8000/api/med/consultations/"

    def __init__(self, theme_manager, token, user_id):
        super().__init__()
        self.theme_manager = theme_manager
        self.token = token
        self.user_id = user_id
        self.all_appointments = []
        self.setup_ui()
        self.load_appointments_data()

    def load_appointments_data(self):
        try:
            response = requests.get(self.BASE_API_URL, headers={"Authorization": f"Token {self.token}"}, params={"id": self.user_id})
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
        add_appointment_btn = QPushButton("➕ New Appointment")
        add_appointment_btn.setObjectName("primaryButton")
        add_appointment_btn.setFixedWidth(150)
        add_appointment_btn.clicked.connect(self.add_appointment)
        actions_layout.addWidget(add_appointment_btn)

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
        
        today_date = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        now = QDateTime.currentDateTime()

        today = 0
        upcoming = 0

        for a in appointments:
            date_deb_str = a.get("date_deb", "")
            
            if not date_deb_str:
                continue  # Ignore les entrées sans date_deb

            # Utilisation du format ISO 8601
            date_deb = QDateTime.fromString(date_deb_str, Qt.DateFormat.ISODate)
            if not date_deb.isValid():
                print(f"⚠️ Date invalide : {date_deb_str}")
                continue  # Ignore les dates invalides
            
            if date_deb.toString("yyyy-MM-dd") == today_date:
                today += 1
            if date_deb > now:
                upcoming += 1  # Seules les dates futures comptent comme "upcoming"

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
            view_btn.setObjectName("iconButton")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, a=appointment: self.view_appointment(a))
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.setObjectName("iconButton")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda _, a=appointment: self.edit_appointment(a))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Supprimer")
            delete_btn.setObjectName("iconButton")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda _, a=appointment: self.delete_appointment(a))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, len(cells), actions_widget)
    
    def add_appointment(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une Consultation")
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
            QLineEdit, QComboBox, QDateTimeEdit, QTextEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 3px;
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
        title = QLabel("AJOUTER UNE CONSULTATION")
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

        # Création des champs de formulaire
        patient_dropdown = QComboBox()
        date_debut = QDateTimeEdit()
        date_fin = QDateTimeEdit()
        observation = QTextEdit()
        condition_medicale = QTextEdit()

        fields = [
            ("Patient:", patient_dropdown),
            ("Date de début:", date_debut),
            ("Date de fin:", date_fin),
            ("Observation:", observation),
            ("Condition Médicale:", condition_medicale),
        ]

        # Frame pour les champs
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(5)

        for label_text, field in fields:
            field_layout = QVBoxLayout()
            
            label = QLabel(label_text)
            field_layout.addWidget(label)
            
            field.setMinimumHeight(20)
            field_layout.addWidget(field)
            
            form_layout.addLayout(field_layout)

        layout.addWidget(form_frame)
        layout.addStretch()

        # Bouton de soumission
        submit_btn = QPushButton("Ajouter Consultation")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)

        def send_data():
            """ Envoie les données de la consultation à l'API """
            patient_id = patient_dropdown.currentData()
            if patient_id is None:  # Fallback si currentData() ne marche pas
                patient_id = patient_dropdown.currentText().split()[0]  # Prend l'ID affiché

            consultation_data = {
                "patient_id": int(patient_id),  # Récupère l'ID du patient
                "medecin_id": int(self.user_id),  # ID du médecin actuel
                "date_deb": date_debut.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                "date_fin": date_fin.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                "observation": observation.toPlainText().strip(),
                "condition_medicale": condition_medicale.toPlainText().strip(),
            }

            if not all(consultation_data.values()):
                QMessageBox.warning(dialog, "Erreur", "Tous les champs sont requis.")
                return

            try:
                response = requests.post(
                    self.BASE_API_URL+'add/',  
                    headers={"Authorization": f"Token {self.token}"},
                    json=consultation_data
                )

                if response.status_code == 201:
                    QMessageBox.information(dialog, "Succès", "Consultation ajoutée avec succès!")
                    dialog.close()
                    self.load_appointments_data()
                else:
                    error = response.json().get('detail', 'Échec de l’ajout de la consultation.')
                    QMessageBox.critical(dialog, "Erreur", error)
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(dialog, "Erreur", f"Erreur de connexion: {str(e)}")

        submit_btn.clicked.connect(send_data)
        layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Charger la liste des patients et médecins
        self.populate_dropdown(fields[0][1], "http://127.0.0.1:8000/api/med/patients/")  # Load patients

        dialog.exec()

    def populate_dropdown(self, combo_box, api_url):
        """ Remplit une QComboBox avec des données d'API """
        try:
            response = requests.get(api_url, headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                data = response.json()
                print("Réponse API:", data)  # Débogage pour voir la structure des données
                
                # Vérifie si les noms sont directement accessibles ou dans `user`
                for item in data:
                    patient_id = item["id"]
                    first_name = item.get("first_name", item.get("user", {}).get("first_name", ""))
                    last_name = item.get("last_name", item.get("user", {}).get("last_name", ""))

                    combo_box.addItem(f"{patient_id} - {first_name} {last_name}", patient_id)  # Associe l'ID au texte
            else:
                QMessageBox.warning(None, "Erreur", "Impossible de charger les données.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(None, "Erreur", f"Erreur de connexion: {str(e)}")

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

        pat = appointment.get("patient", {}).get("user", {})

        details = {
            "ID": str(appointment.get("id", "N/A")),
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
    
    def edit_appointment(self, appointment):
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier consultation")
        dialog.setFixedSize(500, 550)

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
            QLineEdit, QDateTimeEdit, QTextEdit {
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
        title = QLabel("MODIFIER RENDEZ-VOUS")
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

        # Récupérer les données de l'objet
        date_deb = QDateTimeEdit(QDateTime.fromString(appointment.get("date_deb"), Qt.DateFormat.ISODate))
        date_deb.setCalendarPopup(True)
        date_fin = QDateTimeEdit(QDateTime.fromString(appointment.get("date_fin"), Qt.DateFormat.ISODate))
        date_fin.setCalendarPopup(True)
        
        observation = QTextEdit()
        observation.setText(appointment.get("observation", ""))

        condition_medicale = QTextEdit()
        condition_medicale.setText(appointment.get("condition_medicale", ""))
        
        # Organisation des champs
        fields = [
            ("Date Début:", date_deb),
            ("Date Fin:", date_fin),
            ("Observation:", observation),
            ("Condition Médicale:", condition_medicale)
        ]
        
        for label_text, field in fields:
            field_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            field_layout.addWidget(label)
            field.setMinimumHeight(35)
            field_layout.addWidget(field)
            layout.addLayout(field_layout)

        layout.addStretch()

        # Bouton Sauvegarder
        save_btn = QPushButton("Sauvegarder les modifications")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_appointment_changes(
            appointment["id"],
            {
                "date_deb": date_deb.dateTime().toString(Qt.DateFormat.ISODate),
                "date_fin": date_fin.dateTime().toString(Qt.DateFormat.ISODate),
                "observation": observation.toPlainText(),
                "condition_medicale": condition_medicale.toPlainText()
            },
            dialog
        ))
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()

    def save_appointment_changes(self, appointment_id, data, dialog):
        try:
            response = requests.put(
                f"{self.BASE_API_URL}update/{appointment_id}/",
                headers={"Authorization": f"Token {self.token}"},
                json=data
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Rendez-vous mis à jour avec succès !")
                dialog.close()
                self.load_appointments_data()
            else:
                error = response.json()
                QMessageBox.critical(self, "Error", f"Mise à jour échouée: {error}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Erreur de connexion: {str(e)}")


    def delete_appointment(self, appointment):
        reply = QMessageBox.question(
            self,
            "Confirmer suppression",
            f"Voulez-vous vraiment supprimer {appointment['id']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete(
                    f"{self.BASE_API_URL}delete/{appointment['id']}/",
                    headers={"Authorization": f"Token {self.token}"}
                )
                
                if response.status_code == 204:
                    QMessageBox.information(self, "Succès", "appointment supprimé avec succès!")
                    self.load_appointments_data()
                else:
                    error = response.json().get('detail', 'Erreur inconnue')
                    QMessageBox.critical(self, "Erreur", f"Échec de la suppression: {error}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Erreur", f"Erreur de connexion: {str(e)}")