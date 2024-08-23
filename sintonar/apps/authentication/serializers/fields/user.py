from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import PrimaryKeyRelatedField, ValidationError

from sintonar.apps.authentication.models import Interest

User = get_user_model()


class UserField(PrimaryKeyRelatedField):
    def get_queryset(self):
        return User.objects.filter(is_confirmed=True)

    def to_internal_value(self, data):
        try:
            return User.objects.get(
                id=data,
                is_confirmed=True,
            )
        except User.DoesNotExist:
            raise ValidationError(
                detail={"detail": _(f'Invalid pk "{data}" - object does not exist.')}
            )


class InterestField(PrimaryKeyRelatedField):
    def get_queryset(self):
        return Interest.objects.all()

    def to_internal_value(self, data):
        try:
            return Interest.objects.get(
                id=data,
            )
        except Interest.DoesNotExist:
            raise ValidationError(
                detail={"detail": _(f'Invalid pk "{data}" - object does not exist.')}
            )
