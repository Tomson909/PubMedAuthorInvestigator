import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

def get_authors(data):
    """
    Extracts authors from the given data.
    Args:
        data (list): A list of dictionaries containing author information.
    Returns:
        list: A list of authors.
    """
    authors = []
    for entry in data:
        authors.append(entry['FAU'])
    return authors

def plot_network(data):
    """
    Constructs a network graph from author data and visualizes it.
    Args:
        data (list): A list of dictionaries containing author information.
    Returns:
        go.Figure: A Plotly figure object representing the network graph.
    """
    # Get the authors from the data
    authors = get_authors(data)
    
    # Initialize the graph
    G = nx.Graph()
    
    # Construct the graph by adding edges between authors in the same list
    for author_list in authors:
        for i in range(len(author_list)):
            for j in range(i + 1, len(author_list)):
                G.add_edge(author_list[i], author_list[j])

    # Detect communities within the graph
    communities = list(nx.algorithms.community.greedy_modularity_communities(G))
    
    # Modularity Calculation
    modularity = nx.algorithms.community.modularity(G, communities)
    
    # Create results DataFrame
    results_df = pd.DataFrame({
        "Metric": ["Number of Communities", "Modularity"],
        "Value": [len(communities), modularity]
    }).set_index("Metric")
    
    
    # Centrality calculation
    center_nodes = nx.degree_centrality(G)
    sorted_centrality = sorted(center_nodes.items(), key=lambda x: x[1], reverse=True)[:10]
    most_centered_nodes = [node for node, centrality in sorted_centrality]
    most_centered_nodes_score = [centrality for node, centrality in sorted_centrality]
    
    # Prepare network plot
    pos = nx.spring_layout(G, seed=42, k=0.15, iterations=50)
    node_degree = [G.degree(n) for n in G.nodes()]
    max_degree = max(node_degree)
    node_sizes = [10 + 40 * (deg / max_degree) for deg in node_degree]
    
    # Create edge traces for the network
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
    
    # Create node traces for the network
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
            color=node_degree,  
            colorscale='Viridis',  
            colorbar=dict(
                title='Node Degree',
                thickness=15,
                xanchor='left',
                titleside='right'
            ),
            line_width=2
        ),
        text=[str(node) for node in G.nodes()],
    )
    
    # Create the final figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        height=800,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    )
                )
    
    # Add annotations for center nodes
    for node in most_centered_nodes:
        if node in G.nodes():
            x, y = pos[node]
            fig.add_annotation(
                x=x, y=y, text=node,
                showarrow=True,
                arrowhead=2, ax=0, ay=-10,
                font=dict(size=15, color='white'),
                bgcolor='rgba(0, 0, 0, 0.8)',
                opacity=0.9,
            )
    
    return fig, results_df


def show_page(data):
    st.info('The network analysis may take too long. In case it does not load, try a different author who has fewer colaborators.')
    # make a green box for text, which says that the network analysis is being performed

    with st.spinner("Please wait..."):
        # Display the network plot
        fig_network, results_df = plot_network(data)


    # Add text and explanation to Streamlit
    modularity_explanation = """
    ## Modularity
    Modularity is a measure used in network analysis to evaluate the strength of division of a network into communities or groups. It quantifies how well a network is organized into clusters, where connections (edges) are denser within groups (communities) than between them.
    
    ### Why is Modularity Important?
    - **Community Detection**: High modularity indicates that a network has distinct communities, making it easier to identify groups of nodes (such as authors) that collaborate more closely with each other than with nodes outside their group.
    - **Network Structure Insight**: Understanding the modularity of a network helps reveal its structure and can provide insights into the dynamics and interactions within the network.

    ### How is Modularity Calculated?
    Modularity (Q) is calculated using the following formula:
    """

    st.markdown(modularity_explanation)
    st.dataframe(results_df, use_container_width=True)
    
    # Display the modularity formula
    st.latex(r"""
    Q = \frac{1}{2m} \sum_{i} \left( e_{ii} - \frac{k_i^2}{2m} \right)
    """)
    
    # Continue the explanation after the formula
    st.markdown("""
    Where:
    
    - $$ m $$ is the total number of edges in the network.
    - $$ e_{ii} $$ is the number of edges within community $$ i $$.
    - $$ k_i $$ is the total degree (number of connections) of nodes in community $$ i $$.

    ### Interpretation of Modularity Values
    - **Q = 0**: The network has no community structure; connections are random.
    - **Q > 0**: The network has communities. The higher the value, the stronger the community structure.
    - **0.3 < Q ≤ 0.5**: A moderate community structure.
    - **Q > 0.5**: A strong community structure, indicating well-defined groups.

    ## Community Detection
    The community detection algorithm used in this analysis is the Greedy Modularity Communities algorithm, which is based on maximizing the modularity of the network. It identifies communities by iteratively moving nodes between communities to improve the overall modularity score.
    """)

    st.markdown("""
        ## Understanding Network Plot Below (from `networkx.spring_layout`)
        
        This network plot shows relationships (e.g., co-authorships) in a collaboration network. Here's how to interpret it:
        
        1. **Nodes (Circles)**:
        - Each circle represents a person (e.g., an author).
        - Larger or more prominently colored nodes indicate individuals with more connections.
        
        2. **Edges (Lines)**:
        - Lines show relationships (e.g., collaborations) between nodes.
        - Shorter lines connect closely related individuals or frequent collaborators.
        
        3. **Clusters**:
        - Groups of closely packed nodes represent communities or teams that collaborate frequently.
        - Distant clusters imply less interaction with the core of the network.
        
        4. **Key Figures**:
        - Labeled nodes are central figures with many connections, often the 'center' of the group.
        
        5. **Layout (Spring Layout)**:
        - The `networkx.spring_layout` algorithm places highly connected nodes close together.
        - Peripheral nodes are those with fewer connections to the central network.
        
        This plot reveals collaboration patterns, highlighting key individuals, core groups, and peripheral members in the network.
    """)
    st.plotly_chart(fig_network, use_container_width=True)
