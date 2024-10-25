import streamlit as st
from pubmed_crawler import SinglePubMedSearcher
import os
import json
import pandas as pd
import plotly.express as px
from collections import Counter
import folium
from collections import Counter
from streamlit_folium import st_folium

def show_page(data):
    def get_authors(data):
        authors = []
        for entry in data:
            authors.append(entry['FAU'])
        return authors

    def plot_network(data):
        import networkx as nx
        import plotly.graph_objects as go

        # Get the authors from the data
        authors = get_authors(data)
        # initialize the graph
        G = nx.Graph()
        # construct the graph
        for author_list in authors:
            for author in author_list:
                G.add_node(author)
            for i in range(len(author_list)):
                for j in range(i+1, len(author_list)):
                    G.add_edge(author_list[i], author_list[j])

        communities = nx.algorithms.community.greedy_modularity_communities(G)
        st.write(f"Number of communities: {len(communities)}")

        # Initialize a list to hold center nodes for each community
        center_nodes_groups = []
        center_names_groups = []
        # Loop through each community
        for i, community in enumerate(communities):
            # Create a subgraph for the community
            subgraph = G.subgraph(community)
            
            # Calculate degree centrality for the subgraph
            centrality = nx.degree_centrality(subgraph)
            
            # Get the node with the highest degree centrality in the community
            center_node = max(centrality, key=centrality.get)
            center_nodes_groups.append((i, center_node, centrality[center_node]))  # Store the community index, center node, and its centrality score
            center_names_groups.append(center_node)
        st.write(center_names_groups)

        # modularity
        modularity = nx.algorithms.community.modularity(G, communities)
        st.write(f"Modularity: {modularity}")

        # most centered nodes
        center_nodes = nx.algorithms.centrality.degree_centrality(G)
        center_nodes = sorted(center_nodes.items(), key=lambda x: x[1], reverse=True)

        most_centered_nodes = [node for node, centrality in center_nodes[:10]]
        most_centered_nodes_score = [centrality for node, centrality in center_nodes[:10]]
        df = pd.DataFrame({'Author': most_centered_nodes, 'Centrality Score': most_centered_nodes_score})
        st.write(df)

        # Configure the spring layout
        pos = nx.spring_layout(G, seed=42, k=0.15, iterations=50)

        # Get node degrees for coloring and sizing
        node_degree = [G.degree(n) for n in G.nodes()]
        max_degree = max(node_degree)

        # Normalize node sizes
        node_sizes = [10 + 40 * (deg / max_degree) for deg in node_degree]  # Scale node sizes for better visibility

        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Create node traces
        node_x = []
        node_y = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_degree,  # Use degree for color scaling
                colorscale='Viridis',  # Use a predefined color scale
                colorbar=dict(
                    title='Node Degree',
                    thickness=15,
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2
            ),
            text=[str(node) for node in G.nodes()],  # Add node labels
        )

        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            height=800,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        
        # Adding annotations for center nodes with improved styling
        for node in center_names_groups:  # Assuming center_names_groups is a list of center node names
            if node in G.nodes():
                x, y = pos[node]
                fig.add_annotation(
                    x=x, 
                    y=y, 
                    text=node, 
                    showarrow=True,  # Show arrows pointing to the nodes
                    arrowhead=2,  # Arrowhead style
                    ax=0,  # X offset of the annotation text
                    ay=-10,  # Y offset of the annotation text
                    font=dict(size=15, color='white'),  # Change font color
                    bgcolor='rgba(0, 0, 0, 0.8)',  # Dark background for contrast
                    bordercolor='rgba(255, 255, 255, 0.8)',  # Light border
                    borderwidth=0.5,  # Border width
                    borderpad=2,  # Padding around the text
                    opacity=0.9,  # Opacity of the annotation box
                )

        # Show the plot
        return fig
    with st.spinner('Analyzing Network...'):
        fig_network = plot_network(data)
    st.plotly_chart(fig_network, key = 'network')
