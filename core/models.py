from django.db import models

# Create your models here.
class Grade(models.Model):
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.address}, {self.city}"