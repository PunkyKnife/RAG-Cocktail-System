# RAG-Cocktail-System: AI-Powered Cocktail Advisor

This project is an AI-powered cocktail recommendation system that leverages Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs). It can recommend cocktails from a local CSV database and generate new cocktail recipes based on user queries.

## ✨ Features

- **Cocktail Recommendations**: Get suggestions for cocktails from a pre-defined local `.csv` file.
- **New Recipe Generation**: Invent unique cocktail recipes using a Large Language Model based on your specified characteristics.
- **Dual Language Support**: Supports both English and Chinese for generating new recipes.
- **Interactive Web Interface**: A simple and intuitive chat interface for seamless interaction.

## 🛠️ Technologies Used

The project is built using Python and several key libraries:

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) for building the API.
- **LLM Integration**: [LangChain](https://www.langchain.com/) for constructing the RAG chain and interacting with LLMs.
- **Language Model (LLM) & Embeddings**: [DashScope](https://www.dashscope.cn/) (Alibaba Cloud) is used for both text embeddings (`text-embedding-v4`) and language model (`qwen-plus`) capabilities.
- **Vector Database**: [Chroma](https://www.trychroma.com/) for storing and retrieving cocktail data efficiently.
- **Data Handling**: [Pandas](https://pandas.pydata.org/) for reading and processing the CSV data.
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/) to serve the FastAPI application.
- **Frontend Server**: Python's built-in `http.server` for the static web interface.
- **Frontend**: HTML, CSS, and JavaScript for the chat interface.

## 📂 Project Structure

```plaintext
RAG-Cocktail-System/
├── app/
│   ├── check.py
│   ├── final_cocktails.csv  # This is a duplicate of the root level CSV, use the one in the root for RAG
│   ├── main.py              # FastAPI application entry point
│   ├── routers/
│   │   ├── predict-roi.py   # Original predict router, can be ignored
│   │   └── predict.py       # API endpoint for cocktail prediction/generation
│   ├── schemas/
│   │   └── question.py      # Pydantic model for request body
│   ├── services/
│   │   ├── rag_chain-ori.py # Original RAG chain, can be ignored
│   │   └── rag_chain.py     # Core RAG logic, custom LLM and embedding classes
├── final_cocktails.csv      # Main cocktail database
├── index.html               # Frontend web interface
├── pyproject.toml           # Project dependencies and metadata
└── start.py                 # Script to launch backend and frontend servers
```

## 🚀 Setup and Installation

Follow these steps to get the project up and running on your local machine.

### 1. Prerequisites

- Python 3.11 or higher installed on your system.
- A [DashScope API Key](https://dashscope.console.aliyun.com/apiKey) from Alibaba Cloud.

### 2. Clone the Repository

If you haven't already, clone the project repository:

```
git clone <repository_url> # Replace with your repository URL 
cd RAG-Cocktail-System
```

### 3. Set up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```
python -m venv .venv
```

Activate the virtual environment:

- macOS/Linux:

  `source .venv/bin/activate`

- Windows:

  `.venv\Scripts\activate`

### 4. Install Dependencies

Install the project dependencies using uv (or pip if uv is not preferred):

```
uv pip install -e . # Or, if you prefer pip: # pip install -e .
```

### 5. Configure DashScope API Key

The DashScope API key is hardcoded in app/routers/predict.py for convenience. **For production environments, it is strongly recommended to load this key from environment variables.**

Open RAG-Cocktail-System/app/routers/predict.py and replace "sk-9e39176f7e20433bb1651fe18d0ea975" with your actual DashScope API Key:

```
# app/routers/predict.py DASHSCOPE_API_KEY = "YOUR_DASHSCOPE_API_KEY"  # Replace this with your actual key
```

### 6. Run the Application( Just run this )

Execute the start.py script to launch both the backend and frontend servers:

```
python start.py
```

You should see output indicating that the backend and frontend servers have started.

## 🚀 Usage

Once the servers are running, open your web browser and navigate to:

http://localhost:8000/

You can interact with the system through the chat interface:

- To get cocktail recommendations from the CSV: Ask questions like:
  - "What is the recipe for Mojito?"
  - "Suggest a cocktail with Gin and Lemon."
  - "Tell me about non-alcoholic drinks."
  - "Show me drinks with Vodka and Cranberry juice."
- To generate a new cocktail recipe (supports English and Chinese):
  - **English**: "Generate new recipe: a refreshing drink for summer with fruit and mint."
  - **Chinese**: "生成新配方：一种适合冬天的热饮，要有咖啡和奶油。" (Generate new recipe: a hot drink for winter, with coffee and cream.)
  - **General Generation**: "Generate new recipe" or "生成新配方" (The model will create a unique recipe without specific requirements).
 - Below is a preview image, you can also see Test_Demo.mp4 in the repository
![Test](https://github.com/user-attachments/assets/a450e07d-24e6-4977-815c-6e7454cb6b50)
