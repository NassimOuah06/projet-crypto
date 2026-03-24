from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QLineEdit, QTableWidget, 
                           QTableWidgetItem, QComboBox, QHeaderView, QScrollArea, 
                           QMessageBox, QDateEdit, QFileDialog, QDialog, QFormLayout)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import requests
import csv
from datetime import datetime

class RepportsPage(QWidget):
    API_URL = "http://127.0.0.1:8000/api/pat/dossiers/"
    
    def __init__(self, theme_manager, token, user_id):
        super().__init__()
        self.theme_manager = theme_manager
        self.user_id = user_id
        self.token = token
        self.setup_ui()
        self.load_repports_data()

    def load_repports_data(self):
        """Charger les données des dossiers depuis l'API"""
        try:
            response = requests.get(
                self.API_URL, 
                headers={"Authorization": f"Token {self.token}"},
                params={"id": self.user_id}
            )
            
            if response.status_code == 200:
                dossiers = response.json()
                self.populate_table(dossiers)
                self.total_dossiers_label.setText(f"📁 {len(dossiers)}")
            else:
                QMessageBox.critical(
                    self, 
                    "Erreur", 
                    f"Échec de récupération des données: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self, 
                "Erreur de connexion", 
                f"Impossible de se connecter au serveur: {str(e)}"
            )

    def show_dossier_details(self, dossier_id):
        """Afficher les détails complets d'un dossier"""
        try:
            response = requests.get(
                f"http://127.0.0.1:8000/api/pat/dossiers/{dossier_id}/",
                query={"id": self.user_id},
                headers={"Authorization": f"Token {self.token}"},
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

            # Bouton de consultation
            view_btn = QPushButton("👁️ Voir")
            view_btn.setToolTip("Consulter ce dossier")
            view_btn.setObjectName("viewButton")
            view_btn.setFixedSize(80, 30)
            view_btn.clicked.connect(lambda _, id=dossier_id: self.show_dossier_details(id))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            actions_layout.addWidget(view_btn)
            
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
        
        # Bouton d'export
        actions_layout = QHBoxLayout()
        
        export_btn = QPushButton("📊 Exporter en CSV")
        export_btn.setObjectName("primaryButton")
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