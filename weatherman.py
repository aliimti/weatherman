import argparse
import calendar
import csv
import glob
import os
from colorama import Fore, Style


def convert_month(weather_month_input):
    try:
        month_number = int(weather_month_input)
        if 1 <= month_number <= 12:
            return calendar.month_abbr[month_number]
    except ValueError:
        raise ValueError("Invalid input: Please provide a valid month number between 1 and 12")


def generate_weather_file_names(base_directory, weather_year, weather_month=None):
    pattern = f"*{weather_year}*"
    if weather_month:
        pattern = f"*{weather_year}*{weather_month}*"

    files_to_process = glob.glob(os.path.join(base_directory, pattern))
    return files_to_process


def read_weather_files(weather_year, weather_month):
    weather_records = []

    base_directory = r"D:\Cogent Labs\weatherfiles\weatherfiles"
    files_to_process = generate_weather_file_names(base_directory, weather_year, weather_month)

    for weathermas_file_path in files_to_process:
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
        maximum_temperature = weather_record['Max TemperatureC']
        minimum_temperature = weather_record['Min TemperatureC']
        humidity = weather_record['Max Humidity']

        try:
            if maximum_temperature and float(maximum_temperature) > yearly_weather_record['highest_temperature']:
                yearly_weather_record['highest_temperature'] = float(maximum_temperature)
                yearly_weather_record['highest_temperature_day'] = weather_record['PKT']

            if minimum_temperature is not None and float(minimum_temperature) < yearly_weather_record['lowest_temperature']:
                yearly_weather_record['lowest_temperature'] = float(minimum_temperature)
                yearly_weather_record['lowest_temperature_day'] = weather_record['PKT']

            if humidity and float(humidity) > yearly_weather_record['most_humidity']:
                yearly_weather_record['most_humidity'] = float(humidity)
                yearly_weather_record['most_humidity_day'] = weather_record['PKT']
        except ValueError:
            continue

    return yearly_weather_record


def calculate_monthly_weather_record(weather_records):
    month_weather_record = {
        'mean_humidity': 0,
        'mean_iteration': 0,
        'average_lowest_temperature': 0,
        'average_highest_temperature': 0
    }

    for weather_record in weather_records:
        mean_humidity_weather_record = weather_record[' Mean Humidity']
        maximum_temperature = weather_record['Max TemperatureC']
        minimum_temperature = weather_record['Min TemperatureC']

        try:
            if mean_humidity_weather_record and float(mean_humidity_weather_record) > 0:
                month_weather_record['mean_humidity'] += float(mean_humidity_weather_record)
                month_weather_record['mean_iteration'] += 1

            if maximum_temperature and float(maximum_temperature) > 0:
                month_weather_record['average_highest_temperature'] += float(maximum_temperature)

            if minimum_temperature and float(minimum_temperature) > 0:
                month_weather_record['average_lowest_temperature'] += float(minimum_temperature)
        except ValueError:
            continue

    return month_weather_record


def print_yearly_weather_record(highest_temperature, highest_temperature_day, lowest_temperature, lowest_temperature_day, most_humidity, most_humidity_day):
    print(f"Highest Temperature: {highest_temperature}°C on {highest_temperature_day}")
    print(f"Lowest Temperature: {lowest_temperature}°C on {lowest_temperature_day}")
    print(f"Most humidity {most_humidity}% on  {most_humidity_day} ")


def print_monthly_weather_record(mean_iteration, mean_humidity, average_lowest_temperature, average_highest_temperature):
    if mean_iteration > 0:
        average_mean_iteration = mean_humidity / mean_iteration
        average_highest_temperature /= mean_iteration
        average_lowest_temperature /= mean_iteration

        print(f"Average Lowest Temperature: {average_lowest_temperature:.3f}")
        print(f"Average Highest Temperature: {average_highest_temperature:.3f}")
        print(f"Average Mean Humidity: {average_mean_iteration:.3f}%")
    else:
        print("No valid data found for the given month.")


def generate_weather_bar_chart(weather_records):
    for weather_record in weather_records:
        date = weather_record['PKT']

        try:
            maximum_temperature = int(weather_record['Max TemperatureC'])
            minimum_temperature = int(weather_record['Min TemperatureC'])
            reset_code = Style.RESET_ALL

            color_code = Fore.RED
            bar = "+" * maximum_temperature
            print(f"{color_code}{date} {bar:<1} {maximum_temperature}C{reset_code}")

            color_code = Fore.BLUE
            bar = "+" * minimum_temperature
            print(f"{color_code}{date} {bar:<1} {minimum_temperature}C{reset_code}")

        except ValueError:
            continue


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process weatherman data files.")
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
    return parser.parse_args()


def main():
    parsed_arguments = parse_arguments()
    weather_year = None
    weather_month = None
    try:
        if parsed_arguments.weather_year:
            weather_year = parsed_arguments.weather_year
            weather_records = read_weather_files(weather_year, weather_month)
            statistics_year = calculate_yearly_weather_records(weather_records)
            print_yearly_weather_record(**statistics_year)

        if parsed_arguments.weather_year_month:
            weather_year, weather_month_input = parsed_arguments.weather_year_month.split('/')
            try:
                weather_month = convert_month(weather_month_input)
                weather_records = read_weather_files(weather_year, weather_month)
                statistics_month = calculate_monthly_weather_record(weather_records)
                print_monthly_weather_record(**statistics_month)
            except ValueError as error:
                print("invalid input", error)
                return

        if parsed_arguments.weather_bar_chart:
            weather_year, weather_month_input = parsed_arguments.weather_bar_chart.split('/')
            try:
                weather_month = convert_month(weather_month_input)
                weather_records = read_weather_files(weather_year, weather_month)
                generate_weather_bar_chart(weather_records)
            except ValueError as error:
                print("invalid input for bar_chart", error)
                return

    except:
        print("Please provide a year using the '-e', '-a', or '-c' option.")


if __name__ == "__main__":
    main()
