import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter



def show_page(data, author_name):
    """
    Display an interactive dashboard summarizing research metrics for a specific author.

    Parameters:
        data (list of dict): List of publication data, with each publication as a dictionary.
        author_name (str): Name of the author to analyze and highlight in the dashboard.
    """

    # Helper Functionss

    def get_number_of_unique_authors(data):
        """
        Return the number of unique authors in the provided publication data. The serched author is excluded.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """

        authors = []
        for i in data:
            authors.extend(i['FAU'])
        return len(set(authors)) - 1
    
    def plot_most_collaborated_authors(data):
        """
        Plot the top 10 most collaborated authors based on the provided publication data. The searched author is included to get an idea about the order of magnitude.
        
        parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """
        authors = []
        for i in data:
            authors.extend(i['FAU'])
        # Number of counts for each author
        author_counts = Counter(authors)
        # Get the top 10 authors
        top_authors = author_counts.most_common(10)
        top_author = top_authors[1][0]
        # Create a DataFrame for the top 10 authors
        df = pd.DataFrame(top_authors, columns=['Author', 'Number of Papers']).sort_values('Number of Papers')
        # Plot the top 10 authors using Plotly
        fig = px.bar(df, y='Author', x='Number of Papers')
        # Update the layout and appearance
        fig.update_layout(
            height=600,   # Set the height of the figure
            xaxis_title='Number of Papers',
            yaxis_title='Author',
        )

        return fig, top_author

    def plot_history_published(data):
        """
        Plot the number of papers published each year based on the provided publication data. All papers include date of publication.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """
        dates = []
        for i in data:
            dates.extend(i['DP'])
        # Count the number of papers published in each year
        year_counts = Counter([date.split()[0] for date in dates])
        # Sort the years
        years = sorted(year_counts.keys())
        # Create a dataframe
        df = pd.DataFrame([(year, year_counts[year]) for year in years], columns=['Year', 'Number of Papers'])
        # Plot the data as a bar chart
        fig = px.bar(df, x='Year', y='Number of Papers')
        fig.update_layout(
            height=600,   # Set the height of the figur# bigger font size
        )
        return fig

    def percentage_affiliation(data):
        """
        This returns the percentage of authors who have affiliation in each article. This is calculated by dividing the number of affiliations by the number of authors in the paper. 
        This is done paperwise. If an author appears in many papers, but has only few times affiliation, this will be low.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """
        affiliations = 0
        authors = 0
        for i in data:
            author_names = i['FAU']
            authors += len(author_names)
            for author in author_names:
                try:
                    affiliations += len(i[f'{author}_AD'])
                except KeyError:
                    pass
        return affiliations / authors * 100

    def author_percentage_affiliation(data, author_name):
        """
        This returns the precentage of affiliations of a specific author in the papers. I only use this for the author.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
            author_name (str): Name of the author to analyze and highlight in the dashboard.
        """
        affiliations = 0
        authors = 0
        for i in data:
            if author_name in i['FAU']:
                authors += 1
                try:
                    affiliations += len(i[f'{author_name}_AD'])
                except KeyError:
                    pass
        return affiliations / authors * 100


    def percentage_funding(data):
        """
        This returns how many percent of the papers contain funding information. One paper can also have multiple funding sources.
        
        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """
        counts = 0
        for i in data:
            if 'GR' in i:
                counts += 1

        perc_funding = counts / len(data) * 100

        return perc_funding

    def plot_funding(data):
        """
        Plot the top 10 most frequent funding sources based on the provided publication data.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """

        funders = []
        for i in data:
            if 'GR' in i:
                funders.extend(i['GR'])
                
        # Count occurrences of each funder
        funder_counts = Counter(funders)
        ten_most_common_funders = funder_counts.most_common(10)
        
        # Create a bar chart of the top 10 funding sources
        fig = px.bar(
            pd.DataFrame(ten_most_common_funders, columns=['Funder', 'Number of Papers']).sort_values('Number of Papers'),
            y='Funder', 
            x='Number of Papers'
        )
        fig.update_layout(
            height=600   # Set the height of the figure
        )
        
        # Determine the most frequent funder
        most_freq_funder = funder_counts.most_common(1)[0][0]

        return fig,  most_freq_funder.replace('.', '')



    def plot_affiliation(data, author_name):
        """
        Plot the top 10 most frequent affiliations based on the provided publication data. This gives an idea what institutions are most frequent in the papers.
        This is done for a specific author. But here only used for te author searched for.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
            author_name (str): Name of the author to analyze and highlight in the dashboard.
        """
        affiliations = []
        for i in data:
            try:
                affiliations.extend(i[f'{author_name}_AD'])
            except KeyError:
                pass

        # Count occurrences of each affiliation
        affiliation_counts = Counter(affiliations)
        ten_most_common_affiliations = affiliation_counts.most_common(10)
        
        # Create a bar chart of the top 10 affiliations
        fig = px.bar(pd.DataFrame(ten_most_common_affiliations, columns=['Affiliation', 'Number of Papers']).sort_values('Number of Papers'),
                    y='Affiliation', 
                    x='Number of Papers')
        fig.update_layout(
            height=600   # Set the height of the figure
        )
        # Determine the most frequent affiliation
        most_freq_affiliation = affiliation_counts.most_common(1)[0][0]

        return fig, most_freq_affiliation.replace('.', '')

    def get_most_frequent_last_author(data):
        """
        Return the most frequent last author name based on the provided publication data. Mostly professors or the head of the lab is the last author.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """
        last_authors = []
        for i in data:
            last_authors.append(i['FAU'][-1])
        return Counter(last_authors).most_common(1)[0][0]

    def number_paper(data):
        """
        Return the number of papers has published, containing the authora name.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
        """
        return len(data)

    def author_positions(data, author_name):
        """
        Plot the position of the author in the papers. This is done for the author searched for.

        Parameters:
            data (list of dict): List of publication data, with each publication as a dictionary.
            author_name (str): Name of the author to analyze and highlight in the dashboard.
        """
        positions = []
        for i in data:
            if author_name in i['FAU']:
                for idx, author in enumerate(i['FAU']):
                    if author == author_name:
                        positions.append(idx +1)
        
        number_first_author = len([pos for pos in positions if pos == 1])
        number_author = pd.DataFrame(positions, columns=['Position']).groupby('Position').size().reset_index(name='Count')
        # make histogram of positions
        fig = px.bar(number_author, x='Position', y='Count')
        return fig, number_first_author


    with st.spinner('Creating Summary...'): # use spinner to show that the data is loading
        number_of_paper = number_paper(data)
        number_unique_collaborators = get_number_of_unique_authors(data)
        fig_most_colaborated_authors, top_author = plot_most_collaborated_authors(data)
        fig_publ_history = plot_history_published(data)
        fig_funding, most_freq_funder = plot_funding(data)
        fig_affiliation, most_freq_affiliation = plot_affiliation(data, author_name)
        most_often_last_author = get_most_frequent_last_author(data)
        fig_author_positions, number_first_author = author_positions(data, author_name)
        perc_fund = percentage_funding(data)
        perc_aff = percentage_affiliation(data)
        perc_aff_author = author_percentage_affiliation(data, author_name)

        info_df = pd.DataFrame({
            "Author Info": ["Number of Papers", "Number of Unique Collaborators", "Top Collaborator", 
                    "Most Frequent Funder", "Most Frequent Affiliation", "Most Often Last Author", "Number of First Authorships"],
            "Value": [number_of_paper, number_unique_collaborators, top_author, 
                    f'{most_freq_funder} | {round(perc_fund)}% of papers have funding information.',
                     f'{most_freq_affiliation} | {round(perc_aff_author)}% of papers include authors affiliation.', 
                    most_often_last_author, number_first_author]
        }).set_index("Author Info")


    # display the summary
    st.write('## Author Overview')
    st.write('This table provides an overview of the author and their research metrics.')
    st.dataframe(info_df, use_container_width=True)
    
    st.write('## History of Published Papers')
    st.write('This graph shows the number of papers published by the author over the course of the years. This plot shows all the papers published on PubMed.')
    st.plotly_chart(fig_publ_history, key='published_papers')

    st.write('## Top 10 Authors ')
    st.write('This graph shows the top most occured authors in the papers published with the author. This is why the name of the author is also included here. This gives us an intutition about the most frequent collaborators of the author.')
    st.plotly_chart(fig_most_colaborated_authors, key='most_collaborated_authors')

    st.write('## Funding Sources')
    st.markdown(f'This graph shows the top 10 funding sources for the papers published with the author. One project can also have multiple grants. The funding identifier is explained in the expander below. **{round(perc_fund)}% of the papers have funding information.**')
    st.plotly_chart(fig_funding, key='funding_sources')


    st.write('## Position of citation of the Author')
    st.write('This graph shows the position of the auhor in the papers. Usually the first author has done most work and the declining order of the author position is the contribution of the author.')
    st.plotly_chart(fig_author_positions, key='author_positions')

    
    st.write('## Affiliations')
    st.write(f'This plot shows the top 10 institutions which contributed to the autho papers. This is not the most frequent insitution of just the author. This are the most frequent institutions of all the authors. **{round(perc_aff)}% of the authors have affiliation information.**')
    st.plotly_chart(fig_affiliation, key='affiliations')


