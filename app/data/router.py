import requests  # type: ignore
from fastapi import APIRouter

from app.data.types import DataOut
from app.data.schemas import DataSchema
from app.database import sessions

nws_url = "https://api.weather.gov"

router = APIRouter()

def celcius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9/5) + 32

async def get_nearby_station(latitude: float, longitude: float) -> str:
    latitude = round(latitude, 4)
    longitude = round(longitude, 4)
    url = f"{nws_url}/points/{latitude},{longitude}"
    response = requests.get(url)
    response.raise_for_status()
    observation_station = response.json()['properties']['observationStations']

    return observation_station

async def get_station_id(observation_stations_url: str) -> str:
    response = requests.get(observation_stations_url)
    response.raise_for_status()
    stations = response.json()['features']
    if not stations:
        raise ValueError("No observation stations found")
    return stations[0]['properties']['stationIdentifier']

async def get_latest_observation(latitude: float, longitude: float, station_id: str) -> tuple[str, str, int, str]:
    observations_url = f"{nws_url}/stations/{station_id}/observations/latest"
    response = requests.get(observations_url)
    response.raise_for_status()
    properties = response.json().get('properties', {})

    temperature = properties.get('temperature', {}).get('value')
    humidity = properties.get('relativeHumidity', {}).get('value')
    # precipitationLastHour is sometimes nested / missing; default to 0
    rainfall = properties.get('precipitationLastHour', {}).get('value', 0) or 0

    alert_url = f"{nws_url}/alerts/active?point={latitude},{longitude}"
    alert_response = requests.get(alert_url)
    alert_response.raise_for_status()
    alerts = alert_response.json().get('features', [])

    # Look for flood-related alert events
    flood_keywords = ('flood', 'flash flood', 'flood watch', 'flood warning', 'flood advisory')
    active_flood_alert = False
    for a in alerts:
        event = a.get('properties', {}).get('event', '') or ''
        if any(k.lower() in event.lower() for k in flood_keywords):
            active_flood_alert = True
            break

    try:
        # rainfall and humidity may be None
        rainfall_val = float(rainfall) if rainfall is not None else 0.0
    except (TypeError, ValueError):
        rainfall_val = 0.0

    try:
        humidity_val = float(humidity) if humidity is not None else 0.0
    except (TypeError, ValueError):
        humidity_val = 0.0

    if active_flood_alert:
        prediction = "High likelihood of flooding (active flood alert present)"
    elif rainfall_val >= 10:
        prediction = "High likelihood of flooding (heavy recent precipitation detected)"
    elif rainfall_val >= 2 or humidity_val >= 90:
        prediction = "Moderate likelihood of flooding"
    else:
        prediction = "Low likelihood of flooding"

    return (temperature, humidity, rainfall, prediction)

# Returns data for the dashboard of the page, such as active flood risks.
@router.get("/data/{latitude}/{longitude}")
async def get_data(
    latitude: float,
    longitude: float
) -> DataOut:

    observation_stations_url: str = await get_nearby_station(latitude, longitude)
    station_id = await get_station_id(observation_stations_url)
    temperature, humidity, rainfall, flood_risk = await get_latest_observation(
        latitude,
        longitude,
        station_id
    )

    temperature = celcius_to_fahrenheit(temperature) # type: ignore

    # Store data in the database
    record = DataSchema(
        rainfall=rainfall,
        temperature=temperature,
        humidity=humidity,
        flood_risk=flood_risk
    )

    sessions.add(record)
    sessions.commit()
    sessions.refresh(record)

    return DataOut.model_validate(record)