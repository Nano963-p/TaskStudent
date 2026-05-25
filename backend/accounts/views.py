from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from .models import UserProfile, UserBadge, BADGE_DEFINITIONS

ORGANISE_TARGET = 5


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    ser = RegisterSerializer(data=request.data)
    if ser.is_valid():
        user = ser.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': {'id': user.id, 'username': user.username, 'email': user.email},
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    u = request.user
    return Response({'id': u.id, 'username': u.username, 'email': u.email})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    earned_map = {b.badge_key: b.earned_at for b in UserBadge.objects.filter(user=user)}

    badges = []
    for key, data in BADGE_DEFINITIONS.items():
        badge_info = {
            'key': key,
            'name': data['name'],
            'description': data['description'],
            'icon': data['icon'],
            'color': data['color'],
            'earned': key in earned_map,
            'earned_at': earned_map.get(key),
            'progress': None,
        }
        # Progression vers le badge Organisé
        if key == 'organise':
            badge_info['progress'] = {
                'current': user_profile.tasks_completed,
                'target': ORGANISE_TARGET,
            }
        badges.append(badge_info)

    return Response({
        'total_xp': user_profile.total_xp,
        'level': user_profile.level,
        'tasks_completed': user_profile.tasks_completed,
        'xp_current_level': user_profile.xp_current_level,
        'xp_next_level': user_profile.xp_next_level,
        'xp_progress_pct': user_profile.xp_progress_pct,
        'badges': badges,
    })
