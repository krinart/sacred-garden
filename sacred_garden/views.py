from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import serializers

from sacred_garden import models


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'first_name']


class HomeSerializer(serializers.ModelSerializer):

    partner_user = PartnerSerializer()

    class Meta:
        model = models.User
        fields = ['id', 'first_name',
                  'partner_user', 'partner_name', 'partner_invite_code']


@api_view()
def home(request):
    serializer = HomeSerializer(request.user)
    return Response(serializer.data)
