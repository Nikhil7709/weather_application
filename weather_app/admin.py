from django.contrib import admin
from .models import MonthlyData, Region, Year, Month, Season, Parameter, SeasonalData, AnnualData, Annual

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['id', 'year']

@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'column']

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','column']

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(SeasonalData)
class SeasonaldataAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'region', 'params', 'season', 'value']
    list_filter = ['year', 'season', 'region__name', 'params']

@admin.register(MonthlyData)
class MonthlyDataAdmin(admin.ModelAdmin):
    list_display = ['id','year', 'region', 'params', 'month', 'value']
    list_filter = ['year', 'params', 'region__name']

@admin.register(Annual)
class AnnualAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'column']

@admin.register(AnnualData)
class AnnualDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'region', 'params',  'value']
    list_filter = ['year', 'params', 'region__name']