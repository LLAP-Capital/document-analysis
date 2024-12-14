# Document-Analysis

# Install dependencies
pip install -r requirements.txt

# Build the image
docker build -t lap-rag-app .

# Run the container
docker run -p 7860:7860 --env-file .env lap-rag-app

# Clean up
docker system prune -f

# Clean up logs
make clean