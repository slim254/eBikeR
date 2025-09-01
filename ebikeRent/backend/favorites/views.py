from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from utils.logging import get_logger, log_api_request, log_api_response, log_api_error, log_user_action, log_business_event

from .models import Favorite
from .serializers import FavoriteSerializer, CreateFavoriteSerializer
from bikes.models import Bike
from utils.response import api_response

logger = get_logger("favorites")


class FavoriteListView(generics.ListAPIView):
    """List user's favorites"""

    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        log_api_request(logger, request, "list_favorites")
        
        try:
            queryset = self.get_queryset()
            count = queryset.count()
            serializer = self.get_serializer(queryset, many=True)

            response = api_response(
                success=True,
                message="Favorites retrieved successfully",
                data={"count": count, "results": serializer.data},
                status_code=status.HTTP_200_OK,
            )
            log_api_response(logger, request, "list_favorites", status.HTTP_200_OK, 
                           favorites_count=count)
            return response
        except Exception as e:
            log_api_error(logger, request, "list_favorites", e)
            raise


class FavoriteCreateView(generics.CreateAPIView):
    """Add a bike to favorites"""

    serializer_class = CreateFavoriteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        log_api_request(logger, request, "add_favorite", favorite_data=request.data)
        
        try:
            serializer = self.get_serializer(
                data=request.data, context={"request": request}
            )

            if serializer.is_valid():
                try:
                    favorite = serializer.save()
                    log_user_action(logger, request, "add_favorite", resource_id=str(favorite.id),
                                  bike_id=str(favorite.bike.id))
                    
                    response_serializer = FavoriteSerializer(favorite)
                    response = api_response(
                        success=True,
                        message="Bike added to favorites successfully",
                        data=response_serializer.data,
                        status_code=status.HTTP_201_CREATED,
                    )
                    log_api_response(logger, request, "add_favorite", status.HTTP_201_CREATED, 
                                   favorite_id=str(favorite.id), bike_id=str(favorite.bike.id))
                    return response
                except IntegrityError:
                    log_user_action(logger, request, "duplicate_favorite_attempt", 
                                  bike_id=request.data.get('bike_id'))
                    return api_response(
                        success=False,
                        message="This bike is already in your favorites",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

            log_api_response(logger, request, "add_favorite", status.HTTP_400_BAD_REQUEST, 
                           validation_errors=serializer.errors)
            return api_response(
                success=False,
                message="Invalid data provided",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log_api_error(logger, request, "add_favorite", e)
            raise


class FavoriteDeleteView(APIView):
    """Remove a bike from favorites"""

    permission_classes = [IsAuthenticated]

    def delete(self, request, bike_id):
        log_api_request(logger, request, "remove_favorite", bike_id=bike_id)
        
        try:
            bike = get_object_or_404(Bike, id=bike_id)
            favorite = get_object_or_404(Favorite, user=request.user, bike=bike)
            favorite.delete()
            
            log_user_action(logger, request, "remove_favorite", resource_id=str(favorite.id),
                          bike_id=str(bike.id))

            response = api_response(
                success=True,
                message="Bike removed from favorites successfully",
                status_code=status.HTTP_200_OK,
            )
            log_api_response(logger, request, "remove_favorite", status.HTTP_200_OK, 
                           bike_id=str(bike.id))
            return response

        except Favorite.DoesNotExist:
            log_user_action(logger, request, "favorite_not_found", bike_id=bike_id)
            return api_response(
                success=False,
                message="This bike is not in your favorites",
                status_code=status.HTTP_404_NOT_FOUND,
            )


class FavoriteStatusView(APIView):
    """Check if a bike is in user's favorites"""

    permission_classes = [IsAuthenticated]

    def get(self, request, bike_id):
        try:
            bike = get_object_or_404(Bike, id=bike_id)
            is_favorited = Favorite.objects.filter(
                user=request.user, bike=bike
            ).exists()

            return api_response(
                success=True,
                message="Favorite status retrieved successfully",
                data={"is_favorite": is_favorited},
                status_code=status.HTTP_200_OK,
            )

        except Bike.DoesNotExist:
            return api_response(
                success=False,
                message="Bike not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )


class FavoriteToggleView(APIView):
    """Toggle favorite status of a bike"""

    permission_classes = [IsAuthenticated]

    def post(self, request, bike_id):
        try:
            bike = get_object_or_404(Bike, id=bike_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user, bike=bike
            )

            if created:
                return api_response(
                    success=True,
                    message="Bike added to favorites successfully",
                    data={"is_favorite": True},
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                favorite.delete()
                return api_response(
                    success=True,
                    message="Bike removed from favorites successfully",
                    data={"is_favorite": False},
                    status_code=status.HTTP_200_OK,
                )

        except Bike.DoesNotExist:
            return api_response(
                success=False,
                message="Bike not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
