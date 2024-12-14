from pymongo import MongoClient
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
import gradio as gr
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
dbName = os.getenv("DATABASE_NAME")
collectionName = os.getenv("COLLECTION_NAME")
collection = client[dbName][collectionName]

# After MongoDB connection, add this check:
doc_count = collection.count_documents({})
print(f"Number of documents in collection: {doc_count}")

# Define the text embedding model
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the Vector Store
vectorStore = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string=os.getenv("MONGO_URI"),
    namespace=f"{dbName}.{collectionName}",
    embedding=embeddings,
    index_name="default"  # Make sure this matches your Atlas Search index name
)

try:
    # Test the vector store
    test_results = vectorStore.similarity_search("test", k=1)
    print(f"Vector store initialized successfully. Found {len(test_results)} documents.")
except Exception as e:
    print(f"Error testing vector store: {str(e)}")

def query_data(query):
    try:
        # Perform similarity search
        docs = vectorStore.similarity_search(query, k=1)
        if not docs:
            return "No documents found in vector store", "No documents found in vector store"
        as_output = docs[0].page_content

        # Initialize OpenAI model
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0)

        # Get retriever
        retriever = vectorStore.as_retriever()

        # Create QA chain
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

        # Execute the chain
        retriever_output = qa.run(query)

        return as_output, retriever_output
    except Exception as e:
        print(f"Error in query_data: {str(e)}")  # This will print to your console
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

demo.launch()


