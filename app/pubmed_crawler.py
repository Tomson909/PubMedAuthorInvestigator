import re
import os
import json
import requests
import random
from time import sleep
from bs4 import BeautifulSoup

class PubMedRecord:
    """
    Parses raw PubMed(There File Format) data into structured records for processing.

    Attributes:
        raw_data (str): Raw data input from PubMed.
        chunks (list): List of individual chunks of PubMed records, split by unique identifiers (PMID).
        parsed_raw (list): Parsed data extracted from raw chunks into key-value pairs.
        parsed (list): Final processed list of dictionaries where each dictionary contains metadata for a record.

    Methods:
        filter_abstract_4_names(author):
            Filters records by author name, returning records that match the author.

        _make_pmid_chungs():
            Parses raw data into chunks based on unique PMIDs.

        _extract_all():
            Extracts all metadata key-value pairs from each chunk into a structured format.

        _sim_id_to_list():
            Processes the parsed raw data into a structured list of records, each represented by a dictionary.
    """
    
    def __init__(self, raw_data: str):
        self.raw_data = raw_data
        self.chunks = self._make_pmid_chungs()
        self.parsed_raw = self._extract_all()
        self.parsed = self._sim_id_to_list()
    
    def filter_abstract_4_names(self, author):
        """
        Filters the parsed data to retrieve entries associated with the specified author. Different people with the same name result can not be filtered easily.

        Args:
            author (str): The name of the author to filter by.

        Returns:
            tuple: (filtered_chunks, index) where filtered_chunks is a list of records by the author,
                   and index is the position of the last non-matching author entry.
        """
        filtered_chunks = [entry for entry in self.parsed if author in entry['FAU']]
        
        # Locate the last chunk that does not contain the author, to end further scraping if needed
        index = 0
        for entry in self.parsed:
            if author not in entry['FAU']:
                break
            index += 1
        return filtered_chunks, index 

    def _make_pmid_chungs(self):
        """
        Splits raw PubMed data into chunks based on the unique identifier (PMID).

        Returns:
            list: List of text segments, each representing a distinct PubMed record.
        """
        removed_start = self.raw_data[re.search(r'\bPMID\s*-\s*\d+', self.raw_data).start():].strip()
        split_data = re.split(r'(?=PMID\s*-\s*\d+|PMID-\s*\d+)', removed_start)[1:]
        return split_data

    def _extract_all(self):
        """
        Parses each chunk into key-value pairs representing metadata fields for each record.

        Returns:
            list: List of dictionaries containing the extracted data for each PubMed record.
        """
        parsed_results = []
        for chunk in self.chunks:
            dummy = []
            # Parse each line for key-value metadata fields
            for line in chunk.split('\n'):
                if re.match(r'[A-Z]{2,6}\s*-\s*', line):
                    dummy.extend([line])
                else:
                    dummy[-1] += line
            # Clean up and structure the data
            dummy = [entry.strip().replace('\n      ', '').replace('\r', '').replace('\n', '') for entry in dummy]
            dummy = [re.split(r'\s*-\s*', entry, 1) for entry in dummy]
            dummy = [{entry[0]: entry[1]} for entry in dummy]
            parsed_results.append(dummy)
        
        return parsed_results

    def _sim_id_to_list(self):
        """
        Converts parsed raw data into a structured dictionary format for each PubMed record.

        Returns:
            list: Final list of dictionaries, each representing a PubMed record with metadata fields.
        """
        self.parsed = []
        for chunk_raw in self.parsed_raw:
            chunk_parsed = {}
            current_author = ''
            for i, entry in enumerate(chunk_raw):
                key = list(entry.keys())[0]
                value = list(entry.values())[0]
                # Store author-related and address fields under unique keys
                if key not in chunk_parsed:
                    chunk_parsed[key] = []
                if key == 'FAU':
                    author = value
                if key == 'AD':
                    chunk_parsed[key].append(value.replace('\r', '').replace('       ', ' '))
                    key = author + '_' + key                
                if key not in chunk_parsed:
                    chunk_parsed[key] = []
                chunk_parsed[key].append(value.replace('\r', '').replace('       ', ' '))
            self.parsed.append(chunk_parsed)

        return self.parsed


