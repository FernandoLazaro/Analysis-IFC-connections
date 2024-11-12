#
#
#
#

import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from tkinter import filedialog, Tk

def parse_ifc_file(file_path):
    """Parse the IFC file to extract tags and their relationships."""
    nodes = {}
    edges = []
    pattern = re.compile(r"^#(\d+)=\s*(\w+)\((.*?)\);")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            match = pattern.match(line.strip())
            if match:
                label = f"#{match.group(1)}"
                entity_name = match.group(2)
                nodes[label] = entity_name
                references = re.findall(r"#\d+", match.group(3))
                edges.extend((label, ref) for ref in references)
    
    return nodes, edges

def filter_graph_by_tag(start_tag, nodes, edges):
    """Filter nodes and edges starting from the specified tag."""
    filtered_nodes = {start_tag: nodes[start_tag]}
    filtered_edges = []
    distances = {start_tag: 0}
    queue = [start_tag]
    visited = set(queue)
    
    while queue:
        current = queue.pop(0)
        current_distance = distances[current]
        for edge in edges:
            if edge[0] == current:
                target = edge[1]
                filtered_edges.append(edge)
                if target not in visited:
                    visited.add(target)
                    queue.append(target)
                    filtered_nodes[target] = nodes[target]
                    distances[target] = current_distance + 1
    
    return filtered_nodes, filtered_edges, distances

def create_graph_layout(nodes, edges):
    """Create the graph layout."""
    G = nx.DiGraph()
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, seed=42)  # Use spring layout for better visualization
    return G, pos

def get_fading_color(base_color, distance, max_distance):
    """Calculate faded color based on distance from the start tag."""
    alpha = max(0.3, 1 - (distance / max_distance))
    return to_rgba(base_color, alpha)

def draw_and_save_graph(G, pos, nodes, edges, start_tag, distances):
    """Draw and save the graph."""
    labels = {node: f"{node}\n{entity}" for node, entity in nodes.items()}
    max_distance = max(distances.values()) if distances else 1
    
    plt.figure(figsize=(12, 8))
    for start, end in edges:
        distance = distances.get(end, 0)
        color = get_fading_color("orange" if pos[end][1] > pos[start][1] else "lightgreen", distance, max_distance)
        nx.draw_networkx_edges(G, pos, edgelist=[(start, end)], edge_color=[color], arrows=True, width=2.0)
    
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", edgecolors="black", linewidths=[3.0 if node == start_tag else 0.5 for node in G.nodes()])
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.title(f"IFC File Connections Graph - Starting Tag: {start_tag}")
    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
        print(f"Graph saved to {save_path}")
    plt.show()

def main():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select IFC File", filetypes=[("IFC files", "*.ifc")])

    if file_path and file_path.lower().endswith('.ifc'):
        nodes, edges = parse_ifc_file(file_path)
        start_tag_number = input("Enter the starting tag number (e.g., 24): ").strip()
        start_tag = f"#{start_tag_number}"
        
        if start_tag not in nodes:
            print("The tag does not exist in the file. Please try again.")
            return

        filtered_nodes, filtered_edges, distances = filter_graph_by_tag(start_tag, nodes, edges)
        G, pos = create_graph_layout(filtered_nodes, filtered_edges)
        draw_and_save_graph(G, pos, filtered_nodes, filtered_edges, start_tag, distances)
    else:
        print("Invalid file selected. Please select a valid IFC file.")

if __name__ == "__main__":
    main()

