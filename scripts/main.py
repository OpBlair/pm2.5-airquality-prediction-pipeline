# This script fetches weather data(humidity & temperature) from open-meteo API, for the defined
# coordinates within kampala. The sensor coordinates with varying coordinates, median was used. 

import csv
import os
import urllib.parse
import urllib.request
import json

kampala_locations = {
    "airqo_g5365": (0.326289, 32.538033),  # Namungona
    "aq_g507":     (0.349695, 32.576490),  # Lower Nsooba
    "aq_g5_101":   (0.302489, 32.645624),  # Luzira
    "aq_g5_37":    (0.316930, 32.589951),  # Civic Centre
    "ag_588c81267534": (0.33354, 32.56861)   # Salama Road
}

start_date = "2026-08-01"
end_date = "2026-08-16"

# Master list to store flat record dictionaries
all_data = []

# Loop through each location
for device_name, (lat, lon) in kampala_locations.items():
    print(f"Fetching data for {device_name}...")
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m",
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date
    }
    
    # Use Open-Meteo archive endpoint for historical/past dates
    base_url = "https://archive-api.open-meteo.com/v1/archive?"
    # https://api.open-meteo.com/v1/forecast?
    url = base_url + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
            hourly_data = response_payload.get("hourly", {})
            
            times = hourly_data.get("time", [])
            temperatures = hourly_data.get("temperature_2m", [])
            humidities = hourly_data.get("relative_humidity_2m", [])
            
            print(f" -> Retrieved {len(times)} hourly records for {device_name}")
            
            # Zip the parallel lists together and format as flat dictionary records
            for t, temp, hum in zip(times, temperatures, humidities):
                record = {
                    "device_name": device_name,
                    "latitude": lat,
                    "longitude": lon,
                    "time": t,
                    "temperature_2m": temp,
                    "relative_humidity_2m": hum
                }
                all_data.append(record)
                
    except urllib.error.HTTPError as e:
        error_details = e.read().decode("utf-8")
        print(f"HTTP Error for {device_name}: {e.code} - {e.reason}")
        print(f"Server response details: {error_details}\n")
    except Exception as e:
        print(f"An error occurred for {device_name}: {e}\n")

# Save all combined records into a single CSV file
if all_data:
    output_dir = "dataset"
    os.makedirs(output_dir, exist_ok=True)
    csv_file_path = os.path.join(output_dir, "combined_open_meteo_weather_data.csv")

    # Extract headers from the first record keys
    headers = all_data[0].keys()

    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Successfully saved {len(all_data)} total records to {csv_file_path}")
else:
    print("No data items found to save.")
