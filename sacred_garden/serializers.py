from rest_framework import exceptions
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

    is_initial_state = drf_serializers.SerializerMethodField()

    class Meta:
        model = models.EmotionalNeedState
        list_serializer_class = EmotionalNeedStateListSerializer
        fields = ['emotional_need_id', 'status',
                  'value_abs', 'value_rel', 'id', 'text', 'appreciation_text',
                  'created_at', 'is_initial_state']
        read_only_fields = ['id']
        extra_kwargs = {
            'text': {'required': True},
            'appreciation_text': {'allow_blank': True},
        }

    def get_is_initial_state(self, instance):
        return instance.value_abs is None and instance.value_rel is None

    def validate(self, attrs):
        # for create
        if not self.instance:
            user = self.context['request'].user
            eneed = attrs['emotional_need_id']

            if not eneed.user == user:
                self.context['view'].permission_denied(self.context['request'])

        # for update
        else:
            if self.instance.emotional_need.user != self.context['request'].user:
                self.context['view'].permission_denied(self.context['request'])

        return attrs

    def validate_emotional_need_id(self, value):
        # if value.state_value_type == models.EmotionalNeed.StateValueType.ABSOLUTE:
        #     self.fields['value_abs'].required = True
        # else:
        #     self.fields['value_rel'].required = True

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

    def __init__(self, instance=None, data=drf_serializers.empty, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)

        # Trick to ignore emotional_need_id for PUT requests
        request = kwargs.get('context', {}).get('request')
        if instance and request and request.method == 'PUT':
            self.fields.pop('emotional_need_id')


def get_abs_value(ens, ens_prev):
    if not ens_prev:
        return ens.value_rel

    prev_value_abs = ens_prev.value_abs or 0

    return prev_value_abs + ens.value_rel


class EmotionalNeedSerializer(drf_serializers.ModelSerializer):

    current_state = EmotionalNeedStateSerializer()

    class Meta:
        model = models.EmotionalNeed
        fields = ['id', 'name', 'current_state', 'state_value_type', 'user']
        read_only_fields = ['user']


class PartnerSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'first_name']


class MeSerializer(drf_serializers.ModelSerializer):

    partner_user = PartnerSerializer()
    unread_letters_count = drf_serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = ['id', 'first_name',
                  'partner_user', 'partner_name', 'partner_invite_code',
                  'unread_letters_count']

    def get_unread_letters_count(self, instance):
        if not instance.partner_user:
            return 0

        return models.EmotionalLetter.objects.filter(
            sender=instance.partner_user,
            recipient=instance,
            is_read=False,
        ).count()


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

    initial_status = drf_serializers.ChoiceField(
        choices=models.EmotionalNeedState.StatusChoices.choices,
        write_only=True,
        required=False)

    class Meta:
        model = models.EmotionalNeed
        fields = ['name', 'id', 'state_value_type', 'initial_status']
        read_only_fields = ['id']

    def validate(self, attrs):
        attrs['user_id'] = self.context['request'].user.id
        return attrs

    def create(self, validated_data):
        initial_status = validated_data.pop('initial_status', None)
        instance = super().create(validated_data)

        if initial_status is not None:
            models.create_emotional_need_state(
                self.context['request'].user,
                instance,
                initial_status, None, None, "", "")
        return instance


class EmotionalLetterSerializer(drf_serializers.ModelSerializer):

    is_sent = drf_serializers.SerializerMethodField()
    is_received = drf_serializers.SerializerMethodField()

    class Meta:
        model = models.EmotionalLetter
        fields = ['text', 'appreciation_text', 'advice_text', 'sender',
                  'recipient', 'is_read', 'created_at', 'id', 'is_acknowledged',
                  'is_sent', 'is_received']
        read_only_fields = ['sender', 'recipient', 'is_read', 'is_acknowledged', 'created_at', 'id']
        extra_kwargs = {
            'advice_text': {'required': False, 'allow_blank': True},
            'appreciation_text': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        if not self.context['request'].user.partner_user_id:
            raise exceptions.ValidationError('Partner is required')

        attrs['sender'] = self.context['request'].user
        attrs['recipient'] = self.context['request'].user.partner_user
        return attrs

    def get_is_sent(self, instance):
        return instance.sender == self.context['request'].user

    def get_is_received(self, instance):
        return not self.get_is_sent(instance)


class AppreciationSerializer(drf_serializers.Serializer):

    id = drf_serializers.IntegerField()
    source_entity = drf_serializers.SerializerMethodField()
    appreciation_text = drf_serializers.CharField()
    created_at = drf_serializers.DateTimeField()

    emotional_need_state = drf_serializers.SerializerMethodField()

    def get_source_entity(self, instance):
        if isinstance(instance, models.EmotionalLetter):
            return 'emotional_letter'
        elif isinstance(instance, models.EmotionalNeedState):
            return 'emotional_need_state'

        raise ValueError(f'Unsupported instance type: {type(instance)}')

    def get_emotional_need_state(self, instance):
        if isinstance(instance, models.EmotionalNeedState):
            return {
                'emotional_need_id': instance.emotional_need_id
            }


class CheckUserSerializer(drf_serializers.Serializer):
    email = drf_serializers.EmailField(required=True)


class RegistrationSerializer(drf_serializers.Serializer):
    email = drf_serializers.EmailField(required=True)
    first_name = drf_serializers.CharField(required=True)
    password = drf_serializers.CharField(required=True)
    invite_code = drf_serializers.CharField(required=True)