class SinglePubMedSearcher:
    """
    Searches PubMed for publications by a specified author and stores results.

    Attributes:
        author (str): The name of the author to search for.
        output_dir (str): Directory path to store processed results.
        raw_dir (str): Directory path to store raw HTML response files.

    Methods:
        author_url(page):
            Constructs a PubMed search URL for the given author and page.

        save_chunks(filtered_chunks):
            Saves filtered PubMed records to JSON files.

        search_author():
            Searches PubMed for records by the specified author, saving results in structured JSON format.
    """
    
    def __init__(self, author):
        self.author = author
        self.output_dir = f'results/{author.replace(", ", "_")}/processed'
        self.raw_dir = f'results/{author.replace(", ", "_")}/raw'
        os.makedirs(self.raw_dir, exist_ok=True)

    def author_url(self, page):
        """
        Constructs the PubMed search URL for the given author and page number. The maximum page number is 200.

        Args:
            page (int): The page number of the search results.

        Returns:
            str: The URL for the author's PubMed search results.
        """
        return f'https://pubmed.ncbi.nlm.nih.gov/?term={self.author.replace(" ", "+")}%5Bauthor%5D&format=pubmed&size=200&page={page}'

    def save_chunks(self, filtered_chunks):
        """
        Saves filtered PubMed records to JSON files in the output directory.

        Args:
            filtered_chunks (list): List of filtered records to save.
        """
        for chunk in filtered_chunks:
            pmid = chunk.get('PMID', None)
            
            if pmid is not None:
                pmid_cleaned = ''.join(filter(str.isalnum, pmid[0]))  # Clean the PMID
                file_path = os.path.join(self.output_dir, f'{pmid_cleaned}.json')

                with open(file_path, 'w') as file:
                    json.dump(chunk, file, ensure_ascii=False, indent=4)  # Save as pretty JSON


    def search_author(self):
        """
        Searches for publications by the specified author on PubMed and saves them.

        Returns:
            str: Path to the output directory with saved JSON files.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Check if the author has already been searched
        if os.path.exists(self.output_dir):
            print(f'Author {self.author} has been searched before. Skipping...')
            return self.output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        current_page = 1
        while current_page < 6:
            url_pubmed = self.author_url(current_page)
            response = requests.get(url_pubmed, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                parsed = PubMedRecord(str(soup.get_text()))  # Parse raw data into structured format
                filtered_chunks, index = parsed.filter_abstract_4_names(self.author)

                self.save_chunks(filtered_chunks)  # Save filtered results
                
                # Save raw response HTML
                with open(os.path.join(self.raw_dir, f'{current_page}.html'), 'w') as file:
                    file.write(str(soup))

                sleep(random.uniform(1, 2))  # Simulate human-like delay
            else:
                break

            current_page += 1
        return self.output_dir


# For nested Author search, due to the limitation massive growth of the author tree, I will not use this. Maybe for future work.
# class MultPubMedSearcher:
#     def __init__(self, root_author, depth=1):
#         self.root_author = root_author
#         self.depth = depth
#         self.searched_authors = [root_author]
#         self.metadata = {'authors': [root_author], 'depth': [depth]}
    
#     def get_new_authors(self):
#         # extract from the hole results directory all authors, the authors are saved 
#         mom_dir = 'results/'
#         son_dir = 'processed'
#         author_dirs = os.listdir(mom_dir)
#         file_paths = [
#             os.path.join(mom_dir, author, son_dir, file)
#             for author in author_dirs
#             for file in os.listdir(os.path.join(mom_dir, author, son_dir))
#             if os.path.isdir(os.path.join(mom_dir, author, son_dir))  # Check if processed dir exists
#         ]
#         authors = []
#         for file_path in file_paths:
#             with open(file_path, 'r') as file:
#                 data = json.load(file)
#                 authors.extend(data['FAU'])
#         return authors

#     def search(self):
#         # First search the root author
#         searcher = SinglePubMedSearcher(self.root_author)
#         searcher.search_author()
        
#         # Get new authors
#         for i in range(1, self.depth):
#             authors = self.get_new_authors()
            
#             # Use tqdm to show progress
#             for author in tqdm(authors, desc=f'Searching authors (Depth {i})', unit='author'):
#                 if author not in self.searched_authors:
#                     self.searched_authors.append(author)
#                     searcher = SinglePubMedSearcher(author)
#                     searcher.search_author()

#searcher = MultPubMedSearcher('Mishra, Neha', 1) Too many connections. Takes too long to search all authors.
#searcher.search()
#SinglePubMedSearcher('Mishra, Neha').search_author()
