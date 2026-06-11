from django.db import models
from django.contrib.auth.models import User

class Salon(models.Model):
    owner = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)

    opening_time = models.TimeField(default="09:00")
    closing_time = models.TimeField(default="20:00")

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SalonService(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name="services"
    )

    service = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE
    )

    duration_minutes = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return f"{self.service.name} - {self.salon.name}"