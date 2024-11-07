import streamlit as st

def show_page():
    st.write("Welcome to the PubMed Author Explorer! This application is designed to help you explore and analyze the research publications of a specific author on PubMed.")

    st.markdown("## What is [PubMed](https://pubmed.ncbi.nlm.nih.gov/)?")
    st.write("""
            PubMed is a free online database that provides access to a vast collection of biomedical and life sciences research articles. 
            Managed by the National Center for Biotechnology Information (NCBI) at the U.S. National Library of Medicine (NLM), 
            PubMed includes millions of citations and abstracts from research studies, clinical trials, review papers, and other scholarly articles published in scientific journals. 
            It is widely used by researchers, healthcare professionals, students, and the public to find credible and up-to-date information on topics in medicine, biology, and other health-related fields.

            While PubMed itself usually provides article abstracts, it often links to full-text versions, which may be available for free or through paid subscriptions, depending on the publisher.
            """
    )

    st.markdown("## What is the App About?")
    st.write(
        """
        This app provides insights into an author’s research by offering various metrics and visualizations. 
        With this tool, you can explore an author’s work, conduct network analysis to see 
        co-author relationships, and explore topic clustering of their publications, to see in what major fields the author is contributing.

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

    # How is the Data Retrieved?
    st.markdown("## How is the Data Retrieved?")
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
        number of results. There are also API's available but used this method, since it seemes straight forward to me. The text returned PubMed format looks like this:
        ```
        PMID- 15372042
        OWN - NLM
        STAT- MEDLINE
        DCOM- 20041015
        LR  - 20240308
        IS  - 1476-4687 (Electronic)
        IS  - 0028-0836 (Linking)
        VI  - 431
        IP  - 7006
        DP  - 2004 Sep 16
        TI  - The functions of animal microRNAs.
        PG  - 350-5
        AB  - MicroRNAs (miRNAs) are small RNAs that regulate the expression of complementary 
            messenger RNAs. Hundreds of miRNA genes have been found in diverse animals, and 
            many of these are phylogenetically conserved. With miRNA roles identified in 
            developmental timing, cell death, cell proliferation, haematopoiesis and 
            patterning of the nervous system, evidence is mounting that animal miRNAs are 
            more numerous, and their regulatory impact more pervasive, than was previously 
            suspected.
        FAU - Ambros, Victor
        AU  - Ambros V
        AD  - Dartmouth Medical School, Department of Genetics, Hanover, New Hampshire 03755, 
            USA (e-mail: vra@dartmouth.edu)
        LA  - eng
        PT  - Journal Article
        PT  - Research Support, U.S. Gov't, P.H.S.
        PT  - Review
        PL  - England
        TA  - Nature
        JT  - Nature
        JID - 0410462
        RN  - 0 (MicroRNAs)
        SB  - IM    
        ...
        ```
        To comply with PubMed’s [usage policies](https://www.ncbi.nlm.nih.gov/home/about/policies/), the app 
        limits requests to a maximum of 3 per second, adding a delay to avoid server blocks. The retrieved 
        data is then parsed and saved as JSON files for efficient use within the app. Please read the usage policies carefully
        before using the app. Use is at your own risk. The identifiers are explained in the following drop down. I tried to gather all possible identifiers. Maybe some are missing.
        """
    )
    with st.expander("Explanation of PubMed Identifiers"):
        st.markdown(
            """
            | Variable | Description |
            |----------|-------------|
            | **PMID** | PubMed Identifier - Unique identification number assigned to each article in PubMed, used for easy reference. |
            | **OWN**  | Owner - Indicates the institution responsible for the article entry, typically **NLM** (National Library of Medicine). |
            | **STAT** | Status - Represents the indexing status of the article in PubMed. **MEDLINE** indicates it has been indexed with MeSH terms for easy categorization. |
            | **DCOM** | Date of Completion - The date when the article's processing for MEDLINE was completed, formatted as YYYYMMDD. |
            | **LR**   | Last Revision Date - The last date the record was modified in the PubMed system, in the format YYYYMMDD. |
            | **IS**   | ISSN - International Standard Serial Number for the journal, with separate entries for print and electronic versions. |
            | **VI**   | Volume - The volume number of the journal in which the article was published. |
            | **IP**   | Issue - The specific issue of the journal's volume containing the article. |
            | **DP**   | Date of Publication - The official publication date of the article, formatted as YYYY Mon DD or YYYY Mon. |
            | **TI**   | Title - The title of the article. |
            | **PG**   | Page Range - The specific pages on which the article appears within the journal issue. |
            | **AB**   | Abstract - A summary of the article's main points, providing an overview of its content and findings. |
            | **FAU**  | Full Author - Full name of each author as listed in the publication. |
            | **AU**   | Author - The abbreviated name of each author, usually in the format Last name followed by initials. |
            | **AD**   | Author Affiliation - The institutional affiliation of the author(s), sometimes including contact information. |
            | **LA**   | Language - The language in which the article is written, e.g., **eng** for English. |
            | **PT**   | Publication Type - The type of article, such as Journal Article, Review, or Interview. |
            | **PL**   | Place of Publication - The country in which the journal is published. |
            | **TA**   | Title Abbreviation - The abbreviated title of the journal. |
            | **JT**   | Journal Title - The full title of the journal in which the article was published. |
            | **JID**  | Journal Identifier - A unique identifier for the journal in PubMed. |
            | **RN**   | Registry Number - Registry numbers for substances mentioned in the article, usually related to specific compounds or proteins. |
            | **SB**   | Subset - A code indicating a subset of PubMed to which the article belongs, such as **IM** for Index Medicus. |
            | **MH**   | MeSH Terms - Medical Subject Headings that categorize the article's content, facilitating topic-based searches. |
            | **RF**   | Reference Count - The number of references cited in the article. |
            | **EDAT** | Entry Date - The date the record was first added to PubMed. |
            | **MHDA** | MeSH Date of Assignment - The date MeSH terms were assigned to the article. |
            | **CRDT** | Creation Date - The date the article record was created in the PubMed database. |
            | **PHST** | Publication History Status - Tracks key milestones in the article’s PubMed history, such as **[pubmed]** for entry in PubMed, **[medline]** for MEDLINE processing, and **[entrez]** for general entry. |
            | **AID**  | Article Identifier - Identifiers used by the publisher, often including **DOI** and **PII**. |
            | **PST**  | Publication Status - Indicates the publication status, e.g., **ppublish** for print publication. |
            | **SO**   | Source - A standard citation format that combines journal name, publication date, volume, issue, and page numbers for easy reference. |
            """
        )
            

    st.markdown("## How to Use the App?")
    st.write(
        """
        To get started, enter the author's name in the search bar and click the **Search** button. The app will 
        then retrieve the author's publications from PubMed and display the results in the **Summary** tab. 
        From there, you can navigate to the **Author Network** and **Topic Clustering** tabs to explore 
        co-author relationships and topic groupings, respectively.
        """
    )
