from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from utils.logging import get_logger, log_api_request, log_api_response, log_api_error, log_user_action, log_business_event

from utils.response import api_response
from bikes.models import Bike
from bikes.serializers import BikeSerializer
from bikes.models import MaintenanceTicket
from bikes.serializers import MaintenanceTicketSerializer

logger = get_logger("core")


class HomePageAPIView(APIView):
    """Home page view."""

    permission_classes = [AllowAny]

    def get(self, request):
        log_api_request(logger, request, "get_home_page")
        
        try:
            # Get the first 8 bikes
            bikes = Bike.objects.all()[:8]
            count = bikes.count()
            
            # Get the request from the context
            serializer = BikeSerializer(bikes, many=True, context=self.get_renderer_context())
            context = {
                "bikes": serializer.data,
            }
            response = api_response(
                success=True,
                message="Home page fetched successfully",
                data=context,
                status_code=status.HTTP_200_OK,
            )
            log_api_response(logger, request, "get_home_page", status.HTTP_200_OK, 
                           bikes_count=count)
            return response
        except Exception as e:
            log_api_error(logger, request, "get_home_page", e)
            raise


class MaintenanceTicketListCreateView(generics.ListCreateAPIView):
    serializer_class = MaintenanceTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_owner:
            return MaintenanceTicket.objects.filter(bike__owner=user)
        return MaintenanceTicket.objects.filter(reported_by=user)

    def perform_create(self, serializer):
        bike = get_object_or_404(Bike, pk=serializer.validated_data["bike_id"])
        serializer.save(reported_by=self.request.user)


class MaintenanceTicketDetailView(generics.RetrieveUpdateAPIView):
    queryset = MaintenanceTicket.objects.all()
    serializer_class = MaintenanceTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj
