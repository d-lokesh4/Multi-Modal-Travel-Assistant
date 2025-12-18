"""Tools for fetching weather, images, and city information."""
import requests
from datetime import datetime
from typing import List, Dict
from google import genai
from google.genai import types
import os
import base64
import io

# Vector store: Pre-populated knowledge base for 3 cities
CITY_DATABASE = {
    "paris": {
        "summary": "Paris, the capital of France, is renowned for its art, fashion, gastronomy, and culture. Famous landmarks include the Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, and Champs-Élysées. The city is known as the 'City of Light' and offers world-class cuisine, charming cafes, and romantic Seine River views.",
        "country": "France",
        "latitude": 48.8566,
        "longitude": 2.3522
    },
    "tokyo": {
        "summary": "Tokyo, Japan's capital, blends traditional and modern life. It features ancient temples, imperial palaces, and cutting-edge technology. Famous areas include Shibuya, Shinjuku, Asakusa's Senso-ji Temple, and the Imperial Palace. The city is known for its efficient public transport, incredible food scene, and unique pop culture.",
        "country": "Japan",
        "latitude": 35.6762,
        "longitude": 139.6503
    },
    "new york": {
        "summary": "New York City, often called 'The Big Apple', is a global center of culture, finance, and entertainment. Iconic landmarks include the Statue of Liberty, Central Park, Times Square, and the Empire State Building. The city offers world-class museums, Broadway shows, diverse neighborhoods, and exceptional dining from around the world.",
        "country": "USA",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
}


def check_vector_store(city: str) -> dict:
    """Check if city exists in our pre-populated vector store."""
    city_lower = city.lower().strip()
    if city_lower in CITY_DATABASE:
        return {
            "found": True,
            "data": CITY_DATABASE[city_lower]
        }
    return {"found": False, "data": None}


def search_city_info(city: str) -> str:
    """Search for city information using Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"{city} is a fascinating destination. To get detailed AI-generated summaries, please add your GEMINI_API_KEY to the .env file."
    
    prompt = f"""Provide a comprehensive 3-4 sentence summary about {city} as a travel destination. 
    Include information about famous landmarks, culture, cuisine, and what makes it special. 
    Be informative and engaging."""
    
    # Try multiple Gemini models in order of preference
    models_to_try = ['gemini-3-flash-preview', 'gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.5-pro']
    
    for model_name in models_to_try:
        try:
            print(f"Trying {model_name}...")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            print(f"✓ Successfully fetched summary using {model_name}")
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            print(f"{model_name} failed: {error_msg[:100]}...")
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"Quota exceeded for {model_name}, trying next model...")
                continue
            elif "404" in error_msg or "NOT_FOUND" in error_msg:
                print(f"Model {model_name} not found, trying next...")
                continue
            else:
                continue
    
    # Final fallback - always return a valid string
    print(f"All Gemini models failed, using generic fallback for {city}")
    return f"{city} is a vibrant city with rich culture, fascinating history, and world-class attractions. It offers visitors unique experiences through its landmarks, cuisine, and local traditions that make it a must-visit destination."


def get_weather_forecast(latitude: float, longitude: float) -> List[Dict]:
    """Fetch weather forecast from Tomorrow.io API."""
    tomorrow_api_key = os.getenv("TOMORROW_API_KEY")
    
    if not tomorrow_api_key:
        print("✗ Tomorrow.io API key not found")
        return [{"date": f"2025-12-{12+i}", "temp_max": 20+i, "temp_min": 10+i, "precipitation": 0} for i in range(7)]
    
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": f"{latitude},{longitude}",
        "timesteps": "1d",
        "units": "metric",
        "apikey": tomorrow_api_key
    }
    
    try:
        print(f"Fetching weather from Tomorrow.io for coordinates: ({latitude}, {longitude})")
        response = requests.get(url, params=params, timeout=30)
        print(f"Tomorrow.io API status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        # Format the forecast data
        forecast = []
        timelines = data.get("timelines", {}).get("daily", [])
        
        print(f"Got {len(timelines)} days of weather data from Tomorrow.io")
        
        for i, day in enumerate(timelines[:7]):
            values = day.get("values", {})
            date = day.get("time", "")[:10]  # Extract YYYY-MM-DD
            
            forecast.append({
                "date": date,
                "temp_max": round(values.get("temperatureMax", 20), 1),
                "temp_min": round(values.get("temperatureMin", 10), 1),
                "precipitation": round(values.get("precipitationSum", 0), 1)
            })
        
        print(f"✓ Successfully fetched {len(forecast)} days of weather forecast from Tomorrow.io")
        return forecast
    except requests.exceptions.Timeout as e:
        print(f"✗ Tomorrow.io API timeout after 30s: {e}")
        return [{"date": f"2025-12-{12+i}", "temp_max": 20+i, "temp_min": 10+i, "precipitation": 0} for i in range(7)]
    except requests.exceptions.RequestException as e:
        print(f"✗ Tomorrow.io API request error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return [{"date": f"2025-12-{12+i}", "temp_max": 20+i, "temp_min": 10+i, "precipitation": 0} for i in range(7)]
    except Exception as e:
        print(f"✗ Unexpected error fetching weather: {type(e).__name__}: {e}")
        return [{"date": f"2025-12-{12+i}", "temp_max": 20+i, "temp_min": 10+i, "precipitation": 0} for i in range(7)]


def generate_city_images(city: str) -> List[str]:
    """Fetch real photos of the city using Pexels API."""
    try:
        pexels_key = os.getenv("PEXELS_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Generate better search queries using Gemini if available
        search_terms = [f"{city} landmark", f"{city} cityscape", f"{city} architecture", f"{city} street"]
        
        if gemini_key:
            models_to_try = ['gemini-3-flash-preview', 'gemini-1.5-flash', 'gemini-1.5-flash-8b']
            for model_name in models_to_try:
                try:
                    client = genai.Client(api_key=gemini_key)
                    prompt = f"List 4 famous landmarks or iconic places in {city}, separated by commas. Just the names."
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    landmarks = [term.strip() for term in response.text.split(',')[:4]]
                    if len(landmarks) == 4:
                        search_terms = [f"{city} {landmark}" for landmark in landmarks]
                        print(f"✓ Generated search terms using {model_name}")
                        break
                except Exception as e:
                    print(f"Gemini ({model_name}) search term generation failed: {str(e)[:80]}...")
                    continue
        
        images = []
        
        # Try Pexels API first (high-quality real photos)
        if pexels_key and pexels_key != "your-pexels-api-key-here":
            try:
                for search_term in search_terms:
                    try:
                        url = "https://api.pexels.com/v1/search"
                        headers = {"Authorization": pexels_key}
                        params = {"query": search_term, "per_page": 1, "orientation": "landscape"}
                        response = requests.get(url, headers=headers, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("photos") and len(data["photos"]) > 0:
                                photo_url = data["photos"][0]["src"]["large"]
                                images.append(photo_url)
                                print(f"✓ Found Pexels photo for: {search_term}")
                    except Exception as e:
                        print(f"Error fetching Pexels photo for '{search_term}': {e}")
                
                if len(images) >= 4:
                    return images[:4]
            except Exception as e:
                print(f"Pexels API error: {e}")
        

        
    except Exception as e:
        print(f"Error generating images: {e}")
        import random
        img_ids = [random.randint(100, 999) for _ in range(4)]
        return [
            f"https://picsum.photos/800/600?random={img_ids[0]}",
            f"https://picsum.photos/800/600?random={img_ids[1]}",
            f"https://picsum.photos/800/600?random={img_ids[2]}",
            f"https://picsum.photos/800/600?random={img_ids[3]}"
        ]


def get_city_coordinates(city: str) -> tuple:
    """Get coordinates for a city. Returns (latitude, longitude)."""
    # Check database first
    city_data = check_vector_store(city)
    if city_data["found"]:
        data = city_data["data"]
        return (data["latitude"], data["longitude"])
    
    # For cities not in database, use Open-Meteo geocoding with better filtering
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city, "count": 10, "language": "en", "format": "json"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results"):
            results = data["results"]
            
            # First, filter for exact name matches (case-insensitive)
            city_lower = city.lower().strip()
            exact_matches = [r for r in results if r.get('name', '').lower() == city_lower]
            
            # If we have exact matches, use only those
            if exact_matches:
                results = exact_matches
                print(f"Found {len(exact_matches)} exact match(es) for '{city}'")
            
            # Known tourist regions/states that should be prioritized (for disambiguating cities)
            tourist_regions = [
                'Himachal Pradesh', 'Uttarakhand', 'Goa', 'Kerala', 'Rajasthan',
                'Kashmir', 'Sikkim', 'Meghalaya', 'Bali', 'Tuscany', 'Provence',
                'Bavaria', 'Tyrol', 'Queensland', 'California', 'Hawaii'
            ]
            
            # Prioritize results by feature_code: PPLC (capital) > PPLA (state capital) > PPLA2 > PPL
            priority_codes = ['PPLC', 'PPLA', 'PPLA2', 'PPLA3', 'PPL']
            
            # For each priority code, check tourist regions first, then by population
            for code in priority_codes:
                code_matches = [r for r in results if r.get('feature_code') == code]
                if code_matches:
                    # First, prioritize known tourist regions
                    tourist_matches = [r for r in code_matches if r.get('admin1', '') in tourist_regions]
                    if tourist_matches:
                        # Among tourist regions, prefer higher admin level (PPLA > PPL)
                        tourist_matches.sort(key=lambda x: x.get('population', 0), reverse=True)
                        result = tourist_matches[0]
                        print(f"✓ Found {city} (tourist destination): {result.get('name')}, {result.get('admin1', '')}, {result.get('country')} ({result['latitude']}, {result['longitude']}) - Feature: {code}")
                        return (result["latitude"], result["longitude"])
                    
                    # Otherwise, use highest population for this feature code
                    code_matches.sort(key=lambda x: x.get('population', 0), reverse=True)
                    result = code_matches[0]
                    print(f"✓ Found {city}: {result.get('name')}, {result.get('admin1', '')}, {result.get('country')} ({result['latitude']}, {result['longitude']}) - Feature: {code}, Pop: {result.get('population', 0):,}")
                    return (result["latitude"], result["longitude"])
            
            # If no priority match, use highest population
            populated_results = [r for r in results if r.get('population', 0) > 0]
            if populated_results:
                populated_results.sort(key=lambda x: x.get('population', 0), reverse=True)
                result = populated_results[0]
                print(f"✓ Found {city}: {result.get('name')}, {result.get('admin1', '')}, {result.get('country')} ({result['latitude']}, {result['longitude']}) - Pop: {result.get('population', 0):,}")
                return (result["latitude"], result["longitude"])
            
            # Final fallback: use first result
            result = results[0]
            print(f"✓ Using first result for {city}: {result.get('name')}, {result.get('admin1', '')}, {result.get('country')} ({result['latitude']}, {result['longitude']})")
            return (result["latitude"], result["longitude"])
    except Exception as e:
        print(f"✗ Error geocoding city: {e}")
    
    # Default fallback (Paris coordinates)
    print(f"✗ Using default coordinates for {city}")
    return (48.8566, 2.3522)