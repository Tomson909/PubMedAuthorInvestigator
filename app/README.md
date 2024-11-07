# App
This directory contains everything to run the streamlit application I built. The app should be self explanatory. I tried to document the code as goodas possible, so a reader can understand the code easily.

## Structure
### PubMed Crawler
The directory also contains the pubmed crawler and the parser of the returned PubMed format.
### About
The App consists of 4 different pages. When starting the app the About page shows up. This page is supposed to give a short introduction of what is the app about. But the app should be 'self explanatory'. 

### Summary
This page sumamrizes some of the important aspects of the authors published papers. 

### Author Network
This streamlit page extracts all the authors from the papers and creates a nice visualization to be able to investigate the network of authors the author worked in. 

### Title Embeddings
This page performs a title embedding and then a pca based on the embedding vectors in order to vizualize the topics in a 2 dimensional plot. 
