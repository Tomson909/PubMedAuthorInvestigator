# Welcome to the PubMed Author Explorer!
This application is designed to help you explore and analyze the research publications of a specific author on PubMed.
![Demo](demo.gif)

## What is [PubMed](https://pubmed.ncbi.nlm.nih.gov/)?
PubMed is a free online database that provides access to a vast collection of biomedical and life sciences research articles. Managed by the National Center for Biotechnology Information (NCBI) at the U.S. National Library of Medicine (NLM), PubMed includes millions of citations and abstracts from research studies, clinical trials, review papers, and other scholarly articles published in scientific journals. It is widely used by researchers, healthcare professionals, students, and the public to find credible and up-to-date information on topics in medicine, biology, and other health-related fields.

While PubMed itself usually provides article abstracts, it often links to full-text versions, which may be available for free or through paid subscriptions, depending on the publisher.

## What is the App About?
This app provides insights into an author’s research by offering various metrics and visualizations. With this tool, you can explore an overview of an author’s work, conduct network analysis to see co-author relationships, and explore topic clustering of their publications.

Each section within the app provides detailed information and visual representations to give you a better understanding of the author's research profile.

## Important Note
> - Ensure that the author's name is entered **accurately**; otherwise, the search may return no results.
> - The app currently **cannot distinguish between authors with the same name**; results may include works by multiple individuals if their names match.

## How is the Data Retrieved?
The data is retrieved by sending HTTP requests to PubMed's internal API. Each search query is structured to return pages of results in PubMed format, like this:

`https://pubmed.ncbi.nlm.nih.gov/?term=lastname+firstname&format=pubmed&size=200&page=1`

Using this search method, the app gathers data one page at a time, with each page containing a specified number of results. 

To comply with PubMed’s [usage policies](https://www.ncbi.nlm.nih.gov/home/about/policies/), the app limits requests to a maximum of 3 per second, adding a delay to avoid server blocks. The retrieved data is then parsed and saved as JSON files for efficient use within the app. Please read the usage policies carefully before using the app. Use is at your own risk. There are also API's available but used this method, since it seemes straight forward to me.

## How to Use the App?
To get started, enter the author's name in the search bar and click the **Search** button. The app will then retrieve the author's publications from PubMed and display the results in the **Summary** tab. From there, you can navigate to the **Author Network** and **Topic Clustering** tabs to explore co-author relationships and topic groupings, respectively.


