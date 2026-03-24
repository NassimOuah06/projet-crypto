from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Med, Pat, Dossier, Consultation
from django.utils.timezone import make_aware, is_naive

User = get_user_model()

# 🔐 Serializer pour les utilisateurs (Admin, Médecins, Patients)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]

# 👨‍⚕️ Serializer pour les médecins
class MedSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Med
        fields = ["id", "user", "specialite"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data, role="med")
        med = Med.objects.create(user=user, **validated_data)
        return med

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# 🧑‍⚕️ Serializer pour les patients
class PatSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Pat
        fields = ["id", "user", "etat_traitement"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data, role="pat")
        pat = Pat.objects.create(user=user, **validated_data)
        return pat

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# 📁 Serializer pour les dossiers médicaux
class DossierSerializer(serializers.ModelSerializer):
    medecins_id = serializers.PrimaryKeyRelatedField(
        queryset=Med.objects.all(), many=True, write_only=True, required=True
    )
    medecins = MedSerializer(many=True, read_only=True)
    patient = PatSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Pat.objects.all(), write_only=True, source="patient"
    )
    decrypted_description = serializers.SerializerMethodField()  # Champ pour afficher la description déchiffrée

    class Meta:
        model = Dossier
        fields = ["id", "medecins", "medecins_id", "patient", "patient_id", "decrypted_description", "acces", "date_creation"]
        read_only_fields = ["decrypted_description"]

    def get_decrypted_description(self, obj):
        """ Déchiffre la description uniquement si l'utilisateur a le droit d'accès """
        user = self.context['request'].user
        return obj.decrypt_data(user)

    def create(self, validated_data):
        """ Crée un dossier médical et chiffre les données """
        medecins = validated_data.pop("medecins_id", [])
        if not medecins:
            raise serializers.ValidationError("Au moins un médecin est requis pour créer un dossier médical.")

        patient = validated_data.pop("patient", None)
        if not patient:
            raise serializers.ValidationError("Le patient est requis pour créer un dossier médical.")

        # Récupération de la description brute
        description = self.context['request'].data.get('description', '')

        # Création du dossier sans description
        dossier = Dossier.objects.create(patient=patient, **validated_data)
        dossier.medecins.set(medecins)  

        # Chiffrement et stockage de la description
        dossier.encrypt_data(description)

        return dossier



# 📅 Serializer pour les consultations
class ConsultationSerializer(serializers.ModelSerializer):
    # Retourne l'objet complet pour la lecture
    medecin = MedSerializer(read_only=True)
    patient = PatSerializer(read_only=True)

    # Permet d'envoyer uniquement l'ID lors de la création
    medecin_id = serializers.IntegerField(write_only=True)  # Accepte un entier

    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Pat.objects.all(), write_only=True, source="patient"
    )

    class Meta:
        model = Consultation
        fields = [
            "id", "date_deb", "date_fin", "medecin", "medecin_id", "patient", "patient_id",
            "observation", "condition_medicale"
        ]

    def validate_medecin_id(self, value):
        """ Vérifie que l'ID du User correspond bien à un médecin """
        try:
            return Med.objects.get(user_id=value).id  # Convertit user_id en medecin_id
        except Med.DoesNotExist:
            raise serializers.ValidationError("Aucun médecin trouvé pour cet utilisateur.")

    def create(self, validated_data):
        # Corriger les dates si elles sont naïves
        if "date_deb" in validated_data and is_naive(validated_data["date_deb"]):
            validated_data["date_deb"] = make_aware(validated_data["date_deb"])

        if "date_fin" in validated_data and is_naive(validated_data["date_fin"]):
            validated_data["date_fin"] = make_aware(validated_data["date_fin"])

        return Consultation.objects.create(**validated_data)


