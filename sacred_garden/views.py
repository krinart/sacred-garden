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
        user = request.user
        partner_user = user.partner_user

        emotional_needs = models.get_emotional_needs_with_prefetched_current_values(user=user)
        eneeds_serializer = serializers.EmotionalNeedSerializer(
            instance=emotional_needs, many=True)

        serializer = serializers.MeSerializer(request.user)
        data = serializer.data
        data['emotional_needs'] = eneeds_serializer.data

        if partner_user:
            partner_emotional_needs = models.get_emotional_needs_with_prefetched_current_values(
                user=partner_user)
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


class EmotionalNeedViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = models.EmotionalNeed.objects.all()
    serializer_class = serializers.CreateEmotionalNeedSerializer

    @action(detail=True, methods=['GET'])
    def status_history(self, request, *args, **kwargs):
        eneed = self.get_object()

        if eneed.user == request.user:
            eneed_statuses = models.find_emotional_need_statuses(eneed, user=request.user)
        else:
            eneed_statuses = models.find_emotional_need_statuses(eneed, partner_user=request.user)

        # TODO: Do not use CreateEmotionalNeedStatusSerializer
        serializer = serializers.EmotionalNeedStatusSerializer(
            many=True, instance=eneed_statuses)

        return Response(serializer.data)


class EmotionalNeedStatusViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = models.EmotionalNeedStatus.objects.all()
    serializer_class = serializers.EmotionalNeedStatusSerializer
