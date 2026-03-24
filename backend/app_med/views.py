from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from app.models import Med, Pat, Dossier, Consultation
import traceback
from app.serializers import MedSerializer, PatSerializer, DossierSerializer, ConsultationSerializer

# 📌 Dashboard du médecin
@api_view(["GET"])
def med_dashboard(request, id):
    """Retourne un message indiquant que l'utilisateur est sur son tableau de bord (médecin)."""
    try:
        data = {
            "total_patients": Pat.objects.count(),
            "total_dossiers": Dossier.objects.filter(medecins__id=id).count(),
            "total_consultations": Consultation.objects.filter(medecin_id=id).count(),
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 📌 Gestion des patients
@api_view(["GET"])
def med_get_patients(request):
    """
    Récupère la liste de tous les patients.
    """
    try:
        patients = Pat.objects.all()
        serializer = PatSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def med_get_patient(request, id):
    """Récupère les informations d'un patient spécifique."""
    try:
        patient = get_object_or_404(Pat, id=id)
        serializer = PatSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT"])
def med_update_patient(request, id):
    """Met à jour les informations d'un patient spécifique."""
    try:
        patient = get_object_or_404(Pat, id=id)
        serializer = PatSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 📌 Gestion des dossiers médicaux
@api_view(["GET"])
def med_get_dossiers(request):
    """
    Récupère la liste de tous les dossiers médicaux.
    """
    try:
        id = request.query_params.get("id")
        if id:
            dossiers = Dossier.objects.filter(medecins__id=id)
        else:
            dossiers = Dossier.objects.all()
        serializer = DossierSerializer(dossiers, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def med_get_dossier(request, id):
    """Récupère un dossier médical spécifique."""
    try:
        dossier = get_object_or_404(Dossier, id=id)
        serializer = DossierSerializer(dossier, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT"])
def med_update_dossier(request, id):
    """Met à jour un dossier médical spécifique."""
    try:
        dossier = get_object_or_404(Dossier, id=id)
        serializer = DossierSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE"])
def med_delete_dossier(request, id):
    """Supprime un dossier médical spécifique."""
    try:
        dossier = get_object_or_404(Dossier, id=id)
        dossier.delete()
        return Response({"message": "Dossier supprimé avec succès"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def med_add_dossier(request):
    """Ajoute un nouveau dossier médical."""
    try:
        serializer = DossierSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 📌 Gestion des consultations
@api_view(["GET"])
def med_get_consultations(request):
    """
    Récupère la liste de toutes les consultations.
    """
    try:
        id = request.query_params.get("id")
        if id:
            consultations = Consultation.objects.filter(medecin=Med.objects.get(user__id=id))
        else:
            consultations = Consultation.objects.all()
        serializer = ConsultationSerializer(consultations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET"])
def med_get_consultation(request, id):
    """Récupère une consultation spécifique."""
    try:
        consultation = get_object_or_404(Consultation, id=id)
        serializer = ConsultationSerializer(consultation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT"])
def med_update_consultation(request, id):
    """Met à jour une consultation spécifique."""
    try:
        consultation = get_object_or_404(Consultation, id=id)
        serializer = ConsultationSerializer(consultation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE"])
def med_delete_consultation(request, id):
    """Supprime une consultation spécifique."""
    try:
        consultation = get_object_or_404(Consultation, id=id)
        consultation.delete()
        return Response({"message": "Consultation supprimée avec succès"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def med_add_consultation(request):
    """Ajoute une nouvelle consultation."""
    try:
        serializer = ConsultationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("❌ Erreur serveur:", str(e))  # Debug
        print(traceback.format_exc())  # ✅ Afficher toute la stack trace
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def med_from_user(request, id):
    """ Récupère l'ID du médecin à partir de l'ID du User """
    try:
        medecin = Med.objects.get(user_id=id)
        return Response({"medecin_id": medecin.id}, status=status.HTTP_200_OK)
    except Med.DoesNotExist:
        return Response({"error": "Aucun médecin trouvé pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)