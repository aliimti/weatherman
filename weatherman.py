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


def receive_weather_file_names(BASE_DIRECTORY, yearly_temperatures, weather_month=None):
    pattern = f"*{yearly_temperatures}*"
    if weather_month:
        pattern = f"*{yearly_temperatures}*{weather_month}*"

    weatherman_file_names = glob.glob(os.path.join(BASE_DIRECTORY, pattern))
    return weatherman_file_names


def read_weather_files(yearly_temperatures, weather_month, BASE_DIRECTORY):
    weather_records = []

    weatherman_file_names = receive_weather_file_names(BASE_DIRECTORY, yearly_temperatures, weather_month)

    for weathermas_file_path in weatherman_file_names:
        with open(weathermas_file_path, 'r') as weather_file:
            weather_file_reader = csv.DictReader(weather_file)
            weather_records.extend(weather_file_reader)
    return weather_records


def calculate_yearly_weather_records(weather_records):
    maximum_temp_record = max(weather_records, key=lambda x: float(x.get('Max TemperatureC', '-inf') or '-inf'))
    minimum_temp_record = min(weather_records, key=lambda x: float(x.get('Min TemperatureC', 'inf') or 'inf'))
    most_humidity_record = max(weather_records, key=lambda x: float(x.get('Max Humidity', '0') or '0'))

    yearly_weather_record = {
        'max_temp_value': float(maximum_temp_record['Max TemperatureC']),
        'max_temp_day': maximum_temp_record['PKT'],
        'min_temp_value': float(minimum_temp_record['Min TemperatureC']),
        'min_temp_day': minimum_temp_record['PKT'],
        'max_humidity_value': float(most_humidity_record['Max Humidity']),
        'max_humidity_day': most_humidity_record['PKT']
    }

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
    print(f"Maximum Temperature {weather_record['max_temp_value']}°C on {weather_record['max_temp_day']}")
    print(f"Minimum Temperature {weather_record['min_temp_value']}°C on {weather_record['min_temp_day']}")
    print(f"Most Humidity {weather_record['max_humidity_value']}% on {weather_record['max_humidity_day']}")


def print_monthly_weather_record(monthly_data):
    print(f"Average Lowest Temperature: {monthly_data['average_lowest_temperature']:.3f}°C")
    print(f"Average Highest Temperature: {monthly_data['average_highest_temperature']:.3f}°C")
    print(f"Average Mean Humidity: {monthly_data['mean_humidity']:.3f}%")


def generate_weatherman_monthly_barchart(weather_records):
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
        "-e", "--yearly_temperatures",
        help="For a given year, it will display the highest temperature and day,"
             " lowest temperature and day, most humid day and humidity."
    )
    parser.add_argument(
        "-a", "--weatherman_monthly_temperatures",
        help="For a given month, it will display the average highest temperature,"
             " average lowest temperature, average mean humidity."
    )
    parser.add_argument(
        "-c", "--weatherman_monthly_barchart",
        help="For a given month, it will draw two horizontal bar charts on the console"
             " for the highest and lowest temperature on each day. Highest in"
             " red and lowest in blue."
    )
    args = parser.parse_args()

    if args.weatherman_monthly_temperatures and not validate_input_date(args.weatherman_monthly_temperatures):
        parser.error("Invalid input for -a option. Please use the format 'yyyy/mm' for year and month.")

    if args.weatherman_monthly_barchart and not validate_input_date(args.weatherman_monthly_barchart):
        parser.error("Invalid input for -c option. Please use the format 'yyyy/mm' for year and month.")

    return args


def monthly_weather_results(parsed_argument, BASE_DIRECTORY):
    yearly_temperatures, weather_month_input = parsed_argument.weatherman_monthly_temperatures.split('/')
    weather_month = convert_month(weather_month_input)
    weather_records = read_weather_files(yearly_temperatures, weather_month, BASE_DIRECTORY)
    statistics_month = calculate_monthly_weather_record(weather_records)
    print_monthly_weather_record(statistics_month)


def barchart_weather_results(parsed_argument, BASE_DIRECTORY):
    yearly_temperatures, weather_month_input = parsed_argument.weatherman_monthly_barchart.split('/')
    weather_month = convert_month(weather_month_input)
    weather_records = read_weather_files(yearly_temperatures, weather_month, BASE_DIRECTORY)
    generate_weatherman_monthly_barchart(weather_records)


def yearly_weather_results(parsed_argument, BASE_DIRECTORY):
    yearly_temperatures = parsed_argument.yearly_temperatures
    weather_records = read_weather_files(yearly_temperatures, None, BASE_DIRECTORY)
    statistics_year = calculate_yearly_weather_records(weather_records)
    print_yearly_weather_record(statistics_year)


def main():
    BASE_DIRECTORY = r"D:\Cogent Labs\weatherfiles\weatherfiles"
    parsed_argument = parse_arguments()

    weatherman_workflow = {
        "yearly_temperatures": yearly_weather_results,
        "weatherman_monthly_temperatures": monthly_weather_results,
        "weatherman_monthly_barchart": barchart_weather_results,
    }

    for parser_name, corresponding_function in weatherman_workflow.items():
        if hasattr(parsed_argument, parser_name) and getattr(parsed_argument, parser_name):
            corresponding_function(parsed_argument, BASE_DIRECTORY)

    
if __name__ == "__main__":
    main()
