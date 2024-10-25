import streamlit as st
import os
import json
from pubmed_crawler import SinglePubMedSearcher
import time  # To simulate delay for loading

# Set the page configuration
st.set_page_config(layout="wide", page_title="My Streamlit App")

st.title('PubMed Author Investigator')

# Tab titles
tabs = ["Summary", "Author Network", "Topic Clustering"]

# Initialize session state variables
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "Summary"  # Default tab
if 'data' not in st.session_state:
    st.session_state.data = None  # To store paper data

# Create sidebar elements
selected_tab = st.sidebar.selectbox("Select a Tab", tabs, index=tabs.index(st.session_state.selected_tab))

# Update session state with the selected tab
st.session_state.selected_tab = selected_tab

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
    # Create a BytesIO object to hold the zip file in memory
    zip_buffer = io.BytesIO()
    
    # Create a zip file in memory
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Save the data as a JSON file in the zip
        json_file_name = 'info_data.json'
        zf.writestr(json_file_name, json.dumps(data))
    
    # Move the buffer's cursor to the beginning
    zip_buffer.seek(0)
    
    return zip_buffer.getvalue()


# Search button
if st.sidebar.button('Search'):
    with st.spinner('Searching PubMed... And Analyzing'):  # Show a spinner during the search        
        # Query the PubMed
        dir_name = SinglePubMedSearcher(f'{lname}, {fname}').search_author()
        st.session_state.name = f'{lname}, {fname}'
        # Simulate a loading bar for additional processing
        file_names = get_paper(dir_name)
        my_bar = st.progress(0)  # Initialize a progress bar

        # Loading data with a simulated delay
        total_files = len(file_names)
        st.session_state.data = []
        
        for i, file_name in enumerate(file_names):
            # Simulate file loading delay
            data = get_paper_data([file_name])
            print('-----------')
            print(data)
            st.session_state.data.extend(data)  # Add loaded data to session state
            
            # Update the progress bar
            my_bar.progress((i + 1) / total_files)  # Update progress percentage


    if len(st.session_state.data) == 0:
        st.markdown(
            """
            <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px;">
                <strong>❗ Please enter the author's name and click 'Search' to load data.</strong>
                <br> Make sure you have entered the correct name. For double-checking, go to 
                <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank">PubMed</a> 
                and search the author's name. If no results were returned, try a different author.
            </div>
            """, 
            unsafe_allow_html=True
        )
    
with st.sidebar:
    st.download_button(
        label="Download Data",
        data=make_zip(data),  # Pass your actual data here
        file_name='info_data.zip',    # The name of the downloaded zip file
        mime='application/zip',        # MIME type for zip files
        key='download-data'
    )

# Import and display the selected page module only if data is available
if 'data' in st.session_state and len(st.session_state.data) > 0:
    if st.session_state.selected_tab == "Summary":
        import summary
        summary.show_page(st.session_state.data, st.session_state.name)
    elif st.session_state.selected_tab == "Author Network":
        import network
        network.show_page(st.session_state.data)
    else:  # "Topic Clustering"
        import embedd
        embedd.show_page(st.session_state.data)
else:
    st.write("Please enter the author's name and click 'Search' to load data.")


