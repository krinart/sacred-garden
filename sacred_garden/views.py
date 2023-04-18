from itertools import chain

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q

from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from rest_framework import generics, mixins, viewsets
from rest_framework import permissions as drf_permissions
from rest_framework import serializers as drf_serializers
from rest_framework import views as drf_views
from rest_framework.decorators import action
from rest_framework.response import Response

from sacred_garden import emails
from sacred_garden import models
from sacred_garden import sample_data
from sacred_garden import serializers


INVITES_ENABLED = True


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):

    queryset = models.User.objects.all()
    serializer_class = serializers.UserUpdateSerializer

    @action(detail=False, methods=['GET'])
    def me(self, request):
        user = request.user
        partner_user = user.partner_user

        emotional_needs = models.get_emotional_needs_with_prefetched_current_values(user)
        eneeds_serializer = serializers.EmotionalNeedSerializer(
            instance=emotional_needs, many=True)

        serializer = serializers.MeSerializer(request.user)
        data = serializer.data
        data['emotional_needs'] = eneeds_serializer.data

        if partner_user:
            partner_emotional_needs = models.get_emotional_needs_with_prefetched_current_values(partner_user, by_partner=user)
            partner_eneeds_serializer = serializers.EmotionalNeedSerializer(
                instance=partner_emotional_needs, many=True)
            data['partner_user']['emotional_needs'] = partner_eneeds_serializer.data

        return Response(data)

    @action(detail=False, methods=['POST'])
    def connect_partner(self, request):
        serializer = serializers.ConnectPartnerSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({})

    @action(detail=False, methods=['POST'])
    def disconnect_partner(self, request):
        user = request.user
        partner_user = request.user.partner_user

        if not partner_user :
            raise drf_serializers.ValidationError('User has no partner', code='no_partner')

        models.disconnect_partner(user)

        return Response({})

    @action(detail=True, methods=['POST'])
    def change_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        serializer.is_valid()

        user.set_password(serializer.data['password'])
        user.save()

        return Response()


class EmotionalNeedPermission(drf_permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, user):
        return user == request.user


class SampleDataViewSet(viewsets.GenericViewSet):

    queryset = models.User.objects.all()
    permission_classes = [drf_permissions.IsAuthenticated, EmotionalNeedPermission]

    @action(detail=True, methods=['POST'])
    def populate_sample_data(self, *args, **kwargs):

        # Do not populate sample data if user has a partner
        if self.request.user.partner_user:
            self.permission_denied(self.request)

        sample_data.populate_sample_user_data(self.request.user)

        return Response()

    @action(detail=True, methods=['POST'])
    def clean_sample_data(self, *args, **kwargs):
        sample_data.clean_sample_user_data(self.request.user)
        return Response()


class CheckUserView(drf_views.APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = models.User.objects.get(email=serializer.data['email'])
        except models.User.DoesNotExist:
            if INVITES_ENABLED:
                user_status = 'NON_EXISTING'
            else:
                user_status = 'INVITED'
        else:
            if not user.is_invited:
                user_status = 'NOT_INVITED'
            elif not user.is_active:
                user_status = 'INVITED'
            else:
                user_status = 'ACTIVE'

        return Response({
            'user_status': user_status
        })


class RequestResetPassword(drf_views.APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        user = generics.get_object_or_404(models.User, email=data['email'])
        emails.send_reset_password(user)

        return Response()


class ResetPassword(drf_views.APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        user = generics.get_object_or_404(models.User, id=data['user_id'])
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            self.permission_denied(request)

        user.set_password(data['password'])
        user.save()

        payload = jwt_payload_handler(user)

        return Response({
            'token': jwt_encode_handler(payload),
        })


class JoinWaitListView(drf_views.APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        email = models.User.objects.normalize_email(data['email'])

        try:
            models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            pass
        else:
            self.permission_denied(request)

        models.User.objects.create(email=email, is_invited=False, is_active=False)

        return Response({})


class RegistrationView(drf_views.APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        if INVITES_ENABLED:
            user = generics.get_object_or_404(models.User, email=serializer.data['email'])

            # User was not invited yet
            if not user.is_invited:
                self.permission_denied(request)

            # User is already active
            if user.is_active:
                self.permission_denied(request)

            user.first_name = data['first_name']
            user.set_password(data['password'])
            user.is_active = True
            user.save()

        else:
            user = models.User.objects.create_user(
                data['email'], data['password'], first_name=data['first_name'])

        models.populate_new_profile(user)

        payload = jwt_payload_handler(user)

        return Response({
            'token': jwt_encode_handler(payload),
        })


class EmotionalNeedPermission(drf_permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, eneed):

        if eneed.user.is_sample:
            return True

        if eneed.user == request.user:
            return True

        if eneed.user.partner_user == request.user:
            return True

        return False


class EmotionalNeedViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    queryset = models.EmotionalNeed.objects.all()
    serializer_class = serializers.EmotionalNeedSerializer

    permission_classes = [drf_permissions.IsAuthenticated, EmotionalNeedPermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateEmotionalNeedSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['GET'])
    def state_history(self, request, *args, **kwargs):
        eneed = self.get_object()

        if eneed.user == request.user:
            eneed_statuses = models.find_emotional_need_statuses(eneed, user=request.user)
        else:
            eneed_statuses = models.find_emotional_need_statuses(eneed, partner_user=request.user)

        serializer = serializers.EmotionalNeedStateSerializer(
            many=True, instance=eneed_statuses)

        return Response(serializer.data)


class EmotionalNeedStatePermission(drf_permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, ens):
        return ens.emotional_need.user == request.user


class EmotionalNeedStateViewSet(mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):

    queryset = models.EmotionalNeedState.objects.all()
    serializer_class = serializers.EmotionalNeedStateSerializer

    permission_classes = [drf_permissions.IsAuthenticated, EmotionalNeedStatePermission]


class EmotionalLetterPermission(drf_permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, letter):
        if request.method == 'DELETE' or request.method == 'PUT':
            return letter.sender == request.user
        return letter.sender == request.user or letter.recipient == request.user


class EmotionalLetterViewSet(viewsets.ModelViewSet):

    queryset = models.EmotionalLetter.objects.all()
    serializer_class = serializers.EmotionalLetterSerializer

    permission_classes = [drf_permissions.IsAuthenticated, EmotionalLetterPermission]

    def get_queryset(self):
        return self.queryset.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).order_by(
            '-created_at'
        )

    @action(detail=True, methods=['PUT'])
    def mark_as_read(self, request, *args, **kwargs):

        letter = self.get_object()
        letter.is_read = True
        letter.save()

        return Response()

    @action(detail=True, methods=['PUT'])
    def mark_as_acknowledged(self, request, *args, **kwargs):
        letter = self.get_object()
        letter.is_acknowledged = True
        letter.save()

        return Response()


class AppreciationsAPIView(drf_views.APIView):

    def get(self, request):
        letters = models.EmotionalLetter.objects.filter(recipient=self.request.user)

        eneed_states = models.EmotionalNeedState.objects.filter(
            partner_user=self.request.user,
        ).exclude(
            Q(appreciation_text__isnull=True)|Q(appreciation_text='')
        )

        instances = sorted(
            chain(letters, eneed_states),
            key=lambda x: x.created_at,
            reverse=True,
        )

        serializer = serializers.AppreciationSerializer(
            instance=instances , many=True)
        return Response(serializer.data)
