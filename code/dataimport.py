#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 07:13:38 2024

@author: blakerice
"""

import requests
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = "LEOModel/data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

# NOAA's F10.7 data URL
NOAA_F10_URL = "https://services.swpc.noaa.gov/json/solar-cycle/f10-7cm-flux-smoothed.json"

# File to save the downloaded data
OUTPUT_FILE = os.path.join(DATA_DIR, "f10_index.json")

def download_data(url, output_file):
    """Download data from a given URL and save it to a specified file."""
    try:
        print(f"Downloading data from {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f"Data successfully saved to {output_file}")
    except requests.RequestException as e:
        print(f"Failed to download data: {e}")

if __name__ == "__main__":
    download_data(NOAA_F10_URL, OUTPUT_FILE)

def parse_and_visualize(file_path):
    """Parse the JSON file and visualize the data."""
    try:
        # Load the JSON data
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Convert to a DataFrame
        df = pd.DataFrame(data)

        # Check for the correct column names and handle accordingly
        if 'time-tag' in df.columns and 'f10.7' in df.columns:
            # Process the time-tag as a datetime object
            df['date'] = pd.to_datetime(df['time-tag'], format='%Y-%m')
            
            # Set 'date' as the index
            df.set_index('date', inplace=True)
            
            # Rename columns for clarity
            df.rename(columns={'f10.7': 'solar_flux', 'smoothed_f10.7': 'smoothed_flux'}, inplace=True)
        else:
            print("Required columns ('time-tag' and 'f10.7') not found in the data.")
            return None

        # Plot the solar flux data
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['solar_flux'], label='F10.7 Solar Flux', color='blue')
        
        # Add rolling average
        df['rolling_flux'] = df['solar_flux'].rolling(window=30).mean()
        plt.plot(df.index, df['rolling_flux'], label='30-Day Rolling Avg', color='orange', linestyle='--')
        
        # Customize the plot
        plt.title('F10.7 Solar Flux Over Time')
        plt.xlabel('Date')
        plt.ylabel('Solar Flux (F10.7)')
        plt.legend()
        plt.grid()
        plt.tight_layout()
        
        # Show the plot
        plt.show()

        return df  # Return DataFrame for further use
    except Exception as e:
        print(f"Error parsing or visualizing data: {e}")
        return None

if __name__ == "__main__":
    # Step 1: Download data
    download_data(NOAA_F10_URL, OUTPUT_FILE)
    
    # Step 2: Parse and visualize
    parse_and_visualize(OUTPUT_FILE)
    
def export_to_csv(df, output_csv):
    """Export the DataFrame to a CSV file."""
    try:
        df.to_csv(output_csv)
        print(f"Data successfully exported to {output_csv}")
    except Exception as e:
        print(f"Error exporting data: {e}")

if __name__ == "__main__":
    # Step 1: Download data
    download_data(NOAA_F10_URL, OUTPUT_FILE)
    
    # Step 2: Parse and visualize
    df = parse_and_visualize(OUTPUT_FILE)
    
    # Step 3: Export data for MATLAB
    if df is not None:
        export_to_csv(df, "data/processed/f10_index_processed.csv")