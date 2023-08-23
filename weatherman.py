import argparse
import calendar
from colorama import Fore, Style
import csv
import glob
import os

def convert_month(weather_month_input):
    try:
        month_number = int(weather_month_input)
        if 1 <= month_number <= 12:
            return calendar.month_abbr[month_number]
    except ValueError:
        raise ValueError("Invalid input")
    
def read_files(weather_year, weather_month):
    weather_details = []

    base_directory = r"D:\Cogent Labs\weatherfiles\weatherfiles"
    pattern = f"*{weather_year}*"
    if weather_month:
        pattern = f"*{weather_year}*{weather_month}*"

    files_to_process = glob.glob(os.path.join(base_directory, pattern))

    for weathermas_file_path in files_to_process:
        with open(weathermas_file_path, 'r') as weather_file:
            reader = csv.DictReader(weather_file)
            weather_details.extend(reader)
    
    return weather_details

def calculate_statistics_year(weather_details):
    year_statistics = {
        'highest_temperature': float('-inf'),
        'lowest_temperature': float('inf'),
        'highest_temperature_day': None,
        'lowest_temperature_day': None,
        'most_humidity_day': None,
        'most_humidity': 0
    }

    for row in weather_details:
        maximum_temperature = row['Max TemperatureC']
        minimum_temperature = row['Min TemperatureC']
        humidity = row['Max Humidity']

        try:
            if maximum_temperature and float(maximum_temperature) > year_statistics['highest_temperature']:
                year_statistics['highest_temperature'] = float(maximum_temperature)
                year_statistics['highest_temperature_day'] = row['PKT']

            if minimum_temperature is not None and float(minimum_temperature) < year_statistics['lowest_temperature']:
                year_statistics['lowest_temperature'] = float(minimum_temperature)
                year_statistics['lowest_temperature_day'] = row['PKT']

            if humidity and float(humidity) > year_statistics['most_humidity']:
                year_statistics['most_humidity'] = float(humidity)
                year_statistics['most_humidity_day'] = row['PKT']
        except ValueError:
            continue

    return year_statistics


def calculate_statistics_month(weather_details):
    month_statistics = {
        'mean_humidity': 0,
        'mean_iteration': 0,
        'average_lowest_temperature': 0,
        'average_highest_temperature': 0
    }

    for row in weather_details:
        mean_humidity_row = row[' Mean Humidity']
        maximum_temperature = row['Max TemperatureC']
        minimum_temperature = row['Min TemperatureC']

        try:
            if mean_humidity_row and float(mean_humidity_row) > 0:
                month_statistics['mean_humidity'] += float(mean_humidity_row)
                month_statistics['mean_iteration'] += 1

            if maximum_temperature and float(maximum_temperature) > 0:
                month_statistics['average_highest_temperature'] += float(maximum_temperature)

            if minimum_temperature and float(minimum_temperature) > 0:
                month_statistics['average_lowest_temperature'] += float(minimum_temperature)
        except ValueError:
            continue

    return month_statistics


def print_year_statistics(highest_temperature, highest_temperature_day, lowest_temperature, lowest_temperature_day, most_humidity, most_humidity_day):
    print(f"Highest Temperature: {highest_temperature}°C on {highest_temperature_day}")
    print(f"Lowest Temperature: {lowest_temperature}°C on {lowest_temperature_day}")
    print(f"Most humidity {most_humidity}% on  {most_humidity_day} ")

def print_month_statistics(mean_iteration, mean_humidity, average_lowest_temperature, average_highest_temperature):
    if mean_iteration > 0:
        average_mean_iteration = mean_humidity / mean_iteration
        average_highest_temperature /= mean_iteration
        average_lowest_temperature /= mean_iteration

        print(f"Average Lowest Temperature: {average_lowest_temperature:.3f}")
        print(f"Average Highest Temperature: {average_highest_temperature:.3f}")
        print(f"Average Mean Humidity: {average_mean_iteration:.3f}%")
    else:
        print("No valid data found for the given month.")


def generate_weather_bar_chart(weather_details):
    for row in weather_details:
        date = row['PKT']

        try:
            maximum_temperature = int(row['Max TemperatureC'])
            minimum_temperature = int(row['Min TemperatureC'])
            reset_code = Style.RESET_ALL

            color_code = Fore.RED
            bar = "+" * maximum_temperature
            print(f"{color_code}{date} {bar:<25} {maximum_temperature}C{reset_code}")

            color_code = Fore.BLUE
            bar = "+" * minimum_temperature
            print(f"{color_code}{date} {bar:<25} {minimum_temperature}C{reset_code}")

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
    args = parse_arguments()
    weather_year = None
    weather_month = None

    if args.weather_year_month:
        weather_year, weather_month_input = args.weather_year_month.split('/')
        try:
            weather_month = convert_month(weather_month_input)
        except ValueError as e:
            print(e)
            return

    if args.weather_year:
        weather_year = args.weather_year

    if args.weather_bar_chart:
        weather_year, weather_month_input = args.weather_bar_chart.split('/')
        try:
            weather_month = convert_month(weather_month_input)
        except ValueError as e:
            print(e)
            return

    if not weather_year:
        print("Please provide a year using the '-e', '-a', or '-c' option.")
    else:
        weather_details = read_files(weather_year, weather_month)

        if args.weather_year:
            statistics_year = calculate_statistics_year(weather_details)
            print_year_statistics(**statistics_year)

        if args.weather_year_month:
            statistics_month = calculate_statistics_month(weather_details)
            print_month_statistics(**statistics_month)

        if args.weather_bar_chart:
            generate_weather_bar_chart(weather_details)

if __name__ == "__main__":
    main()