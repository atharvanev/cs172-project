# CS 172 Project 
CS 172 - Project: Web Search Engine 

Part A (Option 1: Web): 

Create a web crawler for HTML pages that parses and analyzes a given seed URL for the URL, title, body, outgoing links, and number of hops to get to the link. This information will then be stored in a json format within one file with the crawled pages stored within a folder. We'll be utilizing tools such as Beautiful Soup and Scrapy to help with breaking down HTML and extracting structured data. 

Example of possible output: 
```
{ "url": "https://example.edu/page.html", 
    "title": "Example Page", 
    "body": "stripped text content...", 
    "creation_date": "2024-01-15", 
    "crawled_at": "2025-04-28T10:30:00", 
    "depth": 2, 
    "filename": "page_0042.html", 
    "outgoing_links": ["https://example.edu/other.html", "..."] 
} 
```


Group Members

* Atharva Nevasekar
* Nikhil Rao
* Austin Le
* David Lee
* Brandon Sun

To begin, start a venv and download needed dependencies with 
```
bash setup.sh 
source venv/bin/activate 
```
to activate the environment. 
All seed urls can be found within seed_urls.txt (feel free to add more). 
You can also run the web crawler in crawling directory with command: 
```scrapy crawl "name_of_crawler"```
