from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.db.models import Q
from . import utils

class User(models.Model):
    username = models.CharField(max_length=55, unique=True)
    email = models.EmailField(blank=True, null=True)
    balance = models.IntegerField()
    phone = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.username} - {self.balance}"


class Transaction(models.Model):
    sender: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sender')
    receiver: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_receiver')
    amount = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount < 100:
            raise ValidationError(f'нельзя отправить меньше 100 тг')
        if self.sender.balance < self.amount:
            raise ValidationError(f'не достаточно средств у {self.sender.username} {self.amount - self.sender.balance} не хватает для отправки')
        if self.sender == self.receiver:
            raise ValidationError(f'Вы не можете отправить денги сами себе')
        today = timezone.datetime.today()
        transactions = Transaction.objects.filter(Q(sender=self.sender) & Q(created__year=today.year) & Q(created__month=today.month) & Q(created__day=today.day))
        sum_amount = sum(transaction.amount for transaction in transactions)
        if sum_amount + self.amount > 500000:
            raise ValidationError(f'Вы не можете отправить больше 500000 за день ')
    def save(self, *args, **kwargs):
        self.sender.balance -= self.amount
        self.sender.save()
        self.receiver.balance += self.amount
        self.receiver.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender.username} отправил {self.receiver.username} - {self.amount} тенге!"

class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_deposit')
    cash = models.DecimalField(max_digits=9, decimal_places=1, verbose_name='Сумма', validators=[utils.validate_cash])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    @property

    def get_cash(self):
        time = str(self.updated - self.created).split(':')
        minutes = int(time[1])
        hour = int(time[0])
        full_minutes = hour * 60 + minutes
        percent = float(self.cash) * 0.12
        return float(self.cash) + (percent * full_minutes)


    def save(self, *args, **kwargs):
        self.updated = timezone.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} {self.cash}'