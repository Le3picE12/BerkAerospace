# BERK AEROSPACE 
## Setup Environment

To setup the environment, install python and create a virtual environment in the root

```bash
cd BERK_AEROSPACE_ASSESSMENT
python3 -m venv .venv 
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Then run 
``` bash
python kalman.py
```

## State Vector
The state vector uses 8 components and they are 

``` bash
x = [
    ax,ay,az,
    wx,wy,wz,
    altitude, 
    vz,
    ]
```

- Which are expressed as m/s^2, rad/s, meters, and m/s 
- Vertical velocity was added to support the altitude prediction between   barometer readings. 
- This means that vertical velocity will not be displayed at all 



## Process Model
The current process model process was intended to predict  

```bash
altitude_next = altitude_current + vertical_velocity * dt
vertical_velocity_next = vertical_velocity
angular_rate_next = angular_rate_current
acceleration_next = acceleration_current
```
- This model is assuming that the angular rate, acceleration, and vertical velocity remains constant.
- Altitude follows constant vertical velocity.
- dt is the time between the measurements 

## Measurement Models
How each sensor was contributed to the filter was by:
- Accounting both IMU's acceleration and angular rate.
- Taking gyro's independent meaures on angular rate.
- Barometers altitude input.
- Reduce as much noise measurements to give non noisy measurements more prominance.

## Saturation Handling
- Implemented a saturation flag from low_g_saturated to decide when to flag it.
- it skips flagged low-g acceleration while keeping it's gyro measurements
- Then accepts high-g acceleration when it's available.
- Then it returns to low-g when the saturation is cleared off. 

## Assumptions and Limitations 
- The assumptions currently are that sensor are alinged, assuming that the shared clock's measurement axe are aligned.
- Sensor baises are not estimated or removed. 


## Incomplete & If I had more time + Reflection
Currently, the biggest gaps in my file would be (from incomplete code):
- Not having the plots implemented 
- Kalman Filter Algorithm not being fully implemented 
    - Update function skeleton code 
    - Build noise function skeleton code
    - Predict function partial code
- Not producing estimates at 100Hz 
- The estimate not being put out into a csv
- Not comparing development estimates against the ground truth and reporting errors
- Not running the filter on a separate test flight. 

If I had more time given to me, I would finish:
- Implementing the Kalman Filter functions:
    - Finishing the update, predict, build_noise function
- Start the plot function algorithm 

The filter will most likely struggle during rapid changes in acceleration and angular rate because the prediction model assumes they remain constant 

