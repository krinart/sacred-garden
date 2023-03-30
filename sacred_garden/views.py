from rest_framework.response import Response
from rest_framework import mixins, viewsets
from rest_framework.decorators import action

from sacred_garden import models
from sacred_garden import serializers


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):

    queryset = models.User.objects.all()
    serializer_class = serializers.UserUpdateSerializer

    @action(detail=False, methods=['GET'])
    def me(self, request):
        serializer = serializers.HomeSerializer(request.user)
        return Response(serializer.data)
