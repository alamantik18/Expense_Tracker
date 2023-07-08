from django.db import models
from django.contrib.auth.models import User


class Spend(models.Model):
    CATEGORY_CHOICES = (
        ('', '--------'),
        ('groceries', 'продукты'),
        ('transportation', 'транспорт'),
        ('entertainment', 'развлечения'),
        ('housing', 'дом'),
        ('medical', 'медицина'),
    )

    description = models.TextField(blank=True, null=True)
    amount_spent = models.FloatField()
    date = models.DateField()
    date_of_creation = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_spends')
    category = models.CharField(max_length=70, choices=CATEGORY_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.date_of_creation.strftime("%d-%m-%Y, %H:%M:%S")


class Tag(models.Model):
    name = models.CharField(max_length=70)
    spend = models.ForeignKey(Spend, on_delete=models.CASCADE, related_name='tags')

    def __str__(self):
        return self.name