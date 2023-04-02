from rest_framework import serializers as drf_serializers

from sacred_garden import models


class EmotionalNeedValueSerializer(drf_serializers.ModelSerializer):

    class Meta:
        model = models.EmotionalNeedValue
        fields = ['value', 'trend', 'created_at', 'text', 'appreciation_text']


class EmotionalNeedSerializer(drf_serializers.ModelSerializer):

    current_value = EmotionalNeedValueSerializer()

    class Meta:
        model = models.EmotionalNeed
        fields = ['id', 'name', 'current_value']


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


class CreateEmotionalNeedSerializer(drf_serializers.ModelSerializer):

    class Meta:
        model = models.EmotionalNeed
        fields = ['name', 'id']
        read_only_fields = ['id']

    def validate(self, attrs):
        attrs['user_id'] = self.context['request'].user.id
        return attrs


class CreateEmotionalNeedValueSerializer(drf_serializers.ModelSerializer):
    emotional_need_id = drf_serializers.PrimaryKeyRelatedField(
        queryset=models.EmotionalNeed.objects.all())

    class Meta:
        model = models.EmotionalNeedValue
        fields = ['emotional_need_id', 'value', 'trend', 'id', 'text', 'appreciation_text']
        read_only_fields = ['id']
        extra_kwargs = {
            'text': {'required': True},
            'appreciation_text': {'required': True},
        }

    def validate(self, attrs):
        user = self.context['request'].user
        eneed = attrs['emotional_need_id']

        if not eneed.user == user:
            raise drf_serializers.ValidationError('Anauthorized access', code='unauthorized')

        return attrs

    def create(self, validated_data):
        return models.create_emotional_need_value(
            self.context['request'].user,
            validated_data['emotional_need_id'],
            validated_data['value'],
            validated_data['trend'],
            validated_data['text'],
            validated_data['appreciation_text'],
        )
