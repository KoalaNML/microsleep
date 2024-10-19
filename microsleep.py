from Neuropy import NeuroPy
from time import sleep
import numpy as np
import serial

arduinoData=serial.Serial('com5',115200)

neuropy = NeuroPy("COM6", 57600)
neuropy.start()

# Parameters for EEG processing
sampling_rate = 256  # Increase sampling rate to 30 Hz
buffer_size =  256  # Collect 1028 samples before applying FFT
# Frequency bands for EEG (in Hz)
theta_band = (4, 8)
delta_band = (0.5, 4)
beta_band = (13, 30)

# Thresholds for detecting microsleep (adjust these values as needed)
theta_threshold = 5000  # Placeholder value, needs tuning
delta_threshold = 5000  # Placeholder value, needs tuning
beta_threshold = 12000   # Placeholder value, needs tuning

def detect_microsleep(eeg_signal, sampling_rate=256):
    # Apply a window function
    window = np.hanning(len(eeg_signal))
    windowed_signal = eeg_signal * window

    fft_values = np.fft.fft(windowed_signal)
    frequencies = np.fft.fftfreq(len(eeg_signal), 1 / sampling_rate)

    # Get the magnitude of the FFT values
    fft_magnitude = np.abs(fft_values)

    # Isolate the power in different frequency bands
    theta_power = np.sum(fft_magnitude[(frequencies >= theta_band[0]) & (frequencies <= theta_band[1])])
    delta_power = np.sum(fft_magnitude[(frequencies >= delta_band[0]) & (frequencies <= delta_band[1])])
    beta_power = np.sum(fft_magnitude[(frequencies >= beta_band[0]) & (frequencies <= beta_band[1])])

    print(f"Frequencies: {frequencies}")
    print(f"FFT Magnitude: {fft_magnitude}")
    print(f"Theta Power: {theta_power}, Delta Power: {delta_power}, Beta Power: {beta_power}")

    if theta_power > theta_threshold and delta_power > delta_threshold and beta_power < beta_threshold:
        return True
    return False 

try:
    raw_values = []

    while True:
        # Collect raw value from EEG sensor
        raw = neuropy.rawValue
        raw_values.append(raw)
        # Sleep for sampling rate second
        sleep(1/sampling_rate)  # Adjust sleep based on new sampling rate

        # Once we have enough data (buffer_size), detect microsleep
        if len(raw_values) >= buffer_size:
            # Convert the list of raw values to a numpy array
            eeg_signal = np.array(raw_values)

            # Detect microsleep
            if detect_microsleep(eeg_signal, sampling_rate):
                print("Microsleep detected!")
                cmd="ON"
                cmd=cmd+'\r'
                arduinoData.write(cmd.encode())

            # Clear the buffer to start collecting new data
            raw_values = []

finally:
    neuropy.stop()
