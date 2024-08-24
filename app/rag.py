import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from app import db
from app.models import Website

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def process_website(url):
    content = scrape_website(url)
    Website.add_website(url, content)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(content)
    
    embeddings = OpenAIEmbeddings()
    vector_store = MongoDBAtlasVectorSearch.from_texts(
        texts,
        embeddings,
        collection=db.vector_store
    )
    return "Website processed and added to RAG database."

def query_rag(query):
    embeddings = OpenAIEmbeddings()
    vector_store = MongoDBAtlasVectorSearch(db.vector_store, embeddings)
    results = vector_store.similarity_search(query, k=3)
    return results