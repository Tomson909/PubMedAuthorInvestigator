import re
from typing import List, Dict
from pprint import pprint
import json
import requests
from bs4 import BeautifulSoup
from time import sleep
import os
import random
from tqdm import tqdm
import sys

###########################
# Searching Default Execution
###########################
class PubMedRecord:
    def __init__(self, raw_data: str):
        self.raw_data = raw_data
        self.chunks = self._make_pmid_chungs()
        self.parsed_raw = self._extract_all()
        self.parsed = self._sim_id_to_list()
    
    def filter_abstract_4_names(self, author):
        filtered_chunks = [entry for entry in self.parsed if author in entry['FAU']]
        # get the last chunk which does not contain the author, then we will stop scraping
        index = 0
        for entry in self.parsed:
            if author not in entry['FAU']:
                break
            index += 1
        return filtered_chunks, index 

    def _make_pmid_chungs(self):
        # find the first pmid occurence and put all text until the next pmid into a list, using regex is appropriate
        removed_start = self.raw_data[re.search(r'\bPMID\s*-\s*\d+', self.raw_data).start():].strip()
        split_data =  re.split(r'(?=PMID\s*-\s*\d+|PMID-\s*\d+)', removed_start)[1:]
        return split_data

    def _extract_all(self):
        parsed_results = []
        for chunk in self.chunks:
            dummy = []
            # iterate over each line in the chunk
            for line in chunk.split('\n'):
                # find the key-value pairs
                if re.match(r'[A-Z]{2,6}\s*-\s*', line):
                    dummy.extend([line])
                else:
                    dummy[-1] += line
            dummy = [entry.strip().replace('\n      ', '').replace('\r', '').replace('\n', '') for entry in dummy]
            dummy = [re.split(r'\s*-\s*', entry, 1) for entry in dummy]
            dummy = [{entry[0]: entry[1]} for entry in dummy]
            parsed_results.append(dummy)
        
        # make the parsed results a dictionary
        return parsed_results

    def _sim_id_to_list(self):
        self.parsed = []
        for chunk_raw in self.parsed_raw:
            chunk_parsed = {}
            current_author = ''
            for i,entry in enumerate(chunk_raw):
                key = list(entry.keys())[0]
                value = list(entry.values())[0]
                # FAU will be first entry and the AU
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
    def __init__(self, author):
        self.author = author
        self.output_dir = f'results/{author.replace(", ", "_")}/processed'
        self.raw_dir = f'results/{author.replace(", ", "_")}/raw'
        os.makedirs(self.raw_dir, exist_ok=True)

    def author_url(self, page):
        """Construct the PubMed search URL for the given author and page."""
        return f'https://pubmed.ncbi.nlm.nih.gov/?term={self.author.replace(" ", "+")}%5Bauthor%5D&format=pubmed&size=200&page={page}'

    def save_chunks(self, filtered_chunks):
        """Save filtered chunks to JSON files."""
        for chunk in filtered_chunks:
            pmid = chunk.get('PMID', None)
            
            if pmid is not None:
                pmid_cleaned = ''.join(filter(str.isalnum, pmid[0]))  # Clean the PMID
                file_path = os.path.join(self.output_dir, f'{pmid_cleaned}.json')

                with open(file_path, 'w') as file:
                    json.dump(chunk, file, ensure_ascii=False, indent=4)  # Save as pretty JSON


    def search_author(self):
        """Search for publications by the specified author on PubMed."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        # check if the author has been searched before
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
                parsed = PubMedRecord(str(soup.get_text()))  # Assuming PubMedRecord is defined elsewhere
                filtered_chunks, index = parsed.filter_abstract_4_names(self.author)
                #print(f"Page {url_pubmed} has {len(filtered_chunks)} entries, index: {index}")

                self.save_chunks(filtered_chunks)  # Save filtered results
                
                # Save raw response
                with open(os.path.join(self.raw_dir, f'{current_page}.html'), 'w') as file:
                    file.write(str(soup))

                sleep(random.uniform(1, 2))  # Simulate human-like delay
            else:
                break

            current_page += 1
        return self.output_dir

class MultPubMedSearcher:
    def __init__(self, root_author, depth=1):
        self.root_author = root_author
        self.depth = depth
        self.searched_authors = [root_author]
        self.metadata = {'authors': [root_author], 'depth': [depth]}
    
    def get_new_authors(self):
        # extract from the hole results directory all authors, the authors are saved 
        mom_dir = 'results/'
        son_dir = 'processed'
        author_dirs = os.listdir(mom_dir)
        file_paths = [
            os.path.join(mom_dir, author, son_dir, file)
            for author in author_dirs
            for file in os.listdir(os.path.join(mom_dir, author, son_dir))
            if os.path.isdir(os.path.join(mom_dir, author, son_dir))  # Check if processed dir exists
        ]
        authors = []
        for file_path in file_paths:
            with open(file_path, 'r') as file:
                data = json.load(file)
                authors.extend(data['FAU'])
        return authors

    def search(self):
        # First search the root author
        searcher = SinglePubMedSearcher(self.root_author)
        searcher.search_author()
        
        # Get new authors
        for i in range(1, self.depth):
            authors = self.get_new_authors()
            
            # Use tqdm to show progress
            for author in tqdm(authors, desc=f'Searching authors (Depth {i})', unit='author'):
                if author not in self.searched_authors:
                    self.searched_authors.append(author)
                    searcher = SinglePubMedSearcher(author)
                    searcher.search_author()

#searcher = MultPubMedSearcher('Mishra, Neha', 1)
#searcher.search()


##################################
# St

SinglePubMedSearcher('Mishra, Neha').search_author()
