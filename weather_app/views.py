from django.http import HttpResponse
from django.shortcuts import render
from django.db.models.signals import post_migrate

from .models import Region, Parameter, Season, SeasonalData, Year, Month , MonthlyData, AnnualData, Annual
from .utils import scrape_data
from django.db.utils import IntegrityError
from django.dispatch import receiver


def fetch_data_view(request):
    regions = Region.objects.all()
    parameters = Parameter.objects.all()

    for region in regions:
        for parameter in parameters:
            data = scrape_data(region.name, parameter.name)
            if data is None:
                print(f"Failed to retrieve data for {region.name} - {parameter.name}")
                continue

            lines = data.strip().split('\n')
            if len(lines) < 7:
                print(f"Invalid data format for {region.name} - {parameter.name}")
                continue

            years = []
            seasonal_data_dict = {} 
            # Extract years and corresponding seasonal data
            for line in lines[6:]:
                parts = line.split()
                if len(parts) < 7:
                    print(f"Invalid data format for {region.name} - {parameter.name}")
                    continue
                year = int(parts[0])
                years.append(year)
                seasonal_data_dict[year] = parts[1:]
                print("at line 45", seasonal_data_dict)

            years = sorted(years, reverse=True)

            # Save the years to the database
            for year in years:
                try:
                    # Get or create the Year object
                    year_obj, _ = Year.objects.get_or_create(year=year)
                    # Year.objects.get_or_create(year=year)
                    
                    # Get seasonal data for the current year
                    seasonal_data = seasonal_data_dict.get(year)
                    print("at line 54", seasonal_data)

                    if seasonal_data and len(seasonal_data) >= 16:
                       
                        seasonal_data = [None if value == '---' else value for value in seasonal_data]
                        seasons = Season.objects.all()
                        print("at line 66:", seasons)
                        # store the seasonal data   
                        for season in seasons:
                            value = seasonal_data[season.column]
                            SeasonalData.objects.get_or_create(
                                year=year_obj,
                                region=region,
                                params=parameter,
                                season=season,
                                value=value
                            )
                        
                        # store the monthly data   
                        months = Month.objects.all()
                        for month, season in zip(Month.objects.all(), months):
                            value = seasonal_data[month.column]
                            print("at line 96: ", value, month)
                            MonthlyData.objects.get_or_create(
                                year=year_obj,
                                region=region,
                                params=parameter,
                                month=month,  
                                value=value
                            )

                        # store anuual data
                        annual = Annual.objects.all()
                        print("line no 93: ", annual)
                        for ann in annual:
                            values=seasonal_data[ann.column]
                            print("line no 96: ", values)

                        annual, _ = AnnualData.objects.get_or_create(
                            value=values,
                            year=year_obj,
                            region=region,
                            params=parameter,
                        )
                      
                        
                    else:
                        print(f"No seasonal data found for year {year} in {region.name} - {parameter.name}")

                except IntegrityError as e:
                    print(f"Error creating year {year}: {e}")

            print("Data saved successfully.")
    return render(request, 'home.html')


def get_yearwise_data(request, year, parameter, region):

    """
    To fetch the maximum, minimum, and average data of a specific year, specific parameter, specific region
    """
    # Fetch data from models for the specific year
    seasonal_data = SeasonalData.objects.filter(year__year=year, region__name=region, params__name=parameter)
    monthly_data = MonthlyData.objects.filter(year__year=year, region__name=region, params__name=parameter)
    season_value = [(data.value) for data in seasonal_data]
    seasons = Season.objects.all()

    # Exclude year value
    monthly_values = [(data.month.name, data.value) for data in monthly_data if data.month.name != 'January']
    annual_data = AnnualData.objects.filter(year__year=year, region__name=region, params__name=parameter)
    annual_value = [(data.value) for data in annual_data ]
    all_data = list(seasonal_data) + list(monthly_data) + list(annual_data)

    # Find the maximum value for the specific year
    max_value = max(data.value for data in all_data if data.value is not None)
    
    # Find the minimum value for the specific year
    min_value = min(data.value for data in all_data if data.value is not None)

    # Find the average value for the specific year
    total_value = sum(data.value for data in all_data if data.value is not None)
    num_values = len(all_data)
    average_value = total_value / num_values if num_values > 0 else 0

    # Fetch monthly data for the specific year, region, and parameter
    months_data = MonthlyData.objects.filter(year__year=year, region__name=region, params__name=parameter)
    month_values = [data.value for data in months_data if data.value is not None]

    # Find the maximum, minimum, and average values for monthly data
    max_month_value = max(month_values) if month_values else None
    min_month_value = min(month_values) if month_values else None
    average_month_value = sum(month_values) / len(month_values) if month_values else 0

    return render(request, 'value.html', {
        'year': year,
        'monthly_values': monthly_values,  
        'max_value': max_value,
        'min_value': min_value,
        'average_value': average_value,
        'max_month_value': max_month_value,
        'min_month_value': min_month_value,
        'average_month_value': average_month_value,
        'data': all_data,
        'season_value':season_value,
        'annual_value':annual_value
    })


def create_month_choices():
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    print("month",months)
    for month in months:
        Month.objects.get_or_create(name=month)

# Connect the function to the post_migrate signal
@receiver(post_migrate)
def post_migrate_handler(sender, **kwargs):
    if sender.name == 'weather_app':
        print('weather-app')
        create_month_choices()  