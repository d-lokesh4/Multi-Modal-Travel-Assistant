"""State definition for the LangGraph agent."""
from typing import TypedDict, List, Dict, Optional


class TravelState(TypedDict):
    """State for the travel assistant agent."""
    city: str
    in_vector_store: Optional[bool]
    city_summary: str
    weather_forecast: List[Dict]
    image_urls: List[str]
