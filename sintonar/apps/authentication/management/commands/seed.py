from datetime import date
from math import sqrt

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from sintonar.apps.authentication.models import Interest, User, UserPhoto


def is_prime(n):
    if n == 1:
        return False
    elif n == 2:
        return True
    else:
        for x in range(2, int(sqrt(n)) + 1):
            if n % x == 0:
                return False
        return True


class Command(BaseCommand):
    help = "Populate database with initial data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        users = list()
        fake = Faker(["pt_BR"])

        interests = [
            Interest(name="Cinema"),
            Interest(name="Esportes"),
            Interest(name="Gastronomia"),
            Interest(name="Literatura"),
            Interest(name="Música"),
            Interest(name="Tecnologia"),
            Interest(name="Viagens"),
        ]

        instances_interests = Interest.objects.bulk_create(interests)

        for i in range(1, 10):
            first_name = fake.first_name_male()
            gender = User.MAN

            if i % 2 == 0:
                first_name = fake.first_name_female()
                gender = User.WOMAN

            elif is_prime(i):
                first_name = fake.first_name()
                gender = User.NON_BINARY

            users.append(
                User(
                    email=f"test{i}@mail.com",
                    birthday=date(1990, 1, 1),
                    gender=gender,
                    first_name=first_name,
                    last_name=fake.last_name(),
                    description=fake.text(100),
                    is_confirmed=True,
                    has_uploaded_photo=True,
                    has_description=True,
                )
            )

        User.objects.bulk_create(users)

        mens_photo = 0
        womens_photos = 0
        neutrals_photos = 0

        for i, user in enumerate(User.objects.all(), start=1):
            user.set_password("123456")
            user.save()

            interest = list(instances_interests)[i % len(instances_interests)]

            user.interests.add(interest)
            user.save()

            if user.gender == User.MAN:
                mens_photo += 1
                for c in range(0, 3):
                    user_photo = UserPhoto(
                        user=user, is_favorite=True if c == 0 else False
                    )

                    file = open(
                        "sintonar/apps/authentication/management/photos/man/photo-{}.jpg".format(
                            ((mens_photo + c) % 7) + 1
                        ),
                        "rb",
                    )
                    image = File(file)

                    user_photo.photos.save(
                        "photo-{}.jpg".format(((i + c) % 7) + 1), image
                    )
                    user_photo.save()

                    file.close()

            elif user.gender == User.WOMAN:
                womens_photos += 1
                for c in range(0, 3):
                    user_photo = UserPhoto(
                        user=user, is_favorite=True if c == 0 else False
                    )

                    file = open(
                        "sintonar/apps/authentication/management/photos/woman/photo-{}.jpg".format(
                            ((womens_photos + c) % 7) + 1
                        ),
                        "rb",
                    )
                    image = File(file)

                    user_photo.photos.save(
                        "photo-{}.jpg".format(((i + c) % 7) + 1), image
                    )
                    user_photo.save()

                    file.close()

            else:
                neutrals_photos += 1
                for c in range(0, 3):
                    user_photo = UserPhoto(
                        user=user, is_favorite=True if c == 0 else False
                    )

                    choice = "man" if neutrals_photos % 2 == 0 else "woman"
                    file = open(
                        "sintonar/apps/authentication/management/photos/{}/photo-{}.jpg".format(
                            choice, ((neutrals_photos + c) % 7) + 1
                        ),
                        "rb",
                    )

                    image = File(file)

                    user_photo.photos.save(
                        "photo-{}.jpg".format(((c + i) % 7) + 1), image
                    )
                    user_photo.save()

                    file.close()

        print("Done!")
