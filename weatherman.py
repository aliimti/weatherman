import argparse
import calendar
import csv
import glob
import os
import re
import statistics
from colorama import Fore, Style


def validate_input_date(date_input):
    pattern = r'^\d{4}/(0[1-9]|1[0-2])$'
    if re.match(pattern, date_input):
        return True
    return False


def convert_month(weather_month_input):
    month_number = int(weather_month_input)
    if 1 <= month_number <= 12:
        return calendar.month_abbr[month_number]


def receive_weather_file_names(base_directory, weather_year, weather_month=None):
    pattern = f"*{weather_year}*"
    if weather_month:
        pattern = f"*{weather_year}*{weather_month}*"

    weatherman_file_names = glob.glob(os.path.join(base_directory, pattern))
    return weatherman_file_names


def read_weather_files(weather_year, weather_month, base_directory):
    weather_records = []

    weatherman_file_names = receive_weather_file_names(base_directory, weather_year, weather_month)

    for weathermas_file_path in weatherman_file_names:
        with open(weathermas_file_path, 'r') as weather_file:
            weather_file_reader = csv.DictReader(weather_file)
            weather_records.extend(weather_file_reader)

    return weather_records


def calculate_yearly_weather_records(weather_records):
    yearly_weather_record = {
        'highest_temperature': float('-inf'),
        'lowest_temperature': float('inf'),
        'highest_temperature_day': None,
        'lowest_temperature_day': None,
        'most_humidity_day': None,
        'most_humidity': 0
    }

    for weather_record in weather_records:
        maximum_temperature = weather_record.get('Max TemperatureC')
        minimum_temperature = weather_record.get('Min TemperatureC')
        humidity = weather_record.get('Max Humidity')

        if maximum_temperature:
            yearly_weather_record['highest_temperature'], yearly_weather_record['highest_temperature_day'] = max(
                (yearly_weather_record['highest_temperature'], yearly_weather_record['highest_temperature_day']),
                (float(maximum_temperature), weather_record['PKT'])
            )

        if minimum_temperature:
            yearly_weather_record['lowest_temperature'], yearly_weather_record['lowest_temperature_day'] = min(
                (yearly_weather_record['lowest_temperature'], yearly_weather_record['lowest_temperature_day']),
                (float(minimum_temperature), weather_record['PKT'])
            )

        if humidity:
            yearly_weather_record['most_humidity'], yearly_weather_record['most_humidity_day'] = max(
                (yearly_weather_record['most_humidity'], yearly_weather_record['most_humidity_day']),
                (float(humidity), weather_record['PKT'])
            )

    return yearly_weather_record


def calculate_monthly_weather_record(weather_records):
    mean_humidity_values = [float(record.get(' Mean Humidity') or 0) for record in weather_records]
    highest_temperature_values = [float(record.get('Max TemperatureC') or 0) for record in weather_records]
    lowest_temperature_values = [float(record.get('Min TemperatureC') or 0) for record in weather_records]

    month_weather_record = {
        'mean_humidity': statistics.mean(mean_humidity_values),
        'average_lowest_temperature': statistics.mean(lowest_temperature_values),
        'average_highest_temperature': statistics.mean(highest_temperature_values),
    }

    return month_weather_record


def print_yearly_weather_record(weather_record):
    print(f"Highest Temperature: {weather_record['highest_temperature']}°C on {weather_record['highest_temperature_day']}")
    print(f"Lowest Temperature: {weather_record['lowest_temperature']}°C on {weather_record['lowest_temperature_day']}")
    print(f"Most humidity {weather_record['most_humidity']}% on {weather_record['most_humidity_day']}")


def print_monthly_weather_record(monthly_data):
    print(f"Average Lowest Temperature: {monthly_data['average_lowest_temperature']:.3f}°C")
    print(f"Average Highest Temperature: {monthly_data['average_highest_temperature']:.3f}°C")
    print(f"Average Mean Humidity: {monthly_data['mean_humidity']:.3f}%")


def generate_weather_bar_chart(weather_records):
    for weather_record in weather_records:
        date = weather_record['PKT']

        max_temp_str = weather_record['Max TemperatureC']
        min_temp_str = weather_record['Min TemperatureC']

        if max_temp_str.isdigit() and min_temp_str.isdigit():
            maximum_temperature = int(max_temp_str)
            minimum_temperature = int(min_temp_str)
            reset_code = Style.RESET_ALL

            color_code = Fore.RED
            bar = "+" * maximum_temperature
            print(f"{color_code}{date} {bar:<1} {maximum_temperature}C{reset_code}")

            color_code = Fore.BLUE
            bar = "+" * minimum_temperature
            print(f"{color_code}{date} {bar:<1} {minimum_temperature}C{reset_code}")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process weatherman data files")
    parser.add_argument(
        "-e", "--weather_year",
        help="For a given year, it will display the highest temperature and day,"
             " lowest temperature and day, most humid day and humidity."
    )
    parser.add_argument(
        "-a", "--weather_year_month",
        help="For a given month, it will display the average highest temperature,"
             " average lowest temperature, average mean humidity."
    )
    parser.add_argument(
        "-c", "--weather_bar_chart",
        help="For a given month, it will draw two horizontal bar charts on the console"
             " for the highest and lowest temperature on each day. Highest in"
             " red and lowest in blue."
    )
    args = parser.parse_args()

    if args.weather_year_month and not validate_input_date(args.weather_year_month):
        parser.error("Invalid input for -a option. Please use the format 'yyyy/mm' for year and month.")

    if args.weather_bar_chart and not validate_input_date(args.weather_bar_chart):
        parser.error("Invalid input for -c option. Please use the format 'yyyy/mm' for year and month.")

    return args


def fetch_monthly_conditions(parsed_arguments, base_directory):
    weather_year, weather_month_input = parsed_arguments.weather_year_month.split('/')
    try:
        weather_month = convert_month(weather_month_input)
        weather_records = read_weather_files(weather_year, weather_month, base_directory)
        statistics_month = calculate_monthly_weather_record(weather_records)
        print_monthly_weather_record(statistics_month)
    except ValueError as error:
        print("Invalid input for year_month", error)


def fetch_barchart_conditions(parsed_arguments, base_directory):
    weather_year, weather_month_input = parsed_arguments.weather_bar_chart.split('/')

    weather_month = convert_month(weather_month_input)
    weather_records = read_weather_files(weather_year, weather_month, base_directory)
    generate_weather_bar_chart(weather_records)


def fetch_yearly_conditions(parsed_arguments, base_directory):
    weather_year = parsed_arguments.weather_year
    weather_records = read_weather_files(weather_year, None, base_directory)
    statistics_year = calculate_yearly_weather_records(weather_records)
    print_yearly_weather_record(statistics_year)


def main():
    base_directory = r"D:\Cogent Labs\weatherfiles\weatherfiles"
    parsed_arguments = parse_arguments()

    weatherman_workflow = {
        "weather_year": lambda: fetch_yearly_conditions(parsed_arguments, base_directory),
        "weather_year_month": lambda: fetch_monthly_conditions(parsed_arguments, base_directory),
        "weather_bar_chart": lambda: fetch_barchart_conditions(parsed_arguments, base_directory),
    }

    for weatherman_action_name, weatherman_action_function in weatherman_workflow.items():
        if hasattr(parsed_arguments, weatherman_action_name) and getattr(parsed_arguments, weatherman_action_name):
            weatherman_action_function()


if __name__ == "__main__":
    main()
