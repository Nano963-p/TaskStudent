from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from .models import UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': {'id': user.id, 'username': user.username, 'email': user.email},
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({'id': user.id, 'username': user.username, 'email': user.email})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    profil, _ = UserProfile.objects.get_or_create(user=user)
    return Response({
        'total_xp': profil.total_xp,
        'level': profil.get_niveau(),
        'tasks_completed': profil.tasks_completed,
        'xp_current_level': profil.get_xp_niveau_actuel(),
        'xp_next_level': profil.get_xp_prochain_niveau(),
        'xp_progress_pct': profil.get_progression_pct(),
    })
