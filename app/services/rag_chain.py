from pathlib import Path
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
# 确保导入了 PromptValue，尽管我们直接处理字符串，但了解类型转换很重要
from langchain_core.prompt_values import PromptValue
import dashscope


# --- CustomDashScopeEmbeddings 类定义 ---
class CustomDashScopeEmbeddings:
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        all_embeddings = []
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i: i + batch_size]

            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=batch_texts,
                api_key=self.api_key
            )

            if response.status_code == 200:
                if hasattr(response, 'output') and 'embeddings' in response.output:
                    for item in response.output['embeddings']:
                        all_embeddings.append(item['embedding'])
                else:
                    raise Exception(
                        "DashScope Embedding Error: Unexpected response output structure or missing 'embeddings' key.")
            else:
                raise Exception(
                    f"DashScope Embedding Error: {response.code} - {response.message} for batch starting with: '{batch_texts[0]}'")
        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


# --- CustomChatDashScope 类定义 ---
class CustomChatDashScope:
    def __init__(self, model: str, api_key: str, temperature: float = 0.0):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

    # invoke 方法现在直接接收字符串 prompt_text
    def invoke(self, prompt_text: str):
        messages = [{'role': 'user', 'content': prompt_text}]

        response = dashscope.Generation.call(
            model=self.model,
            messages=messages,
            result_format='message',
            temperature=self.temperature,
            api_key=self.api_key
        )

        if response.status_code == 200:
            if hasattr(response, 'output') and hasattr(response.output, 'choices') and response.output.choices:
                return response.output.choices[0].message.content
            else:
                raise Exception("DashScope Chat Error: Unexpected response structure from API.")
        else:
            raise Exception(f"DashScope Chat Error: {response.code} - {response.message}")


def create_rag_chain(csv_path: str, dashscope_api_key: str, columns_to_use=None):
    """
    Creates a Retrieval-Augmented Generation (RAG) chain using a CSV file and DashScope API.
    Args:
        csv_path (str): The file path to the CSV document.
        dashscope_api_key (str): The API key for accessing DashScope services.
        columns_to_use (list, optional): List of column names to include in the metadata. Defaults to None.
    Returns:
        rag_chain: A configured RAG chain for answering questions based on the CSV data.
    """

    # 配置 DashScope API 密钥
    dashscope.api_key = dashscope_api_key

    # 1. Load CSV documents
    loader = CSVLoader(
        file_path=csv_path,
        csv_args={"delimiter": ",", "quotechar": '"'},
        source_column="source"
        if columns_to_use is None
        else None,
        metadata_columns=columns_to_use,
        encoding='utf-8'
    )
    documents = loader.load()

    # 2. Transform CSV rows into meaningful text chunks
    def format_document(doc):
        if columns_to_use:
            metadata = {k: doc.metadata[k] for k in columns_to_use if k in doc.metadata}
        else:
            metadata = doc.metadata

        formatted_text = "\n".join(
            [f"{key}: {value}" for key, value in metadata.items()]
        )
        doc.page_content = formatted_text
        return doc

    documents = [format_document(doc) for doc in documents]

    # 3. 创建 vector store
    embeddings = CustomDashScopeEmbeddings(
        model="text-embedding-v4",
        api_key=dashscope_api_key,
    )

    vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)

    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 10}
    )

    # 4. 创建聊天 LLM
    llm = CustomChatDashScope(
        model="qwen-plus",
        api_key=dashscope_api_key,
        temperature=0,
    )

    # 5. Create prompt template
    template = """
    You are a polite Cocktail Advisor.
    Answer the question based only on the following context from the CSV data, 
    using all the data from the csv file you have: {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # 6. Create and return the RAG chain
    rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | (lambda x: x.to_string())  # 新增：将 ChatPromptValue 转换为字符串
            | llm.invoke
            | StrOutputParser()
    )

    return rag_chain