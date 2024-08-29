from django.db import transaction
from rest_framework import serializers

from sintonar.apps.authentication.models import User
from sintonar.apps.authentication.serializers.authentication import UserPhotoSerializer
from sintonar.apps.authentication.serializers.fields.user import (
    InterestField,
    UserField,
)
from sintonar.apps.match.models.match import Match
from sintonar.apps.utils.serializers.fields import CustomChoiceField


class MatchCreateSerializer(serializers.ModelSerializer):
    user_from = UserField()
    user_to = UserField()

    class Meta:
        model = Match
        fields = (
            "id",
            "user_from",
            "user_to",
            "like",
            "created_at",
            "updated_at",
        )

    @transaction.atomic
    def create(self, validated_data) -> Match:
        user_from = validated_data.pop("user_from")
        user_to = validated_data.pop("user_to")
        like = validated_data.pop("like", False)

        match = Match.objects.filter(
            user_from=user_from,
            user_to=user_to,
        ).first()

        if match:
            match.like = like
            match.save()

        else:
            match = Match.objects.create(
                user_from=user_from,
                user_to=user_to,
                like=like,
            )

        if match.like:
            match_liked = Match.objects.filter(
                user_to=user_from,
                user_from=user_to,
                like=True,
            )

            if match_liked.exists():
                match_liked.update(match=True)

                match.match = True
            else:
                match.match = False

        else:
            Match.objects.filter(
                user_to=user_from,
                user_from=user_to,
                like=True,
            ).update(match=False)

            match.match = False

        match.save()

        return match

    def to_representation(self, instance) -> dict:
        serializer = MatchDisplaySerializer(instance, context=self.context)

        return serializer.data


class UserMatchDisplaySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    age = serializers.IntegerField()
    school_level = CustomChoiceField(choices=User.SCHOOL_LEVEL)
    interests = InterestField(many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "age",
            "description",
            "interests",
            "school_level",
            "educational_institution",
            "course",
            "profession",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["photos"] = UserPhotoSerializer(
            instance.userphoto_set.all(), many=True
        ).data

        return data


class MatchDisplaySerializer(serializers.ModelSerializer):
    user = UserMatchDisplaySerializer(source="user_from")

    class Meta:
        model = Match
        fields = (
            "id",
            "user",
            "match",
        )
