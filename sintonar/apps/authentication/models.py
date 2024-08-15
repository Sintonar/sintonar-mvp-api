import uuid
from datetime import date

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from sintonar.storage_backends import PrivateMediaStorage


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Interest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "interests"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    MAN = "M"
    WOMAN = "W"
    NON_BINARY = "N"
    NOT_SPECIFIED = "N"

    GENDER = (
        (MAN, "Homem"),
        (WOMAN, "Mulher"),
        (NON_BINARY, "Não-binário"),
        (NOT_SPECIFIED, "Prefiro não informar"),
    )

    NAO_INFORMADO = "NI"
    ENSINO_FUNDAMENTAL_INCOMPLETO = "EFI"
    ENSINO_FUNDAMENTAL_COMPLETO = "EFC"
    ENSINO_MEDIO_INCOMPLETO = "EMI"
    ENSINO_MEDIO_COMPLETO = "EMC"
    ENSINO_TECNICO = "ET"
    ENSINO_SUPERIOR_INCOMPLETO = "ESI"
    ENSINO_SUPERIOR_COMPLETO = "ESC"
    POS_GRADUACAO = "PG"
    MESTRADO = "ME"
    DOUTORADO = "DO"
    POS_DOUTORADO = "PD"

    SCHOOL_LEVEL = (
        (NAO_INFORMADO, "Não informado"),
        (ENSINO_FUNDAMENTAL_INCOMPLETO, "Ensino Fundamental Incompleto"),
        (ENSINO_FUNDAMENTAL_COMPLETO, "Ensino Fundamental Completo"),
        (ENSINO_MEDIO_INCOMPLETO, "Ensino Médio Incompleto"),
        (ENSINO_MEDIO_COMPLETO, "Ensino Médio Completo"),
        (ENSINO_TECNICO, "Ensino Técnico"),
        (ENSINO_SUPERIOR_INCOMPLETO, "Ensino Superior Incompleto"),
        (ENSINO_SUPERIOR_COMPLETO, "Ensino Superior Completo"),
        (POS_GRADUACAO, "Pós-graduação (Lato Sensu)"),
        (MESTRADO, "Mestrado"),
        (DOUTORADO, "Doutorado"),
        (POS_DOUTORADO, "Pós-doutorado"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    birthday = models.DateField()
    description = models.TextField(blank=True)

    gender = models.CharField(max_length=1, choices=GENDER, default=NOT_SPECIFIED)
    school_level = models.CharField(
        max_length=3, choices=SCHOOL_LEVEL, default=NAO_INFORMADO
    )
    educational_institution = models.CharField(max_length=255, blank=True)
    course = models.CharField(max_length=255, blank=True)

    interests = models.ManyToManyField(
        Interest, through="UserInterest", related_name="users", blank=True
    )

    profession = models.CharField(max_length=255, blank=True)

    is_confirmed = models.BooleanField(default=False)
    has_uploaded_photo = models.BooleanField(default=False)
    has_description = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["birthday", "first_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"

    @property
    def age(self):
        return int((date.today() - self.birthday).days / 365.25)

    @property
    def full_name(self):
        return self.get_full_name()


class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_interests"
        unique_together = ("user", "interest")

    @property
    def members(self):
        return User.objects.filter(
            id__in=UserInterest.objects.filter(interest=self.interest)
            .exclude(user=self.user)
            .values_list("user", flat=True)
        ).order_by("first_name", "last_name")

    @property
    def members_count(self):
        return self.members.count()

    @property
    def matched_members_count(self):
        from sintonar.apps.match.models.match import Match

        matchs = Match.objects.filter(
            user_from=self.request.user, user_to__in=self.members, match=True
        )

        return matchs.count()

    @property
    def viewed_members_count(self):
        from sintonar.apps.match.models.match import Match

        matchs = Match.objects.filter(
            user_from=self.request.user, user_to__in=self.members
        )

        return matchs.count()

    @property
    def not_viewed_members_count(self):
        return self.members_count - self.viewed_members_count


def model_directory_path(instance, filename):
    extension = filename.split(".")[-1]
    return "{0}.{1}".format(instance.id, extension)


class UserPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photos = models.ImageField(
        upload_to=model_directory_path, storage=PrivateMediaStorage()
    )
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_photos"


class UserConfirm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    identification_code = models.UUIDField(
        editable=False, unique=True, default=uuid.uuid4
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_confirm"
