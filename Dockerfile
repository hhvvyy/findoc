# 1. Use an official lightweight Python image
FROM python:3.10-slim

# 2. Install system dependencies needed for parsing and building dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 3. Set up a secure non-root user (Required by Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 4. Set the working directory inside the container
WORKDIR $HOME/app

# 5. Copy requirements and install Python dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code
COPY --chown=user . .

# 7. Expose the default port Hugging Face expects
EXPOSE 7860

# 8. Run BOTH FastAPI (on port 8000) and Streamlit (on port 7860) at the same time
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0