from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Account(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1000.00")
    )

    def __str__(self):
        return f"{self.owner.username}'s account"


class Transaction(models.Model):
    sender = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="sent_transactions"
    )

    receiver = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="received_transactions"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.CharField(max_length=200)

    def __str__(self):
        return (
            f"{self.sender.owner.username} -> "
            f"{self.receiver.owner.username}: "
            f"{self.amount}"
        )