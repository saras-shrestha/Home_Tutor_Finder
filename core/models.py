from django.db import models

# Create your models here.
class Grade(models.Model):
    name = models.CharField(max_length=50)     
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
# Location
class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="districts"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "region"],
                name="unique_district_per_region",
            )
        ]

    def __str__(self):
        return self.name


class City(models.Model):
    LOCAL_LEVEL_TYPES = [
        ("METROPOLITAN", "Metropolitan City"),
        ("SUB_METROPOLITAN", "Sub-Metropolitan City"),
        ("MUNICIPALITY", "Municipality"),
        ("RURAL_MUNICIPALITY", "Rural Municipality"),
    ]

    name = models.CharField(max_length=100)
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="cities",
    )
    local_level_type = models.CharField(
        max_length=30,
        choices=LOCAL_LEVEL_TYPES,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "district"],
                name="unique_city_per_district",
            )
        ]

    def __str__(self):
        return self.name


class Location(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    district = models.ForeignKey(District, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    address = models.CharField(max_length=255)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.address}, {self.city}"
# class Region(models.Model):
#     name = models.CharField(max_length=100)

# class District(models.Model):
#     name = models.CharField(max_length=100)
#     region = models.ForeignKey(Region, on_delete=models.PROTECT)

# class City(models.Model):
#     name = models.CharField(max_length=100)
#     district = models.ForeignKey(District, on_delete=models.PROTECT)

# class Location(models.Model):
#     region = models.ForeignKey(Region, on_delete=models.PROTECT)
#     district = models.ForeignKey(District, on_delete=models.PROTECT)
#     city = models.ForeignKey(City, on_delete=models.PROTECT)

#     address = models.CharField(max_length=255)

#     latitude = models.DecimalField(
#         max_digits=9,
#         decimal_places=6,
#         null=True,
#         blank=True
#     )

#     longitude = models.DecimalField(
#         max_digits=9,
#         decimal_places=6,
#         null=True,
#         blank=True
#     )

#     def __str__(self):
#         return f"{self.address}, {self.city}"