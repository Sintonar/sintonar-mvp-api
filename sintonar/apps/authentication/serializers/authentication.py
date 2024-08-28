from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from sintonar.apps.authentication.models import (
    Interest,
    User,
    UserConfirm,
    UserInterest,
    UserPhoto,
)
from sintonar.apps.utils.image import resize_image
from sintonar.apps.utils.serializers.fields import CustomChoiceField


class JWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_confirmed:
            raise PermissionDenied(
                _("This user is not confirmed."),
                "not_confirmed",
            )

        data["has_description"] = self.user.has_description
        data["has_uploaded_photo"] = self.user.has_uploaded_photo

        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=_("Invalid email - user already exists."),
            )
        ],
    )
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    gender = CustomChoiceField(choices=User.GENDER)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "birthday",
            "first_name",
            "last_name",
            "gender",
        )

    def create(self, validated_data) -> User:
        user = User.objects.create_user(
            **validated_data,
        )

        UserConfirm.objects.create(user=user)

        return user


class UserPhotoSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="photos", read_only=True)

    class Meta:
        model = UserPhoto
        fields = (
            "id",
            "photos",
            "url",
            "is_favorite",
        )
        extra_kwargs = {"photos": {"write_only": True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If the user has photo, the photos field must be read only
        if self.instance:
            self.fields["photos"].read_only = True

    def validate_is_favorite(self, value: bool) -> bool:
        # If the user not has photo, the is_favorite must be True
        if (
            value is False
            and UserPhoto.objects.filter(user=self.context["request"].user).exists()
            is False
        ):
            value = True

        return value

    def validate(self, attrs):
        # If has photo, check if the size is less than 10MB
        if attrs.get("photos", None):
            if attrs["photos"].size > 1024 * 1024 * 10:
                raise serializers.ValidationError(
                    {"photos": _("Image size must be less than 10MB")}
                )

        return super().validate(attrs)

    def create(self, validated_data) -> UserPhoto:
        if self.context["request"].user.userphoto_set.count() >= 3:
            raise serializers.ValidationError(
                {"detail": _("You can't upload more than 3 photos.")}
            )

        photo = resize_image(validated_data["photos"])

        user_photo = UserPhoto.objects.create(
            user=self.context["request"].user,
            photos=photo,
            is_favorite=validated_data.get("is_favorite", False),
        )

        return user_photo

    def update(self, instance, validated_data) -> UserPhoto:
        if validated_data.get("is_favorite", False):
            UserPhoto.objects.filter(user=instance.user).update(is_favorite=False)

        return super().update(instance, validated_data)


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = (
            "id",
            "name",
        )


class UserSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    gender = CustomChoiceField(choices=User.GENDER)
    school_level = CustomChoiceField(choices=User.SCHOOL_LEVEL, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "birthday",
            "first_name",
            "last_name",
            "description",
            "full_name",
            "age",
            "has_description",
            "has_uploaded_photo",
            "interests",
            "gender",
            "school_level",
            "educational_institution",
            "course",
            "profession",
        )
        read_only_fields = (
            "id",
            "email",
            "photos",
            "has_description",
            "has_uploaded_photo",
            "interests",
        )

    def to_representation(self, instance) -> dict:
        data = super().to_representation(instance)
        data["photos"] = UserPhotoSerializer(
            instance.userphoto_set.all().order_by("-is_favorite"), many=True
        ).data

        return data

    @transaction.atomic
    def update(self, instance, validated_data) -> User:
        interests = validated_data.pop("interests", [])

        if "description" in validated_data and instance.has_description is False:
            instance.has_description = True

        if interests:
            instance.interests.set(interests)

        return super().update(instance, validated_data)


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "password",
            "new_password",
        )

    def update(self, instance, validated_data) -> User:
        if not instance.check_password(validated_data["password"]):
            raise serializers.ValidationError({"password": _("Incorrect password.")})

        instance.set_password(validated_data["new_password"])
        instance.save()

        return instance


class UserInterestSerializer(serializers.ModelSerializer):
    interest = InterestSerializer(read_only=True)
    members_count = serializers.IntegerField(read_only=True)
    matched_members_count = serializers.IntegerField(read_only=True)
    viewed_members_count = serializers.IntegerField(read_only=True)
    not_viewed_members_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserInterest
        fields = (
            "interest",
            "members_count",
            "matched_members_count",
            "viewed_members_count",
            "not_viewed_members_count",
        )
