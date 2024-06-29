from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import json
from PIL import Image

# Function to correct the threshold value to be considered in linear regression, based on the computer vision model
def calculate_percentages(json_file, threshold, accumul_light):
    with open(json_file) as f:
        data = json.load(f)
        data = data['detections']

    total_tomato = 0

    light_percentage = accumul_light/threshold

    total_tomato = (data['b_fully_ripened'] + data['l_fully_ripened'] + data['b_half_ripened'] + data['l_half_ripened'] + data['l_green'] + data['b_green'])

    if total_tomato > 0:
        # Calculate the percentages from computer vision model
        fully_ripened_percentage = (data['b_fully_ripened'] + data['l_fully_ripened']) / total_tomato
        fully_half_ripened_percentage = (data['b_fully_ripened'] + data['l_fully_ripened'] + data['b_half_ripened'] + data['l_half_ripened']) / total_tomato

        # According to computer vision, the harvesting point has already been reached. The threshold is the current accumulated light value
        if ((fully_ripened_percentage >= 0.9) and (fully_half_ripened_percentage >= 0.95)) or (fully_ripened_percentage >= 0.95):
            return accumul_light

        threshold *= (1+light_percentage-fully_half_ripened_percentage)

    return threshold

# Function to calculate the accumulated sum and determine how many acquisitions are left to reach the threshold
def calculate_acquisitions_until_threshold(values, threshold, acquisitions_day, file, user_id):
    accumulated = 0
    accumulated_acquisition = [0]
    nacquisitions = 0
    threshold_init = threshold

    # Accumulation of values
    for value in values:
        accumulated += value
        accumulated_acquisition.append(accumulated)
        nacquisitions += 1

    # Check threshold
    threshold = calculate_percentages(file, threshold, accumulated_acquisition[-1])
        
    # Performing the linear regression
    accumulated_acquisition = np.array(accumulated_acquisition)
    acquisitions = np.arange(0, len(accumulated_acquisition))
    coefficients = np.polyfit(acquisitions, accumulated_acquisition, 1)
    polynomial = np.poly1d(coefficients)

    # Calculating the point where the regression line reaches the threshold
    threshold_acquisition = np.ceil((threshold - polynomial(0)) / coefficients[0])
    x_intersection = (threshold - polynomial(0)) / coefficients[0]

    # Plots
    x_next_acquisition = x_intersection + 1
    y_next_acquisition = polynomial(x_next_acquisition)
    plt.figure(figsize=(10, 6))
    plt.plot(acquisitions, accumulated_acquisition, marker='o', linestyle='-', color='b', label='Light Accumulation')
    plt.plot(acquisitions, polynomial(acquisitions), linestyle='--', color='r', label='Linear Regression Trend')
    plt.plot([0, x_next_acquisition], [polynomial(0), y_next_acquisition], linestyle='--', color='r')
    plt.axhline(y=threshold_init, color='y', linestyle='-', label='Initial Light Threshold')
    plt.axhline(y=threshold, color='g', linestyle='-', label='Corrected Light Threshold')
    plt.axvline(x=threshold_acquisition, color='m', linestyle='--', label=f'Threshold Acquisition Prevision: {int(threshold_acquisition)}')
    plt.title('Light Accumulation and Linear Regression')
    plt.xlabel(f'Acquisitions ({acquisitions_day} per day)')
    plt.ylabel('Light Accumulation [Lux]')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(user_id + "/plot_acumul.png")
    # img = Image.open('plot_acumul.png')
    # img.show()

    # Conversion to days
    acquisitions_until_threshold = threshold_acquisition - nacquisitions
    days_until_threshold = round(acquisitions_until_threshold / acquisitions_day)
    threshold_day = round(threshold_acquisition / acquisitions_day)
    
    return days_until_threshold, threshold_day

##########################################    //    ################################################
if __name__ == "__main__":

    light_values = np.random.randint(1500, 2500, 300)        # Vector of light values with 200 indices (example)
    threshold = 2000000                                     # Desired threshold
    acquisitions_day = 8                                    # Acquisitions per day (assuming acquisitions every 3 hours)
    file = 'test.json'                                      # Computer Vision json

    days_until_threshold, threshold_day = calculate_acquisitions_until_threshold(light_values, threshold, acquisitions_day, file, '.')

    # Obtaining the date
    today = datetime.today()
    date_after_days = today + timedelta(days=days_until_threshold)

    # Results Print
    print(f"Cycle Time: {threshold_day} days.")
    print(f"Days until harvest: {days_until_threshold} days.")
    print(f"The expected date is {date_after_days.date()}.")
