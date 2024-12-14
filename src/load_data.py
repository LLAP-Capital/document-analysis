from pymongo import MongoClient
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set the MongoDB URI, DB, Collection Names
client = MongoClient(os.getenv("MONGO_URI"))
dbName = os.getenv("DATABASE_NAME")
collectionName = os.getenv("COLLECTION_NAME")
collection = client[dbName][collectionName]

# Replace the DirectoryLoader with individual TextLoader
documents = []
for filename in os.listdir('../data/'):
    if filename.endswith('.txt'):
        try:
            loader = TextLoader(f'../data/{filename}', encoding='utf-8')
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading file {filename}: {str(e)}")

# Define the OpenAI Embedding Model we want to use for the source data
# The embedding model is different from the language generation model
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the VectorStore, and
# vectorise the text from the documents using the specified embedding model, and insert them into the specified MongoDB collection
vectorStore = MongoDBAtlasVectorSearch.from_documents(documents, embeddings, collection=collection)