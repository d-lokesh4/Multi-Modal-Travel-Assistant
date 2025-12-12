"""LangGraph agent with intelligent routing."""
from langgraph.graph import StateGraph, END
from state import TravelState
from tools import (
    check_vector_store,
    search_city_info,
    get_weather_forecast,
    generate_city_images,
    get_city_coordinates
)


def check_knowledge_node(state: TravelState) -> TravelState:
    """Node: Check if city exists in vector store."""
    city = state["city"]
    result = check_vector_store(city)
    state["in_vector_store"] = result["found"]
    return state


def fetch_from_database_node(state: TravelState) -> TravelState:
    """Node: Fetch city information from internal database."""
    city = state["city"]
    result = check_vector_store(city)
    state["city_summary"] = result["data"]["summary"]
    return state


def fetch_from_web_node(state: TravelState) -> TravelState:
    """Node: Fetch city information from web search."""
    city = state["city"]
    state["city_summary"] = search_city_info(city)
    return state


def fetch_weather_node(state: TravelState) -> TravelState:
    """Node: Fetch weather forecast."""
    city = state["city"]
    lat, lon = get_city_coordinates(city)
    state["weather_forecast"] = get_weather_forecast(lat, lon)
    return state


def fetch_images_node(state: TravelState) -> TravelState:
    """Node: Generate/fetch images of the city."""
    city = state["city"]
    state["image_urls"] = generate_city_images(city)
    return state


def should_use_database(state: TravelState) -> str:
    """Conditional edge: Route based on vector store availability."""
    if state.get("in_vector_store", False):
        return "database"
    else:
        return "web"


def create_travel_agent():
    """Create and compile the LangGraph agent."""
    # Initialize the graph
    workflow = StateGraph(TravelState)
    
    # Add nodes
    workflow.add_node("check_knowledge", check_knowledge_node)
    workflow.add_node("fetch_from_database", fetch_from_database_node)
    workflow.add_node("fetch_from_web", fetch_from_web_node)
    workflow.add_node("fetch_weather", fetch_weather_node)
    workflow.add_node("fetch_images", fetch_images_node)
    
    # Set entry point
    workflow.set_entry_point("check_knowledge")
    
    # Add conditional edge for intelligent routing
    workflow.add_conditional_edges(
        "check_knowledge",
        should_use_database,
        {
            "database": "fetch_from_database",
            "web": "fetch_from_web"
        }
    )
    
    # Both paths converge to weather fetching
    workflow.add_edge("fetch_from_database", "fetch_weather")
    workflow.add_edge("fetch_from_web", "fetch_weather")
    
    # Then fetch images
    workflow.add_edge("fetch_weather", "fetch_images")
    
    # End after images
    workflow.add_edge("fetch_images", END)
    
    # Compile the graph
    return workflow.compile()


def run_agent(city: str) -> TravelState:
    """Run the travel agent for a given city."""
    agent = create_travel_agent()
    
    # Initial state
    initial_state = {
        "city": city,
        "in_vector_store": None,
        "city_summary": "",
        "weather_forecast": [],
        "image_urls": []
    }
    
    # Execute the graph
    result = agent.invoke(initial_state)
    return result
