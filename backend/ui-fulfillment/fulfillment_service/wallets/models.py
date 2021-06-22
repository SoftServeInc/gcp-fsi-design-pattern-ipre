import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from fulfillment_service.utils.fields import BigDecimalField


class NoWalletsForUserError(Exception):
    pass


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=50)
    card_number = models.CharField(
        max_length=19,
        unique=True,
        validators=[RegexValidator(regex='^[0-9]{12,19}$', message='Invalid card number')],
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @staticmethod
    def fits_sum(user, invested_sum):
        return [w for w in Wallet.objects.filter(user=user) if w.balance >= invested_sum]

    @staticmethod
    def max_balance(user):
        wallets = Wallet.objects.filter(user=user)
        if len(wallets) == 0:
            raise NoWalletsForUserError()
        return max(w.balance for w in wallets)

    @property
    def balance(self):
        """
        Returns current balance of the wallet (sum of all transactions)
        """
        return sum(t.sum for t in Transaction.objects.filter(wallet=self))

    def __str__(self):
        return '{} {}: {}'.format(self.bank_name, self.card_number, self.balance)


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    sum = BigDecimalField()
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.created_at, self.name, self.sum)

    class Meta:
        ordering = ('created_at',)
