# 📄 FinDoc AI

An AI-powered Financial Document Analyzer that allows users to upload PDF financial reports and ask questions in natural language using Retrieval-Augmented Generation (RAG).

---

## 🚀 Live Demo

🔗 https://hhvvyy-findoc.hf.space

---

## ✨ Features

- Upload financial PDF documents
- Extract and process document text
- Intelligent text chunking
- Vector embeddings using Sentence Transformers
- Semantic search with ChromaDB
- AI-powered question answering using Groq LLM
- Faithfulness evaluation of generated responses
- Clean and interactive Streamlit interface
---

## 🛠 Tech Stack

### Backend
- Python
- FastAPI

### Frontend
- Streamlit

### AI
- Groq API
- Sentence Transformers
- ChromaDB

### PDF Processing
- pdfplumber

### Deployment
- Hugging Face Spaces

---

## 📂 Project Structure

```
findoc/
│
|
|── extractor.py
│── chunker.py
│── vector_store.py
│── llm.py
│── evaluator.py
│── app.py
│
├── frontend.py
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

1. Upload a financial PDF.
2. Text is extracted from the document.
3. The text is divided into chunks.
4. Each chunk is converted into vector embeddings.
5. Chunks are stored inside ChromaDB.
6. User submits a question.
7. Relevant chunks are retrieved.
8. Groq LLM generates an answer using only retrieved context.
9. A faithfulness evaluation checks whether the answer is supported by the retrieved information.

---

## 📈 Future Improvements

- Semantic chunking
- Source citations with page numbers
- Multi-document comparison
- Financial KPI extraction
- Streaming responses
- User authentication
- Conversation history

---

## 📚 What I Learned

Building this project helped me understand:

- Retrieval-Augmented Generation (RAG)
- FastAPI backend development
- Vector databases using ChromaDB
- Embedding models
- Prompt engineering
- AI application deployment
- Building modular AI systems

---

## 🤝 Contributing

Contributions, suggestions, and feedback are welcome.

---

## 📜 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
You are free to use, modify, and distribute this project under the terms of the GPL-3.0 License. Any derivative work must also be distributed under the same license.
