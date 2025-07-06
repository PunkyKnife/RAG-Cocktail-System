import os
from fastapi import APIRouter
from app.schemas.question import Question
from app.services.rag_chain import create_rag_chain

router = APIRouter(prefix="/predict")

# ⚠️ 安全警告：为了方便，这里直接使用了你提供的密钥。
# 在生产环境中，强烈建议通过环境变量加载密钥！
# 例如：DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")
# 确保你提供的密钥是有效的阿里云 DashScope API 密钥。
DASHSCOPE_API_KEY = "sk-9e39176f7e20433bb1651fe18d0ea975"


@router.post("/")
async def predict(question: Question):
    """
    接收用户问题，通过 RAG 链生成答案。
    """
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "YOUR_DASHSCOPE_API_KEY":  # 这里的YOUR_DASHSCOPE_API_KEY只是一个占位符，如果上面直接写死密钥，这个条件基本不会触发
        return {
            "response": "Error: DashScope API key is not set. Please set the DASHSCOPE_API_KEY environment variable or replace its value in app/routers/predict.py with your actual key."}

    # 传递 DashScope API 密钥给 create_rag_chain
    rag_chain = create_rag_chain(
        csv_path=str(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "final_cocktails.csv")),
        dashscope_api_key=DASHSCOPE_API_KEY,  # 修正了参数名
        columns_to_use=["name", "ingredients", "ingredientMeasures", "alcoholic", "category", "glassType",
                        "instructions"]  # 修正了列名
    )

    response = rag_chain.invoke(question.msg)
    return {"response": response}