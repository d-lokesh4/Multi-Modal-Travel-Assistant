"""Generate a visualization of the LangGraph topology."""
from agent import create_travel_agent
import os


def generate_graph_visualization():
    """Generate and save the graph visualization."""
    agent = create_travel_agent()
    
    try:
        # Get the graph visualization
        png_data = agent.get_graph().draw_mermaid_png()
        
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_path = os.path.join(project_root, "graph_visualization", "graph.png")
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(png_data)
        
        print(f"✓ Graph visualization saved to {output_path}")
    except Exception as e:
        print(f"Error generating graph: {e}")
        print("Note: You may need to install graphviz: brew install graphviz")
        print("Or run: pip install pygraphviz")


if __name__ == "__main__":
    generate_graph_visualization()
