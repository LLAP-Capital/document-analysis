from flask import render_template, request, jsonify
from app import app, db
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

@app.route('/process', methods=['POST'])
def process():
    url = request.form['url']
    try:
        result = process_website(url)
        # Check if the document was added to the database
        doc = db.your_collection_name.find_one({'url': url})
        if doc:
            return jsonify({'success': True, 'message': 'Document processed and added to database successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Document processed but not found in database. Check your database connection.'})
    except Exception as e:
        app.logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Error processing document: {str(e)}'})

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    query = request.json['query']
    try:
        response = query_rag(query)
        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f"Error in chat: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/documents')
def documents():
    docs = db.your_collection_name.find()
    return render_template('documents.html', documents=docs)

@app.route('/test_db')
def test_db():
    try:
        db.your_collection_name.find_one()
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {str(e)}"