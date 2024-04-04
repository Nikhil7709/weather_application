from django.db import models
from django.dispatch import receiver


class Region(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "1. Regions"

    def __str__(self):
        return self.name

class Parameter(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "2. Parameter"

    def __str__(self):
        return self.name
    
class Year(models.Model):
    year = models.IntegerField(unique=True)

    class Meta:
        ordering = ['-year'] 
        verbose_name_plural = "3. Years"

    def __str__(self):
        return str(self.year)
    
class Month(models.Model):
    name = models.CharField(max_length=50, unique=True)
    column = models.IntegerField(default=1)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "4. Month"

    def __str__(self):
        return self.name

class Season(models.Model):
    name = models.CharField(max_length=50, unique=True)
    column = models.IntegerField(default=1)
    class Meta:
        verbose_name_plural = "5. Seasons"

    def __str__(self):
        return f"{self.name}-{self.column}"

class Annual(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    column = models.IntegerField(default=1)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "6. Annual"

    def __str__(self):
        return self.name

class SeasonalData(models.Model):
    value = models.FloatField()

    # F.k's
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="year_season")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="region_season")
    params = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name="params_season")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="season_season")

    class Meta:
        verbose_name_plural = "7. Seasons Data"

    def __str__(self):
        return str(self.season.name)

class MonthlyData(models.Model):
    value = models.FloatField()

    # F.K's
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="year_month")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="region_month")
    params = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name="params_month")
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="month_month")

    class Meta:
        verbose_name_plural = "8. Monthly Data "

    def __str__(self):
        return str(self.month.name)


class AnnualData(models.Model):
    value = models.FloatField()
    column = models.IntegerField(default=1)

    # F.k's
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="year_annual")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="region_annual")
    params = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name="params_annual")

    class Meta:
        verbose_name_plural = "9. Annual Data "

    def __str__(self):
        return str(self.value)