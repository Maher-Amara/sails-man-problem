import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import os

def visualize_street_network(graph: nx.MultiDiGraph) -> None:
    """
    Visualize just the street network without points of interest
    
    Args:
        graph: NetworkX graph of the street network
    """
    print("Generating street network visualization...")
    
    # Create output directory if it doesn't exist
    os.makedirs('out', exist_ok=True)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plot the street network
    ox.plot_graph(
        graph,
        ax=ax,
        node_color='#336699',      # Blue nodes
        node_size=30,
        node_alpha=0.7,
        edge_color='#999999',      # Gray edges
        edge_linewidth=1,
        edge_alpha=0.5,
        bgcolor='white',
        show=False
    )
    
    # Add title
    ax.set_title('Street Network', fontsize=16, pad=20)
    
    # Save the plot to the out directory
    plt.savefig('out/street_network.png',
                dpi=300,
                bbox_inches='tight',
                pad_inches=0.5,
                facecolor='white')
    print("Visualization saved as 'out/street_network.png'")
    
    # Close the figure to free memory
    plt.close()
