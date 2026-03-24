from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from app.models import Med, Pat, Dossier, Consultation
from app.serializers import MedSerializer, PatSerializer, DossierSerializer, ConsultationSerializer

User = get_user_model()

# 🏥 Dashboard Admin
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    data = {
        "total_medecins": Med.objects.count(),
        "total_patients": Pat.objects.count(),
        "total_dossiers": Dossier.objects.count(),
        "total_consultations": Consultation.objects.count()
    }
    return Response(data, status=status.HTTP_200_OK)

# 👨‍⚕️ Liste des médecins
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_get_meds(request):
    doctors = Med.objects.all()
    serializer = MedSerializer(doctors, many=True)
    return Response(serializer.data)

# 👨‍⚕️ Récupérer un médecin
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_get_med(request, id):
    doctor = get_object_or_404(Med, id=id)
    serializer = MedSerializer(doctor)
    return Response(serializer.data)

# 👨‍⚕️ Ajouter un médecin
@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_add_med(request):
    data = request.data

    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=data["username"]).exists():
        return Response({"error": "Ce nom d'utilisateur est déjà pris."}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=data["email"]).exists():
        return Response({"error": "Cet email est déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        role="med"
    )
    doctor = Med.objects.create(user=user, specialite=data["specialite"])
    serializer = MedSerializer(doctor)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# 👨‍⚕️ Modifier un médecin
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def admin_update_med(request, id):
    doctor = get_object_or_404(Med, id=id)
    serializer = MedSerializer(doctor, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 👨‍⚕️ Supprimer un médecin
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_delete_med(request, id):
    doctor = get_object_or_404(Med, id=id)
    user = doctor.user
    doctor.delete()
    user.delete()
    return Response({"message": "Médecin supprimé"}, status=status.HTTP_204_NO_CONTENT)

# 🧑‍⚕️ Liste des patients
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_get_patients(request):
    patients = Pat.objects.all()
    serializer = PatSerializer(patients, many=True)
    return Response(serializer.data)

# 🧑‍⚕️ Récupérer un patient
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_get_patient(request, id):
    patient = get_object_or_404(Pat, id=id)
    serializer = PatSerializer(patient)
    return Response(serializer.data)

# 🧑‍⚕️ Ajouter un patient
@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_add_patient(request):
    data = request.data

    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=data["username"]).exists():
        return Response({"error": "Ce nom d'utilisateur est déjà pris."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data["email"]).exists():
        return Response({"error": "Cet email est déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        role="pat"
    )
    patient = Pat.objects.create(user=user, etat_traitement=data.get("etat_traitement", "non_traité"))
    serializer = PatSerializer(patient)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# 🧑‍⚕️ Modifier un patient
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def admin_update_patient(request, id):
    patient = get_object_or_404(Pat, id=id)
    serializer = PatSerializer(patient, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🧑‍⚕️ Supprimer un patient
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_delete_patient(request, id):
    patient = get_object_or_404(Pat, id=id)
    user = patient.user
    patient.delete()
    user.delete()
    return Response({"message": "Patient supprimé"}, status=status.HTTP_204_NO_CONTENT)

# 📁 Liste des dossiers médicaux
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_get_dossiers(request):
    dossiers = Dossier.objects.all()
    serializer = DossierSerializer(dossiers, many=True, context={"request": request})  # ✅ Ajout du contexte
    return Response(serializer.data)

# 📁 Récupérer un dossier médical
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_get_dossier(request, id):
    dossier = get_object_or_404(Dossier, id=id)
    serializer = DossierSerializer(dossier, context={"request": request})  # ✅ Ajout du contexte
    return Response(serializer.data)

# 📁 Ajouter un dossier médical
@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_add_dossier(request):
    serializer = DossierSerializer(data=request.data, context={"request": request})  # ✅ Ajout du contexte
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 📁 Supprimer un dossier médical
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_delete_dossier(request, id):
    dossier = get_object_or_404(Dossier, id=id)
    dossier.delete()
    return Response({"message": "Dossier supprimé"}, status=status.HTTP_204_NO_CONTENT)

# 📅 Liste des consultations
@api_view(["GET"])
# @permission_classes([IsAdminUser])
def admin_get_consultations(request):
    consultations = Consultation.objects.all()
    serializer = ConsultationSerializer(consultations, many=True)
    return Response(serializer.data)

# 📅 Récupérer une consultation
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_get_consultation(request, id):
    consultation = get_object_or_404(Consultation, id=id)
    serializer = ConsultationSerializer(consultation)
    return Response(serializer.data)
