from rest_framework import mixins, viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.response import Response
from rest_framework.decorators import action

from sacred_garden import models
from sacred_garden import serializers


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):

    queryset = models.User.objects.all()
    serializer_class = serializers.UserUpdateSerializer

    @action(detail=False, methods=['GET'])
    def me(self, request):
        emotional_needs = models.get_emotional_needs_with_prefetched_current_values(user=request.user)
        eneeds_serializer = serializers.EmotionalNeedSerializer(
            instance=emotional_needs, many=True)

        partner_emotional_needs = models.get_emotional_needs_with_prefetched_current_values(user=request.user)
        partner_eneeds_serializer = serializers.EmotionalNeedSerializer(
            instance=partner_emotional_needs, many=True)

        serializer = serializers.MeSerializer(request.user)
        data = serializer.data
        data['emotional_needs'] = eneeds_serializer.data
        data['partner_emotional_needs'] = partner_eneeds_serializer .data

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


class EmotionalNeedViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = models.EmotionalNeed.objects.all()
    serializer_class = serializers.CreateEmotionalNeedSerializer


class EmotionalNeedValueViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = models.EmotionalNeedValue.objects.all()
    serializer_class = serializers.CreateEmotionalNeedValueSerializer
