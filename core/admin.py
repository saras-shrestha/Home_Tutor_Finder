from django.contrib import admin
from .models import Location, Region, District, City, Grade

# Register your models here.

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'get_region')
    list_filter = ('district',)
    search_fields = ('name', 'district__name')
    ordering = ('name',)

    @admin.display(description='Region')
    def get_region(self, obj):
        return obj.district.region


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'address',
        'city',
        'get_district',
        'get_region',
        'latitude',
        'longitude',
    )

    list_filter = (
        'city',
        'city__district',
        'city__district__region',
    )

    search_fields = (
        'address',
        'city__name',
        'city__district__name',
        'city__district__region__name',
    )

    @admin.display(description='District')
    def get_district(self, obj):
        return obj.city.district

    @admin.display(description='Region')
    def get_region(self, obj):
        return obj.city.district.region