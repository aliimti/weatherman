import argparse
import calendar
from colorama import Fore, Style
import csv
import os

def convert_month(month_input):
    try:
        month_num = int(month_input)
        if 1 <= month_num <= 12:
            return calendar.month_abbr[month_num]
        else:
            raise ValueError("Invalid month number")
    except ValueError:
        raise ValueError("Invalid input")
    
def read_files(get_year, get_month):
    weather_details = []

    base_dir = r"D:\Cogent Labs\weatherfiles\weatherfiles"
    files_to_process = [filename for filename in os.listdir(base_dir)
                        if get_year in filename and (not get_month or get_month in filename)]
    
    for filename in files_to_process:
        file_path = os.path.join(base_dir, filename)

        with open(file_path, 'r') as weather_file:
            reader = csv.DictReader(weather_file)
            weather_details.extend(reader)
    
    return weather_details

def calculate_statistics(weather_details, args):
    highest_temp = float('-inf')
    lowest_temp = float('inf')
    highest_temp_day = None
    lowest_temp_day = None
    most_humid_day = None
    most_humidity = 0
    mean_value = 0
    mean_humidity = 0
    average_lowest_temp = 0
    average_highest_temp = 0

    for row in weather_details:
        max_temp = row['Max TemperatureC']
        min_temp = row['Min TemperatureC']
        humidity = row['Max Humidity']
        m_humidity = row[' Mean Humidity']

        try:
            if args.get_year:
                if max_temp and float(max_temp) > highest_temp:
                    highest_temp = float(max_temp)
                    highest_temp_day = row['PKT']

                if min_temp is not None and float(min_temp) < lowest_temp:
                    lowest_temp = float(min_temp)
                    lowest_temp_day = row['PKT']

                if humidity and float(humidity) > most_humidity:
                    most_humidity = float(humidity)
                    most_humid_day = row['PKT']

            if args.get_year_month:  
                if m_humidity and float(m_humidity) > 0:
                    mean_value += float(m_humidity)
                    mean_humidity += 1

                if max_temp and float(max_temp) > 0:
                    average_highest_temp += float(max_temp)

                if min_temp and float(min_temp) > 0:
                    average_lowest_temp += float(min_temp)

        except ValueError:
            continue  

    return (
        highest_temp, highest_temp_day,
        lowest_temp, lowest_temp_day,
        most_humidity, most_humid_day,
        mean_humidity, mean_value,
        average_lowest_temp, average_highest_temp
    )


def print_year_statistics(highest_temp, highest_temp_day, lowest_temp, lowest_temp_day, most_humidity, most_humid_day):
    print(f"Highest Temperature: {highest_temp}°C on {highest_temp_day}")
    print(f"Lowest Temperature: {lowest_temp}°C on {lowest_temp_day}")
    print(f"Most Humid Day: {most_humid_day} with humidity {most_humidity}%")

def print_month_statistics(mean_humidity, mean_value, average_lowest_temp, average_highest_temp):
    if mean_humidity > 0:
        average_mean_humidity = mean_value / mean_humidity
        average_highest_temp /= mean_humidity
        average_lowest_temp /= mean_humidity

        print(f"Average Lowest Temperature: {average_lowest_temp:.3f}")
        print(f"Average Highest Temperature: {average_highest_temp:.3f}")
        print(f"Average Mean Humidity: {average_mean_humidity:.3f}%")
    else:
        print("No valid data found for the given month.")


def generate_bar_chart(weather_details):
    for row in weather_details:
        date = row['PKT']

        try:
            max_temp = int(row['Max TemperatureC'])
            min_temp = int(row['Min TemperatureC'])
            reset_code = Style.RESET_ALL

            color_code = Fore.RED
            bar = "+" * max_temp
            print(f"{color_code}{date} {bar:<25} {max_temp}C{reset_code}")

            color_code = Fore.BLUE
            bar = "+" * min_temp
            print(f"{color_code}{date} {bar:<25} {min_temp}C{reset_code}")

        except ValueError:
            continue 

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process weather data files.")
    parser.add_argument(
        "-e", "--get_year",
        help="For a given year, display the highest temperature and day,"
             " lowest temperature and day, most humid day and humidity."
    )
    parser.add_argument(
        "-a", "--get_year_month",
        help="For a given month, display the average highest temperature,"
             " average lowest temperature, average mean humidity."
    )
    parser.add_argument(
        "-c", "--bar_chart",
        help="For a given month, draw two horizontal bar charts on the console"
             " for the highest and lowest temperature on each day. Highest in"
             " red and lowest in blue."
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    get_year = None
    get_month = None
    
    if args.get_year_month:
        get_year, month_input = args.get_year_month.split('/')
        try:
            get_month = convert_month(month_input)
        except ValueError as e:
            print(e)
            return
    
    if args.get_year:
        get_year = args.get_year

    if args.bar_chart:
        get_year, month_input = args.bar_chart.split('/')
        try:
            get_month = convert_month(month_input)
        except ValueError as e:
            print(e)
            return

    if not get_year:
        print("Please provide a year using the '-e', '-a', or '-c' option.")
    else:
        weather_details = read_files(get_year, get_month)
        (
            highest_temp, highest_temp_day,
            lowest_temp, lowest_temp_day,
            most_humidity, most_humid_day,
            mean_humidity, mean_value,
            average_lowest_temp, average_highest_temp
        ) = calculate_statistics(weather_details, args)

        if args.get_year:
            print_year_statistics(highest_temp, highest_temp_day, lowest_temp, lowest_temp_day, most_humidity, most_humid_day)

        if args.get_year_month:
            print_month_statistics(mean_humidity, mean_value, average_lowest_temp, average_highest_temp)

        if args.bar_chart:
            generate_bar_chart(weather_details)

if __name__ == "__main__":
    main()
