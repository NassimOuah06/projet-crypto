from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from app.models import Dossier, Consultation,Med, Pat
from app.serializers import DossierSerializer, ConsultationSerializer


# 📌 Dashboard du patient
@api_view(["GET"])
def pat_dashboard(request, id):
    try:
        pat = get_object_or_404(Pat, user_id=id)
        data = {
            "total_medecins": Med.objects.all().count(),
            "total_dossiers": Dossier.objects.filter(patient = pat).count(),
            "total_consultations": Consultation.objects.filter(patient=pat).count(),
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def pat_get_dossier(request):  # 🔹 Correction du nom (pluriel)
    """Récupère tous les dossiers médicaux d'un patient."""
    try:
        id = request.query_params.get("id")
        if not id:
            return Response({"error": "ID du patient requis."}, status=status.HTTP_400_BAD_REQUEST)
        pat = get_object_or_404(Pat, user_id=id)
        dossier = Dossier.objects.filter(patient=pat)  # 🔹 Récupérer toutes les consultations du patient
        serializer = DossierSerializer(dossier, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 📌 Gestion des consultations du patient
@api_view(["GET"])
def pat_get_consultations(request):
    """Récupère la liste de toutes les consultations du patient."""
    try:
        id = request.query_params.get("id")
        if not id:
            return Response({"error": "ID du patient requis."}, status=status.HTTP_400_BAD_REQUEST)
        pat = get_object_or_404(Pat, user_id=id)
        consultations = Consultation.objects.filter(patient=pat)  # 🔹 Récupérer toutes les consultations du patient
        serializer = ConsultationSerializer(consultations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def pat_get_consultation(request, id):
    """Récupère une consultation spécifique du patient."""
    try:
        consultation = get_object_or_404(Consultation, id=id)
        serializer = ConsultationSerializer(consultation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)