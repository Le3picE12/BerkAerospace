#####################################
# Libraries                         #
#####################################

import argparse                       # to parse command line arguments
import numpy as np                  # to perform mathematical operations
import matplotlib.pyplot as plt     # to plot graphs
import pandas as pd                 # to read CSV files and manipulate dataframes

"""
To run file: 
python kalman.py

"""

# Goal/Task is to: 
#   - Combine all 4 sensors to:
#   - Find the vechile's linear acceleration, angular rate, and altitute over time 
#   - Using Kalman filter algorithm   
#   - Output format should be t_s, ax_mps2, ay_mps2, az_mps2, wx_radps, wy_radps, wz_radps, altitude_m

# Notes: 

# Gryoscope: 
#   Provides [ANGULAR_RATE]
#   Noisy + Bias that drifts slowly
#   Rate = 500Hz
#
# Barometer: 
#   Provides [INDEPENDENT_ALTITUDE_MEASUREMENTS]
#   Noisy + Altitude is relative to launch pad
#   Rate = 25Hz

# Low-G Accelerometer:
#   Saturates during high acceleration events
#   Accurate during nomral events
#   Output clips at range limit
#   Less noise + finer resolution
#   Rate = 400Hz

# High-G Accelerometer:
#   Can measure the same events 
#   BUT is noisier and slower
#   Less range + Noisier + Coarser resolutions
#   Rate = 100Hz

# Sensor Data:
#   All sensoring measurements

#   ALL 3 (Not Barometer) PROVIDE [ANGULAR_RATE]

# 1 g = 9.80665 m/s2.

#########################
# DATA                  #
#########################

# At minimum output:

# - timestamp
# - estimated ax, ay, az
# - estimated wx, wy, wz
# - estimated altitude



# I Will use all gyroscopes to measure angular rate
# This is to provide a wider range of data 

# Will focus on 3-axis linear acceleration, 3-axis angular rate,
# and altitude.


class KalmanFilter: 

    # Setup state indices
    acceleration = [0,1,2] # ax,ay,az
    angular_rate = [3,4,5] # wx,wy,wz
    altitude = 6 # altitude
    vertical_velocity = 7 # vertical_velocity
    state_size = 8 # total state size

    def __init__(self):
        # Initialize Kalman filter parameters (Constructor)
        self.state = np.zeros(self.state_size)  # State vector

        initial_variance = [
            10.0, 10.0, 10.0,  # ax, ay, az (m/s^2)
            1.0, 1.0, 1.0,     # wx, wy, wz (rad/s)
            100.0,             # altitude (meters)
            25.0               # vertical_velocity (m/s)
        ]
        # Initialize the covariance matrix
        self.covariance = np.diag(initial_variance) 

        self.previous_timestamp = None
        self.altitude_initialized = False

        self.altitude_noise = 1.2 # Altitude has approximately 1.2 m RMS measurement noise plus a small offset.

        # Process noise parameters (tune these based on assumptions)
        self.angular_rate_noise = {
            "low_g_imu": 0.01,
            "high_g_imu": 0.02,
            "gyro": 0.03,
        }

        self.acceleration_noise = {
            "low_g_imu": 0.15, # assuming low-g accelerometer has 0.15 m/s^2 RMS noise
            "high_g_imu": 0.60, # assuming high-g accelerometer has 0.60 m/s^2 RMS noise
        }

    def predict(self, timestamp):
        # Predict the next state based on the current state and control inputs
        timestamp = float(timestamp)

        if self.previous_timestamp is None:
            self.previous_timestamp = timestamp
            return
        # delta time used for prediction step
        dt = timestamp - self.previous_timestamp

        # Base case
        if dt <= 0:
            raise ValueError("Timestamps must be in increasing order.")

        transition = np.eye(self.state_size)  # State transition matrix
        transition[self.altitude, self.vertical_velocity] = dt  # Altitude update based on vertical velocity
        
    def update(self, measurements, state_indices, noise_std):
        # Update the state estimate based on the new measurements
        pass

    def build_process_noise(self, dt):
        # Build the process noise covariance matrix based on the time step
        pass

    def process_measurement(self, row):
        # Process the sensor measurements and apply the Kalman filter
        self.predict(row["timestamp_s"])
        sensor = row["sensor"]

        # Process the measurement based on the sensor type
        if sensor in self.acceleration_noise:
            self.process_acceleration(row)

        if sensor in self.angular_rate_noise:
            self.process_angular_rate(row)

        if sensor == "barometer":
            self.process_altitude(row)

    def process_acceleration(self, row):
        # Process acceleration measurements from the low-g accelerometer
        sensor = row["sensor"]

        saturation_flag = str(
            row.get("low_g_saturated", False)
        ).strip().lower()

        saturated = saturation_flag in {"true", "1", "1.0"}

        if sensor == "low_g_imu" and saturated:
            return

        measurements = [
            row["ax_mps2"],
            row["ay_mps2"],
            row["az_mps2"]
        ]

        self.update(
            measurements,
            self.acceleration,
            self.acceleration_noise[sensor],
        )

    def process_angular_rate(self, row):
        # Process angular rate measurements from the gyroscope
        sensor = row["sensor"]
        measurements = [
            row["wx_rps"],
            row["wy_rps"],
            row["wz_rps"],
        ]

        self.update(
            measurements, 
            self.angular_rate, 
            self.angular_rate_noise[sensor]
        )

    def process_altitude(self, row):
        # Process altitude measurements from the barometer
        altitude = float(row["altitude_m"])

        if not np.isfinite(altitude):
            return
        if not self.altitude_initialized:
            index = self.altitude

            self.state[index] = altitude
            self.altitude_initialized = True

            return

        self.update(
            [altitude], 
            [self.altitude], 
            self.altitude_noise,
        )

def save_plot(): 
    # Ran out of time to implement this function. :((
    pass




# Get data 
data = pd.read_csv("sensor_fusion_sample_data/sensor_data.csv")
data = data.sort_values("timestamp_s", kind= "stable")

# Initialize Kalman filter
kf = KalmanFilter()
outputs = []

# Process each timestamp group
for timestamp, group in data.groupby("timestamp_s"):

    # Process each row in the group
    for _, row in group.iterrows():

        # Process the measurement for each row in the group
        kf.process_measurement(row)
    outputs.append({
        "t_s": timestamp,
        "ax_mps2": kf.x[0],
        "ay_mps2": kf.x[1],
        "az_mps2": kf.x[2],
        "wx_radps": kf.x[3],
        "wy_radps": kf.x[4],
        "wz_radps": kf.x[5],
        "altitude_m": (
            kf.x[6] if kf.altitude_initialized else np.nan
        ),
    })

# Create a DataFrame from the estimated values and print
estimates = pd.DataFrame(outputs)
print(estimates)