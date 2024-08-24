
from flask import render_template, request, jsonify
from app import app
from app.rag import process_website, query_rag

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_website', methods=['POST'])
def add_website():
    url = request.form.get('url')
    if url:
        result = process_website(url)
        return jsonify({'message': result})
    return jsonify({'error': 'No URL provided'}), 400

@app.route('/query', methods=['POST'])
def query():
    query_text = request.form.get('query')
    if query_text:
        results = query_rag(query_text)
        return jsonify({'results': [result.page_content for result in results]})
    return jsonify({'error': 'No query provided'}), 400