import streamlit as st

def show_page():
    st.title("About")
    st.write("Welcome to the PubMed Author Explorer! This application is designed to help you explore and analyze the research publications of a specific author on PubMed.")

    # What is the app about?
    st.markdown("## What is the app about?")
    st.write(
        """
        This app provides insights into an author’s research by offering various metrics and visualizations. 
        With this tool, you can explore an overview of an author’s work, conduct network analysis to see 
        co-author relationships, and explore topic clustering of their publications.

        Each section within the app provides detailed information and visual representations to give you a 
        better understanding of the author's research profile.
        """
    )

    # Important Note
    st.markdown("## Important Note")
    st.warning(
        """
        - Ensure that the author's name is entered **accurately**; otherwise, the search may return no results.
        - The app currently **cannot distinguish between authors with the same name**; results may include 
          works by multiple individuals if their names match.
        """
    )

    # How is the data retrieved?
    st.markdown("## How is the data retrieved?")
    st.write(
        """
        The data is retrieved by sending HTTP requests to PubMed's internal API. Each search query is 
        structured to return pages of results in PubMed format, like this:
        """
    )
    st.code("https://pubmed.ncbi.nlm.nih.gov/?term=lastname+firstname&format=pubmed&size=200&page=1", language="text")
    st.write(
        """
        Using this search method, the app gathers data one page at a time, with each page containing a specified 
        number of results. 

        To comply with PubMed’s [usage policies](https://www.ncbi.nlm.nih.gov/home/about/policies/), the app 
        limits requests to a maximum of 3 per second, adding a delay to avoid server blocks. The retrieved 
        data is then parsed and saved as JSON files for efficient use within the app. Read the usage poicies carefully
        before using the app. Using is own risk. 
        """
    )

    st.markdown("## How to Use the App?")
    st.write(
        """
        To get started, enter the author's name in the search bar and click the **Search** button. The app will 
        then retrieve the author's publications from PubMed and display the results in the **Summary** tab. 
        From there, you can navigate to the **Author Network** and **Title Embeddings** tabs to explore 
        co-author relationships and document embeddings, respectively.
        """
    )