from rest_framework import serializers as drf_serializers

from sacred_garden import models


class PartnerSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'first_name']


class MeSerializer(drf_serializers.ModelSerializer):

    partner_user = PartnerSerializer()

    class Meta:
        model = models.User
        fields = ['id', 'first_name',
                  'partner_user', 'partner_name', 'partner_invite_code']


class UserUpdateSerializer(drf_serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ['first_name', 'partner_name']


class ConnectPartnerSerializer(drf_serializers.Serializer):
    invite_code = drf_serializers.CharField()

    class Meta:
        model = models.User
        fields = ['invite_code']

    def validate(self, attrs):
        try:
            partner_user = models.get_user_by_partner_invite_code(attrs['invite_code'])
        except models.User.DoesNotExist:
            raise drf_serializers.ValidationError('Invalid invite code', code='invalid_invite_code')

        if self.instance.id == partner_user.id:
            raise drf_serializers.ValidationError('Can not invite self', code='invite_self')

        if self.instance.partner_user:
            raise drf_serializers.ValidationError('User already has partner', code='has_partner')

        if partner_user.partner_user:
            raise drf_serializers.ValidationError('User already has partner', code='has_partner')

        attrs['partner_user'] = partner_user

        return attrs

    def update(self, instance, validated_data):
        models.connect_partners(instance, validated_data['partner_user'])
        return instance