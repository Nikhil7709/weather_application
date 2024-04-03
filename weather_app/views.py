from statistics import mean
from django.shortcuts import render
from django.db.models.signals import post_migrate

from .models import (
    Region,
    Parameter,
    Season,
    SeasonalData,
    Year,
    Month,
    MonthlyData,
    AnnualData,
    Annual,
)
from .utils import scrape_data
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.core.paginator import Paginator
import logging


logger = logging.getLogger(__name__)


def fetch_data_view(request):
    regions = Region.objects.all()
    parameters = Parameter.objects.all()

    for region in regions:
        for parameter in parameters:
            data = scrape_data(region.name, parameter.name)
            if data is None:
                logger.error(
                    f"Failed to retrieve data for {region.name} - {parameter.name}"
                )
                continue

            lines = data.strip().split("\n")
            if len(lines) < 7:
                logger.error(
                    f"Invalid data format for {region.name} - {parameter.name}"
                )
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

                    # Get seasonal data for the current year
                    seasonal_data = seasonal_data_dict.get(year)
                    if seasonal_data and len(seasonal_data) >= 16:

                        seasonal_data = [
                            None if value == "---" else value for value in seasonal_data
                        ]
                        seasons = Season.objects.all()

                        # store the seasonal data
                        for season in seasons:
                            value = seasonal_data[season.column]
                            SeasonalData.objects.get_or_create(
                                year=year_obj,
                                region=region,
                                params=parameter,
                                season=season,
                                value=value,
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
                                value=value,
                            )

                        # store anuual data
                        annual = Annual.objects.all()
                        for ann in annual:
                            values = seasonal_data[ann.column]

                        annual, _ = AnnualData.objects.get_or_create(
                            value=values,
                            year=year_obj,
                            region=region,
                            params=parameter,
                        )
                    else:
                        print(
                            f"No seasonal data found for year {year} in {region.name} - {parameter.name}"
                        )

                except IntegrityError as e:
                    print(f"Error creating year {year}: {e}")

            print("Data saved successfully.")
    return render(request, "home.html")


def get_region_parameter_data(request, region, parameter):
    """
    Show the all data on UI
    """
    years = Year.objects.all()
    year_list = [year for year in years]

    regions = Region.objects.all()
    parameters = Parameter.objects.all()

    queryset_annual = AnnualData.objects.filter(
        params__name=parameter, region__name=region
    )
    queryset_monthly = MonthlyData.objects.filter(
        params__name=parameter, region__name=region
    )
    queryset_season = SeasonalData.objects.filter(
        params__name=parameter, region__name=region
    )

    data = {}

    # Concatenating Monthly Data
    for monthly_data in queryset_monthly:
        if monthly_data.year.year not in data:
            data[monthly_data.year.year] = {}
        if "monthly" not in data[monthly_data.year.year]:
            data[monthly_data.year.year]["monthly"] = {}
        data[monthly_data.year.year]["monthly"][
            monthly_data.month.name
        ] = monthly_data.value
        print(
            "at line 183",
            data[monthly_data.year.year]["monthly"][monthly_data.month.name],
        )

    # Concatenating Seasonal Data
    for season_data in queryset_season:
        if season_data.year.year not in data:
            data[season_data.year.year] = {}
        if "seasonal" not in data[season_data.year.year]:
            data[season_data.year.year]["seasonal"] = {}
        data[season_data.year.year]["seasonal"][
            season_data.season.name
        ] = season_data.value

    # Concatenating Annual Data
    for annual_data in queryset_annual:
        if annual_data.year.year not in data:
            data[annual_data.year.year] = {}
        data[annual_data.year.year]["annual"] = annual_data.value

    ranges = []
    avg_values_rounded = []

    # Calculate and print min, max, and average for each year
    for year, year_data in data.items():
        all_values = list(year_data["monthly"].values())
        min_value = min(all_values)
        max_value = max(all_values)
        avg_value = mean(all_values)
        avg_value_rounded = round(avg_value, 2)
        print(
            f"Year: {year}, Min: {min_value}, Max: {max_value}, Avg: {avg_value_rounded}"
        )

        # Concatenate min, max, and avg to the data dictionary
        data[year]["min"] = min_value
        data[year]["max"] = max_value
        data[year]["avg"] = avg_value_rounded
        avg_values_rounded.append(avg_value_rounded)

        ranges.append([min_value, max_value])

    avg_values_rounded_list = list(avg_values_rounded)

    context = {
        "regions": regions,
        "parameters": parameters,
        "min_values": [min_value for item in data.values()],
        "max_values": [max_value for item in data.values()],
        "avg_values": [avg_value_rounded for item in data.values()],
    }

    page_number = request.GET.get("page", 1)
    page_size = 5
    paginator = Paginator(list(data.items()), page_size)
    page_obj = paginator.get_page(page_number)

    # return render(request, 'value.html', {
    #     'years': year_list,
    #     'ranges': ranges,
    #     'context':context,
    #     'page_obj':page_obj
    # })

    return render(
        request,
        "merge_page.html",
        {
            "years": year_list,
            "ranges": ranges,
            "context": context,
            "page_obj": page_obj,
        },
    )

