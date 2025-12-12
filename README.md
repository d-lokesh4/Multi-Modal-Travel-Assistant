# Multi-Modal Travel Assistant

A LangGraph-powered intelligent travel assistant built for the internship assignment.

🌐 **Live Demo**: [https://multi-modal-travel-assistant-m6ecuymzrggxchyzvczpap.streamlit.app/](https://multi-modal-travel-assistant-m6ecuymzrggxchyzvczpap.streamlit.app/)

## 📁 Project Structure

```
Location_Guide/
├── source_code/            # All source code files
│   ├── app.py             # Streamlit frontend
│   ├── agent.py           # LangGraph agent with nodes & edges
│   ├── state.py           # State definition
│   ├── tools.py           # API integrations & vector store
│   ├── generate_graph.py  # Graph visualization generator
│   └── requirements.txt   # Dependencies
├── graph_visualization/    # Graph topology visualization
│   └── graph.png          # LangGraph diagram
└── documentation/          # Project documentation
    └── README.md          # Detailed architecture explanation

```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd source_code
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 3. Try It Out

- **In Database**: Paris, Tokyo, New York
- **Web Search**: Any other city

## ✨ Features Implemented

✅ **LangGraph Orchestration** - Clear nodes, edges, and state management  
✅ **Intelligent Routing** - Conditional edge based on vector store availability  
✅ **Real Weather API** - Open-Meteo (7-day forecast, no API key needed)  
✅ **Image Gallery** - High-quality city images from Unsplash  
✅ **Interactive Visualization** - Line chart showing temperature trends  
✅ **Structured Output** - JSON/Pydantic format with city_summary, weather_forecast, image_urls  
✅ **Streamlit GUI** - Rich, interactive UI (not console output)  

## 📊 Architecture

See [documentation/README.md](documentation/README.md) for detailed architecture explanation and graph topology.

## 🛠️ Tech Stack

- **Orchestration**: LangGraph
- **Frontend**: Streamlit
- **Weather**: Open-Meteo API
- **Images**: Unsplash
- **Language**: Python 3.8+

---

