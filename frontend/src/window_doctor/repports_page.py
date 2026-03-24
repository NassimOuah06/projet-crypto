from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QLineEdit, QTableWidget, 
                           QTableWidgetItem, QComboBox, QHeaderView, QScrollArea, 
                           QMessageBox, QDateEdit, QDateTimeEdit, QFileDialog, QDialog, QFormLayout, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import requests
import csv
from datetime import datetime

class RepportsPage(QWidget):
    API_URL = "http://127.0.0.1:8000/api/med/dossiers/"
    
    def __init__(self, theme_manager, token, user_id):
        super().__init__()
        self.theme_manager = theme_manager
        self.token = token
        self.user_id = user_id  # ID de l'utilisateur connecté
        self.setup_ui()
        self.load_reports_data()

    def load_reports_data(self):
        """Charger les données des dossiers depuis l'API"""
        try:
            # Étape 1 : Récupérer l'ID du médecin depuis l'API
            med_response = requests.get(
                f"http://127.0.0.1:8000/api/med/med/from_user/{self.user_id}/",
                headers={"Authorization": f"Token {self.token}"}
            )

            print("Réponse API médecin:", med_response.status_code, med_response.text)  # 🔍 Debug

            if med_response.status_code != 200:
                QMessageBox.critical(self, "Erreur", "Impossible de récupérer le médecin")
                return

            medecin_id = med_response.json().get("medecin_id")
            print("ID du médecin récupéré:", medecin_id)  # 🔍 Debug

            if not medecin_id:
                QMessageBox.critical(self, "Erreur", "Aucun médecin trouvé pour cet utilisateur")
                return

            # Étape 2 : Charger les dossiers du médecin
            response = requests.get(
                f"{self.API_URL}",
                headers={"Authorization": f"Token {self.token}"},
                params={"id": medecin_id}  # ✅ Utiliser medecin_id
            )

            print("Réponse API dossiers:", response.status_code, response.text)  # 🔍 Debug

            if response.status_code == 200:
                dossiers = response.json()
                print("Dossiers reçus:", dossiers)  # 🔍 Debug
                self.populate_table(dossiers)
                self.total_dossiers_label.setText(f"📁 {len(dossiers)}")
            else:
                QMessageBox.critical(
                    self, "Erreur", f"Échec de récupération des données: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self, "Erreur de connexion", f"Impossible de se connecter au serveur: {str(e)}"
            )


    def show_dossier_details(self, dossier_id):
        """Afficher les détails complets d'un dossier"""
        try:
            response = requests.get(
                f"http://127.0.0.1:8000/api/med/dossiers/{dossier_id}/",
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                dossier = response.json()
                self.display_dossier_dialog(dossier)
            else:
                QMessageBox.critical(
                    self, 
                    "Erreur", 
                    f"Impossible de récupérer les détails: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self, 
                "Erreur de connexion", 
                f"Connexion au serveur impossible: {str(e)}"
            )

    def display_dossier_dialog(self, dossier):
        """Afficher une fenêtre modale avec les détails du dossier"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Détails du dossier - ID: {dossier.get('id', 'N/A')}")
        dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Informations de base
        patient = dossier.get('patient', {}).get('user', {})
        patient_name = f"{patient.get('first_name', 'N/A')} {patient.get('last_name', 'N/A')}"
        
        form_layout.addRow("ID du dossier:", QLabel(str(dossier.get('id', 'N/A'))))
        form_layout.addRow("Patient:", QLabel(patient_name))
        form_layout.addRow("Date de création:", QLabel(dossier.get('date_creation', 'N/A')))
        form_layout.addRow("Niveau d'accès:", QLabel(dossier.get('acces', 'N/A')))
        
        # Liste des médecins
        doctors_list = dossier.get('medecins', [])
        doctors_names = "\n".join([
            f"- {doc.get('user', {}).get('first_name', 'N/A')} {doc.get('user', {}).get('last_name', 'N/A')}"
            for doc in doctors_list
        ]) if doctors_list else "Aucun médecin associé"
        
        doctors_label = QLabel(doctors_names)
        doctors_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form_layout.addRow("Médecins:", doctors_label)
        
        # Description complète
        description = QLabel(dossier.get('decrypted_description', 'N/A'))
        description.setWordWrap(True)
        description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form_layout.addRow("Description:", description)
        
        layout.addLayout(form_layout)
        
        # Bouton de fermeture
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.setLayout(layout)
        dialog.exec()

    def populate_table(self, data):
        """Remplir le tableau avec les données des dossiers"""
        self.table.setRowCount(len(data))

        for row, dossier in enumerate(data):
            doctors_list = dossier.get("medecins", [])
            patient = dossier.get("patient", {}).get("user", {})
            
            dossier_id = str(dossier.get("id", "N/A"))
            patient_name = f"{patient.get('first_name', 'N/A')} {patient.get('last_name', 'N/A')}"
            doctors_list_name = ", ".join([
                f"{doctor.get('user', {}).get('first_name', 'N/A')} {doctor.get('user', {}).get('last_name', 'N/A')}"
                for doctor in doctors_list
            ]) if doctors_list else "N/A"
            
            date_creation = dossier.get("date_creation", "N/A")
            full_description = dossier.get("decrypted_description", "N/A")
            short_description = (full_description[:50] + '...') if len(full_description) > 50 else full_description
            access = dossier.get("acces", "N/A")

            values = [dossier_id, patient_name, doctors_list_name, date_creation, short_description, access]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 4:  # Colonne Description
                    item.setToolTip(full_description)
                self.table.setItem(row, col, item)
                self.table.setRowHeight(row, 40)

            # Bouton de consultation
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Consulter ce dossier")
            view_btn.setObjectName("iconButton")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda _, id=dossier_id: self.show_dossier_details(id))
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.setObjectName("iconButton")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda _, d=dossier: self.edit_report(d))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Supprimer")
            delete_btn.setObjectName("iconButton")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda _, d=dossier: self.delete_report(d["id"]))
            
            

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, len(values), actions_widget)

    def export_to_csv(self):
        """Exporter les données du tableau en CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter les dossiers",
                f"dossiers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "Fichiers CSV (*.csv)"
            )

            if not file_path:
                return

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # En-têtes
                headers = []
                for col in range(self.table.columnCount() - 1):
                    headers.append(self.table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Données
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount() - 1):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(
                self, 
                "Export réussi", 
                f"Les données ont été exportées dans:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur d'export", 
                f"Erreur lors de l'export:\n{str(e)}"
            )

    def apply_filters(self):
        """Appliquer les filtres de date et recherche"""
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        search_text = self.search_input.text().lower()
        
        try:
            response = requests.get(
                self.API_URL,
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                dossiers = response.json()
                filtered_data = []
                
                for dossier in dossiers:
                    # Filtre par date
                    dossier_date = dossier.get("date_creation", "")
                    if date_from <= dossier_date <= date_to:
                        # Filtre par recherche
                        patient = dossier.get("patient", {}).get("user", {})
                        patient_name = f"{patient.get('first_name', '').lower()} {patient.get('last_name', '').lower()}"
                        
                        doctors_list = dossier.get("medecins", [])
                        doctors_names = " ".join([
                            f"{doc.get('user', {}).get('first_name', '').lower()} {doc.get('user', {}).get('last_name', '').lower()}"
                            for doc in doctors_list
                        ])
                        
                        if (search_text in patient_name) or (search_text in doctors_names):
                            filtered_data.append(dossier)
                
                self.populate_table(filtered_data)
                self.total_dossiers_label.setText(f"📁 {len(filtered_data)}")
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self, 
                "Erreur", 
                f"Erreur lors du filtrage: {str(e)}"
            )

    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        welcome_frame = QFrame()
        welcome_frame.setObjectName("welcomeFrame")
        welcome_layout = QVBoxLayout(welcome_frame)
        
        title = QLabel("Consultation des Dossiers")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        subtitle = QLabel("Consulter les dossiers patients (lecture seule)")
        subtitle.setObjectName("subtitle")
        
        welcome_layout.addWidget(title)
        welcome_layout.addWidget(subtitle)
        layout.addWidget(welcome_frame)
        
        # Statistiques
        stats_layout = QHBoxLayout()
        
        card = QFrame()
        card.setObjectName("statCard")
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel("Total des Dossiers")
        title_label.setObjectName("cardTitle")
        
        self.total_dossiers_label = QLabel("📁 0")
        self.total_dossiers_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(self.total_dossiers_label)
        
        stats_layout.addWidget(card)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Barre de recherche et filtres
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par patient ou médecin...")
        self.search_input.setObjectName("searchInput")
        
        # Filtres par date
        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("Date de création:"))
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        
        date_filter_layout.addWidget(self.date_from)
        date_filter_layout.addWidget(QLabel("à"))
        date_filter_layout.addWidget(self.date_to)
        
        filter_btn = QPushButton("Filtrer")
        filter_btn.setObjectName("primaryButton")
        filter_btn.clicked.connect(self.apply_filters)
        
        search_layout.addWidget(self.search_input, 3)
        search_layout.addLayout(date_filter_layout, 2)
        search_layout.addWidget(filter_btn, 1)
        
        layout.addWidget(search_frame)
        
        # Tableau des dossiers
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        
        table_header = QHBoxLayout()
        table_title = QLabel("Liste des Dossiers")
        table_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        table_header.addWidget(table_title)
        table_header.addStretch()
        
        table_layout.addLayout(table_header)
        
        self.table = QTableWidget()
        self.table.setObjectName("dossiersTable")
        self.setup_table()
        table_layout.addWidget(self.table)

        # Actions Tableau
        actions_layout = QHBoxLayout()
        add_repport_btn = QPushButton("➕ New Repport")
        add_repport_btn.setObjectName("primaryButton")
        add_repport_btn.setFixedWidth(150)
        add_repport_btn.clicked.connect(self.add_report)
        actions_layout.addWidget(add_repport_btn)

        
        export_btn = QPushButton("📊 Exporter en CSV")
        export_btn.setObjectName("secondaryButton")
        export_btn.clicked.connect(self.export_to_csv)
        export_btn.setFixedWidth(150)
        
        actions_layout.addWidget(export_btn)
        actions_layout.addStretch()
        table_layout.addLayout(actions_layout)
        
        layout.addWidget(table_frame)
        
        scroll_area.setWidget(main_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def setup_table(self):
        """Configurer le tableau des dossiers"""
        headers = [
            "ID", 
            "Patient", 
            "Médecins", 
            "Date Création", 
            "Description", 
            "Accès", 
            "Actions"
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(4, 200)
        

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
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setMinimumHeight(300)

    def add_report(self):
        """ Opens a dialog to add a medical report (Dossier) """

        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un Dossier Médical")
        dialog.setFixedSize(500, 450)

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
            QLineEdit, QComboBox, QTextEdit {
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

        # Title
        title = QLabel("AJOUTER UN DOSSIER MÉDICAL")
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

        # Fields
        patient_dropdown = QComboBox()
        self.populate_dropdown(patient_dropdown, "http://127.0.0.1:8000/api/med/patients/")  # Load patients

        access_dropdown = QComboBox()
        access_dropdown.addItems(["Confidentiel", "Public", "Sensible"])

        description = QTextEdit()
        description.setPlaceholderText("Entrez la description du dossier médical...")

        # Layout for form fields
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Patient:"))
        form_layout.addWidget(patient_dropdown)
        form_layout.addWidget(QLabel("Niveau d'accès:"))
        form_layout.addWidget(access_dropdown)
        form_layout.addWidget(QLabel("Description:"))
        form_layout.addWidget(description)

        layout.addLayout(form_layout)

        # Submit button
        submit_btn = QPushButton("Ajouter Dossier")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)

        def send_data():
            """ Envoie les données du rapport à l'API """
            patient_id = patient_dropdown.currentData()
            if patient_id is None:  
                patient_id = patient_dropdown.currentText().split()[0]  
            
            try:
                # 🔹 Récupérer medecin_id à partir du user_id
                response = requests.get(
                    f"http://127.0.0.1:8000/api/med/med/from_user/{self.user_id}/",
                    headers={"Authorization": f"Token {self.token}"}
                )
                if response.status_code == 200:
                    medecin_id = response.json().get("medecin_id")  # Récupérer l'ID du médecin
                else:
                    QMessageBox.critical(dialog, "Erreur", "Impossible de récupérer l'ID du médecin.")
                    return
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(dialog, "Erreur", f"Erreur de connexion: {str(e)}")
                return
            print("##################",patient_id, medecin_id)  # <---- Ajout pour débogage
            report_data = {
                "patient_id": int(patient_id),  # S'assurer que c'est un entier
                "patient": int(patient_id),  # S'assurer que c'est un entier
                "medecins": [medecin_id],  # Liste contenant l'ID du médecin actuel
                "medecins_id": [medecin_id],  # Liste contenant l'ID du médecin actuel
                "description": description.toPlainText().strip(),
                "acces": access_dropdown.currentText().lower(),
            }

            # Vérification des champs
            if not all(report_data.values()):
                QMessageBox.warning(dialog, "Erreur", "Tous les champs sont requis.")
                return

            try:
                response = requests.post(
                    f"{self.API_URL}add/",
                    headers={"Authorization": f"Token {self.token}"},
                    json=report_data
                )
                print("🛠️ Debug API Response:", response.status_code, response.json())  # <---- Ajout pour débogage

                if response.status_code == 201:
                    QMessageBox.information(dialog, "Succès", "Dossier ajouté avec succès!")
                    dialog.close()
                    self.load_reports_data()
                else:
                    error = response.json().get("detail", "Échec de l’ajout du dossier.")
                    QMessageBox.critical(dialog, "Erreur", error)
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(dialog, "Erreur", f"Erreur de connexion: {str(e)}")

        submit_btn.clicked.connect(send_data)
        layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def edit_report(self, report):
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier Rapport Médical")
        dialog.setFixedSize(500, 550)

        # Appliquer le style
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
            QLineEdit, QTextEdit, QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 5px;
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

        # Titre
        title = QLabel("MODIFIER RAPPORT MÉDICAL")
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

        # Récupérer les données existantes
        description = QTextEdit()
        description.setText(report.get("description", ""))

        acces_choices = ["Confidentiel", "Public", "Sensible"]
        acces_map = {"confidentiel": "Confidentiel", "public": "Public", "sensible": "Sensible"}
        acces_reverse_map = {v: k for k, v in acces_map.items()}

        acces_dropdown = QComboBox()
        acces_dropdown.addItems(acces_choices)
        acces_dropdown.setCurrentText(acces_map.get(report.get("acces", "confidentiel"), "Confidentiel"))

        # Organisation des champs
        fields = [
            ("Description:", description),
            ("Niveau d'accès:", acces_dropdown)
        ]

        for label_text, field in fields:
            field_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            field_layout.addWidget(label)
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
        save_btn.clicked.connect(lambda: self.save_report_changes(
            report["id"],
            {
                "description": description.toPlainText(),
                "acces": acces_reverse_map[acces_dropdown.currentText()]
            },
            dialog
        ))
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()


    def save_report_changes(self, report_id, data, dialog):
        try:
            response = requests.put(
                f"{self.API_URL}update/{report_id}/",
                headers={"Authorization": f"Token {self.token}"},
                json=data
            )

            if response.status_code == 200:
                QMessageBox.information(self, "Succès", "Rapport mis à jour avec succès !")
                dialog.close()
                self.load_reports_data()
            else:
                error = response.json()
                QMessageBox.critical(self, "Erreur", f"Mise à jour échouée: {error}")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de connexion: {str(e)}")
    
    def delete_report(self, report_id):
        """Supprimer un rapport médical"""
        try:
            response = requests.delete(
                f"{self.API_URL}delete/{report_id}/",
                headers={"Authorization": f"Token {self.token}"}
            )

            if response.status_code == 204:
                QMessageBox.information(self, "Succès", "Rapport supprimé avec succès !")
                self.load_reports_data()
            else:
                error = response.json()
                QMessageBox.critical(self, "Erreur", f"Échec de la suppression: {error}")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de connexion: {str(e)}")

