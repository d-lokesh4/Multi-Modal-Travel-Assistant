# Multi-Modal Travel Assistant

A LangGraph-powered travel assistant that intelligently routes queries and provides comprehensive city information.

## 🏗️ Architecture Overview

This system uses **LangGraph** to create an intelligent agent that decides how to fetch information based on data availability.

### Graph Topology

```
┌─────────────────┐
│ check_knowledge │ ◄── Entry Point
└────────┬────────┘
         │
         ▼
   [Conditional Edge]
    /           \
   /             \
  ▼               ▼
database         web
  │               │
  ▼               ▼
fetch_from_    fetch_from_
database         web
  │               │
  └───────┬───────┘
          ▼
   fetch_weather
          │
          ▼
   fetch_images
          │
          ▼
        [END]
```

### Key Components

1. **State Management** (`state.py`)
   - Defines `TravelState` TypedDict
   - Tracks: city, vector store status, summary, weather, images

2. **Intelligent Routing** (`agent.py`)
   - **check_knowledge**: Determines if city is in vector store
   - **Conditional Edge**: Routes to database OR web search
   - **fetch_weather**: Gets 7-day forecast from Open-Meteo API
   - **fetch_images**: Retrieves city images
   - **Structured Output**: Returns JSON with all data

3. **Tools** (`tools.py`)
   - **Vector Store**: Pre-populated with Paris, Tokyo, New York
   - **Weather API**: Open-Meteo (no API key required)
   - **Image Source**: Unsplash for reliable city images
   - **Geocoding**: Open-Meteo geocoding for coordinates

4. **Frontend** (`app.py`)
   - **Streamlit UI**: Clean, interactive interface
   - **Text Summary**: City description
   - **Line Chart**: Temperature visualization using st.line_chart
   - **Image Gallery**: 4 high-quality city images
   - **JSON Output**: Structured data display

## 📊 The "Switch" (Decision-Making)

The agent demonstrates **intelligent routing** through a conditional edge:

- **Vector Store Path**: If city is in database (Paris/Tokyo/New York)
  - Fast retrieval from pre-populated knowledge base
  - High-quality, curated summaries

- **Web Search Path**: If city is NOT in database
  - Fallback to web search logic
  - Still provides weather and images

This conditional logic is implemented in `should_use_database()` function.

## 🚀 How to Run

### 1. Install Dependencies

```bash
cd source_code
pip install -r requirements.txt
```

### 2. Set Environment Variables

Edit the `.env` file in the `source_code` folder and add your Gemini API key:

```
GEMINI_API_KEY=your-actual-api-key-here
```

**Optional**: Add Pexels API key for higher quality images:
```
PEXELS_API_KEY=your-pexels-api-key
```
Get free Pexels API key from: https://www.pexels.com/api/

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. Generate Graph Visualization

```bash
python generate_graph.py
```

## 📁 Project Structure

```
Location_Guide/
├── source_code/
│   ├── app.py              # Streamlit frontend
│   ├── agent.py            # LangGraph agent (nodes, edges, routing)
│   ├── state.py            # State definition
│   ├── tools.py            # API integrations & vector store
│   ├── generate_graph.py   # Graph visualization generator
│   └── requirements.txt    # Python dependencies
├── graph_visualization/
│   └── graph.png          # LangGraph topology diagram
└── documentation/
    └── README.md          # This file
```

## 🎯 Core Features

✅ **LangGraph Orchestration**: Clear nodes, edges, and state  
✅ **Intelligent Routing**: Conditional edge based on knowledge availability  
✅ **Real Weather Data**: Open-Meteo API (7-day forecast)  
✅ **Image Gallery**: High-quality city images  
✅ **Interactive Visualization**: Line chart for temperature trends  
✅ **Structured Output**: JSON/Pydantic format  
✅ **No Mock APIs**: All real data sources  

## 🧪 Try These Cities

- **In Vector Store**: Paris, Tokyo, New York (fast, detailed)
- **Not in Store**: London, Berlin, Sydney (web search fallback)

## 🛠️ Technical Stack

- **Orchestration**: LangGraph
- **Frontend**: Streamlit
- **Weather**: Open-Meteo API
- **Images**: Unsplash
- **Language**: Python 3.8+

## 📝 Notes

- No API keys required for basic functionality
- Weather data updates in real-time
- Vector store can be expanded with more cities
- Graph visualization requires graphviz (optional)

---

Built with ❤️ using LangGraph and Streamlit
