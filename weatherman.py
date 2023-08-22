import os
import csv
import argparse
from colorama import Fore, Style

def convert_month(month_input):
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    if month_input.isdigit() and 1 <= int(month_input) <= 12:
        return month_names[int(month_input) - 1]
    return None

def read_files(year, month):
    headers = []

    for iterate in os.listdir(r"D:\Cogent Labs\github\weatherman\weatherfiles"):
        if year in iterate and (not month or month in iterate):
            file_path = os.path.join(r"D:\Cogent Labs\github\weatherman\weatherfiles", iterate)

            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    headers.append(row)
    
    return headers

def calculate_statistics(headers):
    highest_temp = float('-inf')
    lowest_temp = float('inf')
    most_humid_day = None
    most_humidity = 0
    meandata = 0
    mean_humidity = 0
    average_lowest_temp = 0
    average_highest_temp = 0

    for row in headers:
        max_temp = row['Max TemperatureC']
        min_temp = row['Min TemperatureC']
        humidity = row['Max Humidity']
        m_humidity = row[' Mean Humidity']

        try:
            if max_temp and float(max_temp) > highest_temp:
                highest_temp = float(max_temp)
                highest_temp_day = row['PKT']

            if min_temp and float(min_temp) < lowest_temp:
                lowest_temp = float(min_temp)
                lowest_temp_day = row['PKT']

            if humidity and float(humidity) > most_humidity:
                most_humidity = float(humidity)
                most_humid_day = row['PKT']

            if m_humidity and float(m_humidity) > 0:
                meandata += float(m_humidity)
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
        mean_humidity, meandata,
        average_lowest_temp, average_highest_temp
    )

def print_statistics(args, highest_temp, highest_temp_day, lowest_temp, lowest_temp_day, most_humidity, most_humid_day, mean_humidity, meandata, average_lowest_temp, average_highest_temp):
    if args.year_month:
        if mean_humidity > 0:
            average_mean_humidity = meandata / mean_humidity
            average_highest_temp /= mean_humidity
            average_lowest_temp /= mean_humidity

            print(f"Average Lowest Temperature: {average_lowest_temp:.3f}")
            print(f"Average Highest Temperature: {average_highest_temp:.3f}")
            print(f"Average Mean Humidity: {average_mean_humidity:.3f}%")
        else:
            print("No valid data found for the given month.")

    if args.year:  
        print(f"Highest Temperature: {highest_temp}°C on {highest_temp_day}")
        print(f"Lowest Temperature: {lowest_temp}°C on {lowest_temp_day}")
        print(f"Most Humid Day: {most_humid_day} with humidity {most_humidity}%")

def generate_bar_chart(headers):
    
    for row in headers:
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
    parser.add_argument("-e", "--year", help="Search files containing the specified year")
    parser.add_argument("-a", "--year_month", help="Search files containing the specified year and month (in the format 'YYYY/MM' or 'YYYY/Mon')")
    parser.add_argument("-c", "--bar_chart", help="Search files containing the specified year and month (in the format 'YYYY/MM' or 'YYYY/Mon')")
    return parser.parse_args()

def main():
    args = parse_arguments()
    year = None
    month = None
    
    if args.year_month:
        year, month_input = args.year_month.split('/')
        month = convert_month(month_input)
    
    if args.year:
        year = args.year

    if args.bar_chart:
        year, month_input = args.bar_chart.split('/')
        month = convert_month(month_input)

    if not year:
        print("Please provide a year using the '-e', '-a', or '-c' option.")
    else:
        headers = read_files(year, month)
        (
            highest_temp, highest_temp_day,
            lowest_temp, lowest_temp_day,
            most_humidity, most_humid_day,
            mean_humidity, meandata,
            average_lowest_temp, average_highest_temp
        ) = calculate_statistics(headers)

        print_statistics(args, highest_temp, highest_temp_day, lowest_temp, lowest_temp_day, most_humidity, most_humid_day, mean_humidity, meandata, average_lowest_temp, average_highest_temp)

        if args.bar_chart:
            generate_bar_chart(headers)

if __name__ == "__main__":
    main()
