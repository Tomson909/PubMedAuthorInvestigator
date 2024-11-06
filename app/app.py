import streamlit as st
import os
import json
from pubmed_crawler import SinglePubMedSearcher

# Set the page configuration for layout and title in the Streamlit app
st.set_page_config(layout="wide", page_title="My Streamlit App")

# Display the main title of the application
st.title('PubMed Author Investigator')

# Define the titles for each of the application tabs
tabs = ["About", "Summary", "Author Network", "Topic Clustering"]

# Initialize session state variables if they don’t exist
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "About"  # Default tab on load
if 'data' not in st.session_state:
    st.session_state.data = None  # Variable to store paper data

# Create sidebar elements for user navigation
# Create a selectbox in the sidebar for tab selection
selected_tab = st.sidebar.selectbox("Select a Tab", tabs, index=tabs.index(st.session_state.selected_tab))
st.session_state.selected_tab = selected_tab  # Store selected tab in session state for persistence

# Add text input fields in the sidebar to input author details
fname = st.sidebar.text_input('First Name', key='fname')
lname = st.sidebar.text_input('Last Name', key='lname')

# remove leading and trailing whitespaces
fname = fname.strip()
lname = lname.strip()


# Function to retrieve list of file paths in the specified directory
def get_paper(dir_name):
    """
    Retrieves the list of file paths within a given directory.

    Args:
        dir_name (str): Directory containing files.

    Returns:
        list: List of file paths in the directory.
    """
    return [os.path.join(dir_name, file_name) for file_name in os.listdir(dir_name)]


# Function to get the number of files in a specified directory
def get_number_of_papers(dir_name):
    """
    Counts the number of files in a directory.

    Args:
        dir_name (str): Directory to count files in.

    Returns:
        int: Number of files in the directory.
    """
    return len(os.listdir(dir_name))


# Function to read and load data from a list of JSON files
def get_paper_data(file_names):
    """
    Reads JSON files and appends their data into a list.

    Args:
        file_names (list): List of JSON file paths.

    Returns:
        list: List containing JSON data from each file.
    """
    results = []
    for file_name in file_names:
        with open(file_name, 'r') as file:
            data = json.load(file)
            results.append(data)
    return results


# Function to package data into a downloadable ZIP archive
def make_zip(data):
    """
    Packages a list of JSON data into a ZIP file for download.

    Args:
        data (list): JSON serializable data to be archived.

    Returns:
        bytes: In-memory ZIP file data ready for download.
    """
    import io
    import zipfile
    zip_buffer = io.BytesIO()  # Create an in-memory buffer for the ZIP file
    
    # Add JSON data as a file to the ZIP archive
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        json_file_name = 'info_data.json'
        zf.writestr(json_file_name, json.dumps(data))
    
    zip_buffer.seek(0)  # Move buffer cursor to the beginning
    return zip_buffer.getvalue()


# Search and retrieve author data upon button click
if st.sidebar.button('Search - Update'):
    with st.spinner('Searching PubMed... And Analyzing'):
        # Use PubMed searcher to find specified author data
        dir_name = SinglePubMedSearcher(f'{lname}, {fname}').search_author()
        st.session_state.name = f'{lname}, {fname}'  # Store author name in session state
        
        # Retrieve list of files and initialize progress bar
        file_names = get_paper(dir_name)
        total_files = len(file_names)
        st.session_state.data = []  # Initialize session state data list
        my_bar = st.progress(0)  # Progress bar for file loading
        
        # Load data from each file and update the progress bar
        for i, file_name in enumerate(file_names):
            data = get_paper_data([file_name])
            st.session_state.data.extend(data)
            my_bar.progress((i + 1) / total_files)
        
        my_bar.empty()  # Clear the progress bar when loading is complete

        st.session_state.selected_tab = "Summary"
    # Display an error message if no data is loaded
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
    
    # Provide a download button for the data in the sidebar if data is loaded
    with st.sidebar:
        if st.session_state.data:
            st.download_button(
                label="Download Data",
                data=make_zip(st.session_state.data),
                file_name='data.zip',
                mime='application/zip'
            )

# about page is not dependent on data.
if st.session_state.selected_tab == "About":
    import about
    about.show_page()

# Display the selected tab module only if data is available
if st.session_state.data:
    st.write('Read the about page for more details about the app and the data retrieval process.')
    if st.session_state.selected_tab == "Summary":
        import summary
        summary.show_page(st.session_state.data, st.session_state.name)
    elif st.session_state.selected_tab == "Author Network":
        import network
        network.show_page(st.session_state.data)
    elif st.session_state.selected_tab == "Topic Clustering":
        import embedd
        embedd.show_page(st.session_state.data, st.session_state.name)

# Display a message prompting users to enter an author name and search if no data is loaded
else:
    st.write("Please enter the author's name and click 'Search' to load data.")

# Footer information for the app
st.markdown("---")  # Adds a simple horizontal line
st.write("**App Version:** 1.0.0  |  **Developer:** Tom Ruge")
st.write("Contact: www.linkedin.com/in/tom-ruge-990660291")
