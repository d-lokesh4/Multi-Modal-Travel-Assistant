"""Streamlit UI for the Multi-Modal Travel Assistant."""
import streamlit as st
import pandas as pd
from agent import run_agent
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    st.set_page_config(
        page_title="Multi-Modal Travel Assistant",
        page_icon="✈️",
        layout="wide"
    )
    
    st.title("✈️ Multi-Modal Travel Assistant")
    st.markdown("Ask me about any city and I'll provide a comprehensive guide!")
    
    # User input
    city = st.text_input(
        "Enter a city name:",
        placeholder="e.g., Paris, Tokyo, New York, or any other city"
    )
    
    if st.button("Explore City", type="primary"):
        if city:
            with st.spinner(f"Gathering information about {city}..."):
                # Run the LangGraph agent
                result = run_agent(city)
                
                # Display structured output
                display_results(result)
        else:
            st.warning("Please enter a city name.")
    
    # Show example cities
    st.sidebar.header("🗺️ About")
    st.sidebar.info(
        "This assistant uses LangGraph to intelligently route requests:\n\n"
        "- **Vector Store Cities**: Paris, Tokyo, New York\n"
        "- **Other Cities**: Fetched via web search\n\n"
        "Features:\n"
        "- Real-time weather forecast (Tomorrow.io)\n"
        "- City images\n"
        "- Interactive weather charts"
    )
    
    # Show LangGraph visualization
    st.sidebar.header("🔀 LangGraph Workflow")
    graph_path = os.path.join(os.path.dirname(__file__), "..", "graph_visualization", "graph.png")
    if os.path.exists(graph_path):
        st.sidebar.image(graph_path, caption="Agent Workflow", use_container_width=True)
    else:
        st.sidebar.warning("Graph visualization not found")


def display_results(result: dict):
    """Display the structured results from the agent."""
    
    # Section 1: City Summary
    st.header(f"📍 {result['city'].title()}")
    
    if result.get("in_vector_store"):
        st.success("✓ Information retrieved from knowledge base")
    else:
        st.info("🔍 Information retrieved from web search")
    
    st.markdown("### Summary")
    st.write(result["city_summary"])
    
    # Section 2: Weather Forecast
    st.markdown("### 🌤️ Weather Forecast (Next 7 Days)")
    
    if result["weather_forecast"]:
        # Create DataFrame for the chart
        df = pd.DataFrame(result["weather_forecast"])
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_temp_max = df["temp_max"].mean()
            st.metric("Avg High", f"{avg_temp_max:.1f}°C")
        with col2:
            avg_temp_min = df["temp_min"].mean()
            st.metric("Avg Low", f"{avg_temp_min:.1f}°C")
        with col3:
            total_precip = df["precipitation"].sum()
            st.metric("Total Precipitation", f"{total_precip:.1f}mm")
        
        # Line chart for temperature
        chart_data = pd.DataFrame({
            "Date": df["date"],
            "Max Temp (°C)": df["temp_max"],
            "Min Temp (°C)": df["temp_min"]
        })
        chart_data = chart_data.set_index("Date")
        
        st.line_chart(chart_data)
        
        # Detailed forecast table
        with st.expander("View Detailed Forecast"):
            display_df = df.copy()
            display_df.columns = ["Date", "Max Temp (°C)", "Min Temp (°C)", "Precipitation (mm)"]
            st.dataframe(display_df, width="stretch")
    else:
        st.warning("Weather data unavailable")
    
    # Section 3: Image Gallery
    st.markdown("### 🖼️ Image Gallery")
    
    if result["image_urls"]:
        cols = st.columns(2)
        for idx, img_url in enumerate(result["image_urls"]):
            with cols[idx % 2]:
                st.image(img_url, width="stretch")
    else:
        st.warning("Images unavailable")
    
    # Section 4: Raw JSON Output
    with st.expander("📄 View Structured Output (JSON)"):
        # Create clean output
        output = {
            "city_summary": result["city_summary"],
            "weather_forecast": result["weather_forecast"],
            "image_urls": result["image_urls"]
        }
        st.json(output)


if __name__ == "__main__":
    main()
