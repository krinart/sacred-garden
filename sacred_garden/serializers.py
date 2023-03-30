from rest_framework import serializers as drf_serializers

from sacred_garden import models


class PartnerSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'first_name']


class HomeSerializer(drf_serializers.ModelSerializer):

    partner_user = PartnerSerializer()

    class Meta:
        model = models.User
        fields = ['id', 'first_name',
                  'partner_user', 'partner_name', 'partner_invite_code']


class UserUpdateSerializer(drf_serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ['first_name', 'partner_name']
