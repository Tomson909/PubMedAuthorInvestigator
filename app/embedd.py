import streamlit as st
import pandas as pd
import numpy as np
from pubmed_crawler import SinglePubMedSearcher
import os
import json
import pandas as pd
import plotly.express as px
from collections import Counter
import torch
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch
import numpy as np
from pprint import pprint
import plotly.express as px


def plot_embeddings_with_plotly(embeddings, urls):
    # Create a DataFrame to hold the embedding data and corresponding document info
    df = pd.DataFrame({
        'PCA Component 1': embeddings[:, 0],
        'PCA Component 2': embeddings[:, 1],
        'URL': urls
    })

    # Create a scatter plot using Plotly Express
    fig = px.scatter(
        df, 
        x='PCA Component 1', 
        y='PCA Component 2', 
        title='BioBERT Document Embeddings with Clusters',
        hover_data={'URL': True},  # Show URL on hover
        labels={'PCA Component 1': 'PCA Component 1', 'PCA Component 2': 'PCA Component 2'},
        template='plotly_white'
    )
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

    # Show the interactive plot in Streamlit
    return fig


def get_abstracts_pmid(paper_data, pubmed_endpoint):
    abstracts = []
    pmids = []
    for data in paper_data:
        try:
            abstracts.extend(data['TI'])
            #print(list(data['PMID'])[0])
            pmids.append(pubmed_endpoint + list(data['PMID'])[0] + '/')
        except KeyError:
            pass
    return abstracts, pmids

# Function to get embeddings from a list of documents
def get_embeddings(documents, tokenizer, model):
    all_embeddings = []
    for i in range(0, len(documents), 8):  # Process in batches of 8 (or other sizes)
        inputs = tokenizer(documents[i:i+8], return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        # Mean pooling instead of just the [CLS] token
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
        all_embeddings.extend(embeddings)
    return np.array(all_embeddings)

def show_page(data):
    with st.spinner('Create Embeddings...'):
        # Check if embeddings have already been calculated
        if 'embeddings' not in st.session_state:
            pubmed_endpoint = 'https://pubmed.ncbi.nlm.nih.gov/'
            
            # Load the BioBERT model and tokenizer
            model_name = "dmis-lab/biobert-v1.1"  # BioBERT model
            tokenizer = AutoTokenizer.from_pretrained(model_name)  # Load the tokenizer
            model = AutoModel.from_pretrained(model_name)  # Load the model

            titles, urls = get_abstracts_pmid(data, pubmed_endpoint)
            embeddings = get_embeddings(titles, tokenizer, model)

            # Dimensionality reduction using PCA for visualization
            pca = PCA(n_components=2)
            reduced_embeddings = pca.fit_transform(embeddings)

            # Store the results in session state
            st.session_state.embeddings = reduced_embeddings
            st.session_state.urls = urls  # Store URLs in session state

            # Plot the embeddings with Plotly
            fig = plot_embeddings_with_plotly(st.session_state.embeddings, st.session_state.urls)
            st.session_state.fig = fig

    # Display the Plotly figure
    st.plotly_chart(st.session_state.fig)
    # Selectbox for viewing documents
    selected_index = st.selectbox("Select a paper to open:", range(len(st.session_state.urls)), format_func=lambda x: f"Document {x + 1}")
    
    # Update the selected URL based on the index selected
    if selected_index is not None:
        st.session_state.selected_url = st.session_state.urls[selected_index]

    # Display the selected document link
    if 'selected_url' in st.session_state:
        st.write(f"You can view the paper [here]({st.session_state.selected_url}).")

