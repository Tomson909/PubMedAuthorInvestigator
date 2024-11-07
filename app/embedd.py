import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.decomposition import PCA

"""
Warning: Running this code in a docker enviroment leads to following warning:
    Examining the path of torch.classes raised: Tried to instantiate class '__path__._path', but it does not exist! Ensure that it is registered via torch::class_

I was not able to fix this problem. The code works fine in a local enviroment. But the functionality is not affected by this warning.
"""

# Function to plot embeddings using Plotly
def plot_embeddings_with_plotly(embeddings, urls):
    """
    Plots a 2D scatter plot of embeddings using Plotly, with annotations and URL hover info.

    Parameters:
    - embeddings: numpy array of reduced embeddings for each document
    - urls: list of URLs corresponding to each document

    Returns:
    - fig: Plotly figure object for the scatter plot
    """
    # Create a DataFrame to hold embeddings and document URLs
    df = pd.DataFrame({
        'PCA Component 1': embeddings[:, 0],
        'PCA Component 2': embeddings[:, 1],
        'URL': urls
    })

    # Create scatter plot of embeddings with Plotly
    fig = px.scatter(
        df, 
        x='PCA Component 1', 
        y='PCA Component 2', 
        hover_data={'URL': True},  # Show URL on hover
        labels={'PCA Component 1': 'PCA Component 1', 'PCA Component 2': 'PCA Component 2'},
        template='plotly_white'
    )
    
    # Annotate each point with "Doc {number}"
    for i in range(len(df)):
        fig.add_annotation(
            x=df['PCA Component 1'][i],
            y=df['PCA Component 2'][i],
            text=f'Doc {i + 1}',  # Document number starting from 1
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-10
        )

    # Return the figure for display
    return fig

# Function to extract abstracts and PMIDs
def get_abstracts_pmid(paper_data, pubmed_endpoint):
    """
    Extracts abstracts and PubMed IDs (PMIDs) from the paper data.

    Parameters:
    - paper_data: list of dictionaries containing paper details
    - pubmed_endpoint: base URL for PubMed to generate links

    Returns:
    - abstracts: list of abstracts (titles) from papers
    - pmids: list of URLs to access papers on PubMed
    """
    abstracts = []
    pmids = []
    for data in paper_data:
        try:
            # Collect titles and PMIDs for each document
            abstracts.extend(data['TI'])
            pmids.append(pubmed_endpoint + list(data['PMID'])[0] + '/')
        except KeyError:
            pass  # Skip papers without title or PMID
    return abstracts, pmids

# Function to generate embeddings for a list of documents
def get_embeddings(documents, tokenizer, model):
    """
    Generates embeddings for a list of documents using a pre-trained model.

    Parameters:
    - documents: list of text documents to be embedded
    - tokenizer: tokenizer instance for the model
    - model: pre-trained model instance for generating embeddings

    Returns:
    - numpy array of embeddings for each document
    """
    all_embeddings = []
    # Process documents in batches for efficiency
    for i in range(0, len(documents), 8):  # Batch size of 8
        inputs = tokenizer(documents[i:i+8], return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        # Apply mean pooling across tokens for each document
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy() # average pooling for all the output vectors. This is one way to embedd a document.
        all_embeddings.extend(embeddings)
    return np.array(all_embeddings)

# Main function to display the page content
def show_page(data, name):
    """
    Displays the page content, which includes generating embeddings, reducing dimensions, 
    plotting, and adding interactivity.

    Parameters:
    - data: list of dictionaries containing paper details for analysis
    """
    st.info('The embeddings may take too long. In case it does not load, try a different author with less papers.')
    with st.spinner('Create Embeddings...'):
        # To make sure new athors are loaded
        dummy = None
        # Check if embeddings are already in session state
        if 'embeddings' not in st.session_state or dummy != name:
            pubmed_endpoint = 'https://pubmed.ncbi.nlm.nih.gov/'
            
            # Load BioBERT model and tokenizer for biomedical text processing
            model_name = "dmis-lab/biobert-v1.1"
            tokenizer = AutoTokenizer.from_pretrained(model_name)  # Load tokenizer
            model = AutoModel.from_pretrained(model_name)  # Load model

            # Extract titles (abstracts) and URLs for each document
            titles, urls = get_abstracts_pmid(data, pubmed_endpoint)
            # Generate embeddings for the titles
            embeddings = get_embeddings(titles, tokenizer, model)

            # Apply PCA for dimensionality reduction to 2D for visualization
            pca = PCA(n_components=2)
            reduced_embeddings = pca.fit_transform(embeddings)

            # Store results in session state to avoid recalculating
            st.session_state.embeddings = reduced_embeddings
            st.session_state.urls = urls  # Store URLs

            # Plot the embeddings using Plotly
            fig = plot_embeddings_with_plotly(st.session_state.embeddings, st.session_state.urls)
            st.session_state.fig = fig
            dummy = name

    # Markdown description of the application overview
    description = """
    ## Application Overview
    This page is designed to analyze and visualize titles from scientific papers using natural language processing techniques. Here’s what happens when you use the app:

    1. **Embedding Creation**:
    - The app retrieves the titles (abstracts) of the provided papers and converts them into numerical representations called embeddings using a model known as [BioBERT](https://huggingface.co/dmis-lab/biobert-v1.1). This model is particularly effective for biomedical text.
    - Embeddings are calculated in batches for efficiency.

    2. **Dimensionality Reduction**:
    - Once the embeddings are generated, the app applies Principal Component Analysis (PCA) to reduce the high-dimensional embeddings into two dimensions. This allows us to visualize the data easily on a scatter plot.

    3. **Visualization**:
    - The reduced embeddings are displayed as a scatter plot using Plotly. Each point on the plot represents a document, and hovering over a point will show the corresponding URL for the paper.
    - **Points, which are close to each other should deal with more similar topics compared to distant ones**.
    - Annotations for each point are included for easy identification, labeled as "Doc 1," "Doc 2," etc.

    4. **Interactivity**:
    - Users can select a specific document from a dropdown list. Upon selection, a link to view the full paper is provided.
    """

    # Display overview and warnings
    st.write(description)
    st.warning('I am not a domain expert. Therefore it was not possible for me to validate the results. The only thing I did was too ask chatgpt to compare the topics of the papers.')
    
    # Display the scatter plot
    st.plotly_chart(st.session_state.fig, key = 'embedd', use_container_width=True)

    # Dropdown selection to view a specific document
    selected_index = st.selectbox("Select a paper to open:", range(len(st.session_state.urls)), format_func=lambda x: f"Document {x + 1}")
    
    # Update selected URL based on dropdown choice
    if selected_index is not None:
        st.session_state.selected_url = st.session_state.urls[selected_index]

    # Display the selected document link
    if 'selected_url' in st.session_state:
        st.write(f"You can view the paper [here]({st.session_state.selected_url}).")
