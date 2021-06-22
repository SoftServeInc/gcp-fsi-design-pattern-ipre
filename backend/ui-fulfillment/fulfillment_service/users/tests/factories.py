from django.contrib.auth import get_user_model
from factory import Faker, Sequence
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: 'username{}'.format(n))
    email = Sequence(lambda n: 'email{}@example.com'.format(n))
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = Faker(
        'password',
        length=42,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )

    class Meta:
        model = get_user_model()
