"""
Google Maps API Integration Router
- Location search and geocoding
- Autocomplete place suggestions
- Distance/direction calculations
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
import os
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/maps", tags=["google-maps"])

# Load Google Maps API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# ===== SCHEMAS =====

class PlaceAutoComplete(BaseModel):
    description: str
    place_id: str
    main_text: str
    secondary_text: Optional[str] = None

class AutoCompleteResponse(BaseModel):
    success: bool
    predictions: List[PlaceAutoComplete] = []
    message: str

class GeocodeResult(BaseModel):
    latitude: float
    longitude: float
    address: str
    place_name: str

class GeocodeResponse(BaseModel):
    success: bool
    location: Optional[GeocodeResult] = None
    message: str

class PlaceDetailsResult(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    business_status: Optional[str] = None

class PlaceDetailsResponse(BaseModel):
    success: bool
    place: Optional[PlaceDetailsResult] = None
    message: str

class DistanceResult(BaseModel):
    distance_km: float
    distance_m: int
    duration_text: str
    duration_seconds: int

class DistanceResponse(BaseModel):
    success: bool
    distance: Optional[DistanceResult] = None
    message: str

# ===== ENDPOINTS =====

@router.get("/search/autocomplete")
async def autocomplete_places(input_text: str) -> AutoCompleteResponse:
    """
    Get autocomplete suggestions for location search
    
    Query Parameters:
    - input_text: Search query (e.g., "restaurant", "UNILAG", "Oyo State")
    
    Returns:
    - List of place suggestions with place_id for detailed lookup
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Maps API key not configured"
        )
    
    if not input_text or len(input_text.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    try:
        # Use Google Places Autocomplete API
        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            "input": input_text,
            "key": GOOGLE_MAPS_API_KEY,
            "components": "country:ng",  # Restrict to Nigeria
            "language": "en"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK" and data.get("status") != "ZERO_RESULTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google API error: {data.get('status', 'Unknown')}"
            )
        
        predictions = []
        for pred in data.get("predictions", []):
            predictions.append(PlaceAutoComplete(
                description=pred.get("description", ""),
                place_id=pred.get("place_id", ""),
                main_text=pred.get("main_text", ""),
                secondary_text=pred.get("secondary_text", "")
            ))
        
        return AutoCompleteResponse(
            success=True,
            predictions=predictions,
            message=f"Found {len(predictions)} suggestions"
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Maps service error: {str(e)}"
        )

@router.get("/geocode")
async def geocode_address(address: str) -> GeocodeResponse:
    """
    Convert address/location name to coordinates (latitude, longitude)
    
    Query Parameters:
    - address: Location name or address (e.g., "UNILAG Lagos", "Shoprite Ikeja")
    
    Returns:
    - Latitude, longitude, and formatted address
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Maps API key not configured"
        )
    
    if not address or len(address.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Address must be at least 2 characters"
        )
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": GOOGLE_MAPS_API_KEY,
            "components": "country:NG",  # Restrict to Nigeria
            "language": "en"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "ZERO_RESULTS":
            return GeocodeResponse(
                success=False,
                location=None,
                message="Location not found"
            )
        
        if data.get("status") != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geocoding error: {data.get('status', 'Unknown')}"
            )
        
        result = data["results"][0]
        location = result["geometry"]["location"]
        
        return GeocodeResponse(
            success=True,
            location=GeocodeResult(
                latitude=location["lat"],
                longitude=location["lng"],
                address=result.get("formatted_address", address),
                place_name=result.get("name", address)
            ),
            message="Successfully geocoded location"
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Maps service error: {str(e)}"
        )

@router.get("/place/{place_id}")
async def get_place_details(place_id: str) -> PlaceDetailsResponse:
    """
    Get detailed information about a place using place_id
    
    Path Parameters:
    - place_id: Google Places ID from autocomplete
    
    Returns:
    - Place details: name, address, coordinates, phone, website, rating, etc.
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Maps API key not configured"
        )
    
    if not place_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="place_id is required"
        )
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": GOOGLE_MAPS_API_KEY,
            "language": "en",
            "fields": "name,formatted_address,geometry,formatted_phone_number,website,rating,user_ratings_total,business_status"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Place details error: {data.get('status', 'Unknown')}"
            )
        
        result = data["result"]
        location = result.get("geometry", {}).get("location", {})
        
        return PlaceDetailsResponse(
            success=True,
            place=PlaceDetailsResult(
                name=result.get("name", ""),
                address=result.get("formatted_address", ""),
                latitude=location.get("lat", 0),
                longitude=location.get("lng", 0),
                phone=result.get("formatted_phone_number"),
                website=result.get("website"),
                rating=result.get("rating"),
                user_ratings_total=result.get("user_ratings_total"),
                business_status=result.get("business_status")
            ),
            message="Successfully retrieved place details"
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Maps service error: {str(e)}"
        )

@router.get("/distance")
async def calculate_distance(
    origin: str,
    destination: str,
    mode: str = "driving"
) -> DistanceResponse:
    """
    Calculate distance and travel time between two locations
    
    Query Parameters:
    - origin: Starting location (address or coordinates)
    - destination: Ending location (address or coordinates)
    - mode: Travel mode (driving, walking, transit, bicycling) - default: driving
    
    Returns:
    - Distance in km and meters
    - Travel duration in text format and seconds
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Maps API key not configured"
        )
    
    if not origin or not destination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both origin and destination are required"
        )
    
    valid_modes = ["driving", "walking", "transit", "bicycling"]
    if mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
        )
    
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": GOOGLE_MAPS_API_KEY,
            "language": "en",
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Distance matrix error: {data.get('status', 'Unknown')}"
            )
        
        if not data.get("rows") or not data["rows"][0].get("elements"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not calculate distance between locations"
            )
        
        element = data["rows"][0]["elements"][0]
        
        if element.get("status") != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Route not found: {element.get('status', 'Unknown')}"
            )
        
        distance_data = element.get("distance", {})
        duration_data = element.get("duration", {})
        
        return DistanceResponse(
            success=True,
            distance=DistanceResult(
                distance_km=distance_data.get("value", 0) / 1000,
                distance_m=distance_data.get("value", 0),
                duration_text=duration_data.get("text", ""),
                duration_seconds=duration_data.get("value", 0)
            ),
            message="Successfully calculated distance"
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Maps service error: {str(e)}"
        )

@router.get("/reverse-geocode")
async def reverse_geocode(latitude: float, longitude: float) -> GeocodeResponse:
    """
    Convert coordinates to address (reverse geocoding)
    
    Query Parameters:
    - latitude: Latitude coordinate
    - longitude: Longitude coordinate
    
    Returns:
    - Formatted address and place name
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Maps API key not configured"
        )
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": GOOGLE_MAPS_API_KEY,
            "language": "en"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "ZERO_RESULTS":
            return GeocodeResponse(
                success=False,
                location=None,
                message="No address found for these coordinates"
            )
        
        if data.get("status") != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reverse geocoding error: {data.get('status', 'Unknown')}"
            )
        
        result = data["results"][0]
        
        return GeocodeResponse(
            success=True,
            location=GeocodeResult(
                latitude=latitude,
                longitude=longitude,
                address=result.get("formatted_address", ""),
                place_name=result.get("name", "")
            ),
            message="Successfully reverse geocoded coordinates"
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Maps service error: {str(e)}"
        )
