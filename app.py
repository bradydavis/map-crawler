
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import math
import requests
import pandas as pd
import openai

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
MAP_TILES_FOLDER = 'map_tiles'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(MAP_TILES_FOLDER):
    os.makedirs(MAP_TILES_FOLDER)

openai.api_key = 'sk-proj-ZWLOyqh1DVmnzqipKxiIT3BlbkFJEGx2Z4wRp7BYqVHnMZgf'  # Add your OpenAI API key here

@app.route('/')
def index():
    return render_template('map-index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    system_prompt = request.form['systemPrompt']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        print(f"File saved to {file_path}")  # Logging
        summaries, image_urls, lat, lon = process_csv(file_path, system_prompt)
        return jsonify({'summaries': summaries, 'image_urls': image_urls})

def process_csv(file_path, system_prompt):
    print("Processing CSV file...")  # Logging
    df = pd.read_csv(file_path)
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        print("CSV does not have the required columns 'Latitude' and 'Longitude'")  # Logging
        return

    zoom_level = 16  # Set your desired zoom level
    summaries = []
    image_urls = []
    for index, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        x_tile, y_tile = lat_lon_to_tile(lat, lon, zoom_level)
        image_url = get_map_tile_url(x_tile, y_tile, zoom_level)
        download_map_tile(x_tile, y_tile, zoom_level, index)
        summary = summarize_image(image_url, system_prompt)
        summaries.append({'index': index, 'summary': summary, 'image_url': image_url, 'lat': lat, 'lon': lon})
        image_urls.append(image_url)
        row['Summary'] = summary
        row['Image_URL'] = image_url

    df['Summary'] = [s['summary'] for s in summaries]
    df['Image_URL'] = image_urls
    df.to_csv(os.path.join(UPLOAD_FOLDER, 'summary.csv'))

    return summaries, image_urls, lat, lon

def lat_lon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    print(f"Converted lat/lon {lat}/{lon} to tiles {x_tile}/{y_tile} at zoom {zoom}")  # Logging
    return x_tile, y_tile

def get_map_tile_url(x_tile, y_tile, zoom):
    access_token = 'pk.eyJ1IjoiYnJhZHlkYXZpcyIsImEiOiJjbHkzaDAyNTIwOGY0MmpwdWY4dGphejBiIn0.pILDooiniqy75LWz5C7yMQ'  # Ensure this is your actual Mapbox access token
    return f'https://api.mapbox.com/v4/mapbox.naip/{zoom}/{x_tile}/{y_tile}@2x.png?access_token={access_token}'

def download_map_tile(x_tile, y_tile, zoom, index):
    url = get_map_tile_url(x_tile, y_tile, zoom)
    response = requests.get(url)
    if response.status_code == 200:
        tile_path = os.path.join(MAP_TILES_FOLDER, f'map_tile_{index}.png')
        with open(tile_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded map tile to {tile_path}")  # Logging
    else:
        print(f"Failed to download tile {x_tile}/{y_tile} at zoom {zoom}, status code: {response.status_code}")  # Logging
        print(f"Response: {response.text}")  # Logging

def summarize_image(image_url, system_prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "You are an assistant designed to identify the presence of {system_prompt} in images. Do you see {system_prompt} in this image? Reply with a Yes or No answer only."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                ],
            }
        ],
        "max_tokens": 300
    }

    print(f"Sending request to OpenAI API for image URL {image_url}...")  # Logging
    response = openai.chat.completions.create(**payload)
    
    description = response.choices[0].message.content
    
    print(f"Received description for image URL {image_url}: {description}")  # Logging
    
    return description

@app.route('/thumbnails', methods=['GET'])
def get_thumbnails():
    thumbnails = []
    descriptions = []
    summary_path = os.path.join(UPLOAD_FOLDER, 'summary.csv')
    if os.path.exists(summary_path):
        df = pd.read_csv(summary_path)
        for index, row in df.iterrows():
            file_name = f'map_tile_{index}.png'
            if file_name in os.listdir(MAP_TILES_FOLDER):
                thumbnails.append(f"/map_tiles/{file_name}")
                descriptions.append(row['Summary'])
    return jsonify({'thumbnails': thumbnails, 'descriptions': descriptions})

@app.route('/map_tiles/<filename>')
def serve_tile(filename):
    return send_from_directory(MAP_TILES_FOLDER, filename)


@app.route('/download_summary')
def download_summary():
    return send_from_directory(UPLOAD_FOLDER, 'summary.csv', as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed port to 5001
