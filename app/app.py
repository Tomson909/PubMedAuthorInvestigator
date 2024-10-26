import streamlit as st
import os
import json
from pubmed_crawler import SinglePubMedSearcher

# Set the page configuration
st.set_page_config(layout="wide", page_title="My Streamlit App")

st.title('PubMed Author Investigator')

# Tab titles
tabs = ["Summary", "Author Network", "Topic Clustering"]

# Initialize session state variables if they don’t exist
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "Summary"  # Default tab
if 'data' not in st.session_state:
    st.session_state.data = None  # To store paper data

# Create sidebar elements
selected_tab = st.sidebar.selectbox("Select a Tab", tabs, index=tabs.index(st.session_state.selected_tab))
st.session_state.selected_tab = selected_tab  # Store selected tab in session state

# Add text input fields to the sidebar
fname = st.sidebar.text_input('First Name', key='fname')
lname = st.sidebar.text_input('Last Name', key='lname')

def get_paper(dir_name):
    return [os.path.join(dir_name, file_name) for file_name in os.listdir(dir_name)]

def get_number_of_papers(dir_name):
    return len(os.listdir(dir_name))

def get_paper_data(file_names):
    results = []
    for file_name in file_names:
        with open(file_name, 'r') as file:
            data = json.load(file)
            results.append(data)
    return results

def make_zip(data):
    import io
    import zipfile
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        json_file_name = 'info_data.json'
        zf.writestr(json_file_name, json.dumps(data))
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Search button
if st.sidebar.button('Search'):
    with st.spinner('Searching PubMed... And Analyzing'):
        dir_name = SinglePubMedSearcher(f'{lname}, {fname}').search_author()
        st.session_state.name = f'{lname}, {fname}'
        
        # Process files and show progress
        file_names = get_paper(dir_name)
        total_files = len(file_names)
        st.session_state.data = []
        my_bar = st.progress(0)
        
        for i, file_name in enumerate(file_names):
            data = get_paper_data([file_name])
            st.session_state.data.extend(data)
            my_bar.progress((i + 1) / total_files)
        
        my_bar.empty()

    if not st.session_state.data:
        st.markdown(
            """
            <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px;">
                <strong>❗ No data loaded. Please ensure the author name is correct and try again.</strong>
                <br> You can verify on <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank">PubMed</a>.
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with st.sidebar:
        if st.session_state.data:
            st.download_button(
                label="Download Data",
                data=make_zip(st.session_state.data),
                file_name='info_data.zip',
                mime='application/zip'
            )

# Display the selected tab module only if data is available
if st.session_state.data:
    if st.session_state.selected_tab == "Summary":
        import summary
        summary.show_page(st.session_state.data, st.session_state.name)
    elif st.session_state.selected_tab == "Author Network":
        import network
        network.show_page(st.session_state.data)
    elif st.session_state.selected_tab == "Topic Clustering":
        import embedd
        embedd.show_page(st.session_state.data)
else:
    st.write("Please enter the author's name and click 'Search' to load data.")
