from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

# 🏥 Modèle Utilisateur (Médecin, Patient, Admin)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('med', 'Médecin'),
        ('pat', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

# 👨‍⚕️ Modèle Médecin
class Med(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, 
        limit_choices_to={'role': 'med'}, 
        related_name="medecin", 
        unique=True
    )
    specialite = models.CharField(max_length=100)  # Spécialité médicale

    def __str__(self):
        return f"Dr {self.user.first_name} {self.user.last_name} - {self.specialite}"

# 🧑‍⚕️ Modèle Patient
class Pat(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, 
        limit_choices_to={'role': 'pat'}, 
        related_name="patient", 
        unique=True
    )
    etat_traitement = models.CharField(
        max_length=15,
        choices=[("traité", "Traité"), ("non_traité", "Non traité")],
        default="non_traité"
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_etat_traitement_display()}"

# 📁 Modèle Dossier Médical
class Dossier(models.Model):
    ACCES_CHOICES = [
        ("confidentiel", "Confidentiel"),
        ("public", "Public"),
        ("sensible", "Sensible"),
    ]

    patient = models.ForeignKey(Pat, on_delete=models.CASCADE, related_name="dossiers")
    medecins = models.ManyToManyField(Med, related_name="dossiers")  # Médecins ayant accès
    description = models.TextField()  # Stockage des données chiffrées
    date_creation = models.DateTimeField(default=timezone.now)
    acces = models.CharField(max_length=15, choices=ACCES_CHOICES, default="confidentiel")
    nonce = models.BinaryField(default=b'')  # ⚠ Ajout d'une valeur par défaut temporaire
    tag = models.BinaryField(default=b'')  # ⚠ Même chose pour le tag
    

    def __str__(self):
        return f"Dossier de {self.patient.user.first_name} {self.patient.user.last_name} - {self.get_acces_display()}"

    def encrypt_data(self, data):
        """ Chiffre les données du dossier avec AES-GCM. """
        key = SHA256.new(self.patient.user.username.encode()).digest()  # Clé basée sur l'ID patient
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        
        self.description = ciphertext.hex()
        self.nonce = cipher.nonce
        self.tag = tag
        self.save()

    def decrypt_data(self, user):
        """ Déchiffre les données uniquement si l'utilisateur a l'accès. """
        if user.role == 'pat' and user == self.patient.user:
            key = SHA256.new(user.username.encode()).digest()
        elif user.role == 'med' and self.medecins.filter(user=user).exists():
            key = SHA256.new(self.patient.user.username.encode()).digest()
        else:
            return "Accès refusé."
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=self.nonce)
        try:
            decrypted_data = cipher.decrypt_and_verify(bytes.fromhex(self.description), self.tag)
            return decrypted_data.decode('utf-8')
        except (ValueError, KeyError):
            return "Échec du déchiffrement."

# 📅 Modèle Consultation Médicale
class Consultation(models.Model):
    patient = models.ForeignKey(Pat, on_delete=models.CASCADE, related_name="consultations")
    medecin = models.ForeignKey(Med, on_delete=models.CASCADE, related_name="consultations")
    date_deb = models.DateTimeField()
    date_fin = models.DateTimeField()
    observation = models.TextField()
    condition_medicale = models.TextField()

    def clean(self):
        """ Validation : s'assurer que date_fin est après date_deb """
        if self.date_fin <= self.date_deb:
            raise ValidationError("La date de fin doit être après la date de début.")

    def __str__(self):
        return f"Consultation entre Dr {self.medecin.user.last_name} et {self.patient.user.last_name}"
