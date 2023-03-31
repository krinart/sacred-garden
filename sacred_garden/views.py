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
        serializer = serializers.MeSerializer(request.user)
        return Response(serializer.data)

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
