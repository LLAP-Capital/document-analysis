from pymongo import MongoClient
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
import gradio as gr
from dotenv import load_dotenv
import os
import logging

# Configure logging first, before any other operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Connect to MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    dbName = os.getenv("DATABASE_NAME")
    collectionName = os.getenv("COLLECTION_NAME")
    collection = client[dbName][collectionName]
    
    # Check document count
    doc_count = collection.count_documents({})
    logger.info(f"Successfully connected to MongoDB. Number of documents in collection: {doc_count}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Define the text embedding model
try:
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("Successfully initialized OpenAI embeddings")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI embeddings: {str(e)}")
    raise

# Initialize the Vector Store
try:
    vectorStore = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=os.getenv("MONGO_URI"),
        namespace=f"{dbName}.{collectionName}",
        embedding=embeddings,
        index_name="default"  # Make sure this matches your Atlas Search index name
    )
    
    # Test the vector store
    test_results = vectorStore.similarity_search("test", k=1)
    logger.info(f"Vector store initialized successfully. Found {len(test_results)} documents.")
except Exception as e:
    logger.error(f"Failed to initialize or test vector store: {str(e)}")
    raise

def query_data(query):
    logger.info(f"Processing query: {query}")
    try:
        # Perform similarity search
        docs = vectorStore.similarity_search(query, k=1)
        if not docs:
            logger.warning("No documents found in vector store")
            return "No documents found in vector store", "No documents found in vector store"
        as_output = docs[0].page_content
        logger.debug(f"Retrieved document content: {as_output[:100]}...")  # Log first 100 chars

        # Initialize OpenAI model
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
        
        # Get retriever
        retriever = vectorStore.as_retriever()
        
        # Create QA chain
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
        
        # Execute the chain
        retriever_output = qa.run(query)
        logger.info("Successfully processed query through RetrievalQA")
        
        return as_output, retriever_output
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return f"Error: {str(e)}", f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="LAP RAG Test") as demo:
    gr.Markdown(
        """
        # LAP RAG Test
        """)
    textbox = gr.Textbox(label="Enter your Question:")
    with gr.Row():
        button = gr.Button("Submit", variant="primary")
    with gr.Column():
        output1 = gr.Textbox(lines=1, max_lines=10, label="just Atlas Vector Search (returns text field as is):")
        output2 = gr.Textbox(lines=1, max_lines=10, label="Atlas Vector Search to Langchain's RetrieverQA + OpenAI LLM:")

    button.click(query_data, textbox, outputs=[output1, output2])

logger.info("Starting Gradio interface")
demo.launch()
