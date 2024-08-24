import logging
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.embeddings import OpenAIEmbeddings
from pymongo import MongoClient
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# MongoDB setup
mongodb_uri = os.environ.get('MONGODB_URI')

client = MongoClient(mongodb_uri)
db = client["teste-rag"]

def process_website(url):
    logging.info(f"Processing website: {url}")
    try:
        # Load the web page
        loader = WebBaseLoader(url)
        logging.debug("WebBaseLoader created")
        
        data = loader.load()
        logging.debug(f"Data loaded: {data[:100]}...")  # Log the first 100 characters
        
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        logging.debug("Text splitter created")
        
        docs = text_splitter.split_documents(data)
        logging.debug(f"Documents split: {len(docs)} chunks created")
        
        # Create embeddings and store in MongoDB
        embeddings = OpenAIEmbeddings()
        logging.debug("OpenAIEmbeddings created")
        
        vector_store = MongoDBAtlasVectorSearch.from_documents(
            docs,
            embeddings,
            collection=db.your_collection_name,
            index_name="your_index_name"
        )
        logging.debug("Vector store created and documents stored")
        
        return {"success": True, "message": "Website processed successfully"}
    except Exception as e:
        logging.error(f"Error processing website: {str(e)}", exc_info=True)
        raise

def query_rag(query):
    try:
        embeddings = OpenAIEmbeddings()
        vector_store = MongoDBAtlasVectorSearch(
            db.your_collection_name,
            embeddings,
            index_name="your_index_name"
        )
        results = vector_store.similarity_search(query)
        return [result.page_content for result in results]
    except Exception as e:
        logging.error(f"Error querying RAG: {str(e)}", exc_info=True)
        raise