# def concatenate_data(queryset, data_type, data):
#     for data_entry in queryset:
#         if data_entry.year.year not in data:
#             data[data_entry.year.year] = {}
#         if data_type not in data[data_entry.year.year]:
#             data[data_entry.year.year][data_type] = {}
#         if data_type == 'annual':
#             data[data_entry.year.year][data_type] = data_entry.value
#         else:
#             data[data_entry.year.year][data_type][getattr(data_entry, data_type).name] = data_entry.value



def data_fetch(request):

    # To show data by selecting parameter and region from dropdown list

    region = request.GET.get('region')
    parameter = request.GET.get('parameter')
    years = Year.objects.all()
    year_list = [year for year in years] 
    
    regions = Region.objects.all()
    parameters = Parameter.objects.all()
    
    queryset_annual = AnnualData.objects.filter(params__name=parameter, region__name=region)
    queryset_monthly = MonthlyData.objects.filter(params__name=parameter, region__name=region)
    queryset_season = SeasonalData.objects.filter(params__name=parameter, region__name=region)

    data = {}

    # concatenate_data(queryset_monthly, 'monthly', data)
    # concatenate_data(queryset_season, 'seasonal', data)
    # concatenate_data(queryset_annual, 'annual', data)


    # Concatenating Monthly Data
    for monthly_data in queryset_monthly:    
        if monthly_data.year.year not in data:
            data[monthly_data.year.year] = {}
        if 'monthly' not in data[monthly_data.year.year]:
            data[monthly_data.year.year]['monthly'] = {}
        data[monthly_data.year.year]['monthly'][monthly_data.month.name] = monthly_data.value

    # Concatenating Seasonal Data
    for season_data in queryset_season:
        if season_data.year.year not in data:
            data[season_data.year.year] = {}
        if 'seasonal' not in data[season_data.year.year]:
            data[season_data.year.year]['seasonal'] = {}
        data[season_data.year.year]['seasonal'][season_data.season.name] = season_data.value

    # Concatenating Annual Data
    for annual_data in queryset_annual:    
        if annual_data.year.year not in data:
            data[annual_data.year.year] = {}
        data[annual_data.year.year]['annual'] = annual_data.value

    ranges = []
    avg_values_rounded = []

   # Calculate and print min, max, and average for each year
    for year, year_data in data.items():
        all_values = list(year_data['monthly'].values())
        min_value = min(all_values)
        max_value = max(all_values)
        avg_value = mean(all_values)
        avg_value_rounded = round(avg_value, 2)
        print(f"Year: {year}, Min: {min_value}, Max: {max_value}, Avg: {avg_value_rounded}")

        # Concatenate min, max, and avg to the data dictionary
        data[year]['min'] = min_value
        data[year]['max'] = max_value
        data[year]['avg'] = avg_value_rounded
        avg_values_rounded.append(avg_value_rounded)

        ranges.append([min_value, max_value])

    avg_values_rounded_list = list(avg_values_rounded)
   
    context = {
    'regions': regions,
    'parameters': parameters,
    'data':data,
    'min_values': [min_value for item in data.values()],
    'max_values': [max_value for item in data.values()],
    'avg_values': [avg_value_rounded for item in data.values()],
    'parameter': parameter,
    }

    paginator = Paginator(list(data.items()), 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
  
    return render(request, 'merge_page.html', {
        'years': year_list,
        'ranges': ranges,
        'context':context,
        'page_obj':page_obj,
    })

def create_month_choices():
    months = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]
    print("month", months)
    for month in months:
        Month.objects.get_or_create(name=month)


# Connect the function to the post_migrate signal
@receiver(post_migrate)
def post_migrate_handler(sender, **kwargs):
    if sender.name == "weather_app":
        if not Month.objects.exists():
            print("weather-app")
            create_month_choices()