from rest_framework import serializers as drf_serializers

from sacred_garden import models


class EmotionalNeedStateListSerializer(drf_serializers.ListSerializer):

    def to_representation(self, data):
        result = []
        prev_el = None

        for el in data:
            result.append(self.child.to_representation(el, prev_el, populate_value_abs=True))
            prev_el = el

        return result


class EmotionalNeedStateSerializer(drf_serializers.ModelSerializer):
    emotional_need_id = drf_serializers.PrimaryKeyRelatedField(
        queryset=models.EmotionalNeed.objects.all())

    class Meta:
        model = models.EmotionalNeedState
        list_serializer_class = EmotionalNeedStateListSerializer
        fields = ['emotional_need_id', 'status',
                  'value_abs', 'value_rel', 'id', 'text', 'appreciation_text',
                  'created_at']
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

    def validate_emotional_need_id(self, value):
        if value.state_value_type == models.EmotionalNeed.StateValueType.ABSOLUTE:
            self.fields['value_abs'].required = True
        else:
            self.fields['value_rel'].required = True

        return value

    def create(self, validated_data):
        return models.create_emotional_need_state(
            self.context['request'].user,
            validated_data['emotional_need_id'],
            validated_data['status'],
            validated_data.get('value_abs'),
            validated_data.get('value_rel'),
            validated_data['text'],
            validated_data['appreciation_text'],
        )

    def to_representation(self, instance, prev=None, populate_value_abs=False):
        if instance.value_type == models.EmotionalNeed.StateValueType.RELATIVE and populate_value_abs:
            instance.value_abs = get_abs_value(instance, prev)

        return super().to_representation(instance)


def get_abs_value(ens, ens_prev):
    prev_value = ens_prev and ens_prev.value_abs or 0
    return prev_value + ens.value_rel


class EmotionalNeedSerializer(drf_serializers.ModelSerializer):

    current_state = EmotionalNeedStateSerializer()

    class Meta:
        model = models.EmotionalNeed
        fields = ['id', 'name', 'current_state', 'state_value_type']


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
        fields = ['name', 'id', 'state_value_type']
        read_only_fields = ['id']

    def validate(self, attrs):
        attrs['user_id'] = self.context['request'].user.id
        return attrs
