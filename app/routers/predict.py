import os
from fastapi import APIRouter
from app.schemas.question import Question
from app.services.rag_chain import create_rag_chain, CustomChatDashScope
from langchain_core.prompts import ChatPromptTemplate

router = APIRouter(prefix="/predict")

# ⚠️ 安全警告：为了方便，这里直接使用了你提供的密钥。
# 在生产环境中，强烈建议通过环境变量加载密钥！
# 例如：DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")
DASHSCOPE_API_KEY = "sk-9e39176f7e20433bb1651fe18d0ea975"  # 你的 DashScope API 密钥


@router.post("/")
async def predict(question: Question):
    """
    接收用户问题，根据意图生成答案或新配方。
    """
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "YOUR_DASHSCOPE_API_KEY":
        return {
            "response": "Error: DashScope API key is not set. Please set the DASHSCOPE_API_KEY environment variable or replace its value in app/routers/predict.py with your actual key."}

    user_message = question.msg.strip()
    user_message_lower = user_message.lower()  # 将用户输入转为小写，以便进行不区分大小写的匹配

    # 定义生成配方的触发关键词列表（支持中英文）
    chinese_triggers = ["生成新配方", "给我一个新配方", "新的配方"]
    english_triggers = ["generate new recipe", "create new recipe", "new recipe", "make a new recipe"]

    # 定义中英文的生成 Prompt 模板
    chinese_generation_prompt_template = """
    你是一位富有创意的鸡尾酒调酒师。
    请根据以下要求，构思并提供一个全新的鸡尾酒配方。
    配方应包含：鸡尾酒名称、所用材料（及其大致比例，如“份”或“毫升”）、制作步骤、酒精度分类（如“酒精饮品”或“非酒精饮品”）、饮品类别（如“经典鸡尾酒”、“创意饮品”）、口味描述和推荐饮用场合。

    要求：{characteristics_placeholder}

    请以清晰、易读的格式输出配方，例如：

    鸡尾酒名称：[这里写名称]
    材料：
    - [材料1]：[用量]
    - [材料2]：[用量]
    制作步骤：
    1. [步骤1]
    2. [步骤2]
    酒精度：[酒精饮品/非酒精饮品]
    类别：[类别]
    口味描述：[描述]
    推荐场合：[场合]
    """

    english_generation_prompt_template = """
    You are a creative cocktail bartender.
    Please invent and provide a completely new cocktail recipe based on the following requirements.
    The recipe should include: Cocktail Name, Ingredients (with approximate proportions, e.g., "parts" or "ml"), Preparation Steps, Alcoholic Classification (e.g., "Alcoholic Drink" or "Non-Alcoholic Drink"), Drink Category (e.g., "Classic Cocktail", "Creative Drink"), Taste Profile, and Recommended Occasion.

    Requirements: {characteristics_placeholder}

    Please output the recipe in a clear, readable format, for example:

    Cocktail Name: [Name here]
    Ingredients:
    - [Ingredient 1]: [Amount]
    - [Ingredient 2]: [Amount]
    Preparation Steps:
    1. [Step 1]
    2. [Step 2]
    Alcoholic Classification: [Alcoholic Drink/Non-Alcoholic Drink]
    Category: [Category]
    Taste Profile: [Description]
    Recommended Occasion: [Occasion]
    """

    is_generation_request = False
    chosen_prompt_template = chinese_generation_prompt_template  # 默认使用中文模板
    current_characteristics_placeholder = ""

    # --- 语言和意图判断逻辑 ---
    # 优先检查中文触发词
    for trigger in chinese_triggers:
        if trigger in user_message_lower:
            is_generation_request = True
            chosen_prompt_template = chinese_generation_prompt_template
            # 提取中文冒号后的要求
            if "：" in user_message:
                parts = user_message.split("：", 1)
                if len(parts) > 1:
                    current_characteristics_placeholder = parts[1].strip()
            break  # 找到中文触发词后，跳出循环

    # 如果没有找到中文触发词，则检查英文触发词
    if not is_generation_request:
        for trigger in english_triggers:
            if trigger in user_message_lower:
                is_generation_request = True
                chosen_prompt_template = english_generation_prompt_template
                # 提取英文冒号后的要求
                if ":" in user_message:
                    parts = user_message.split(":", 1)
                    if len(parts) > 1:
                        current_characteristics_placeholder = parts[1].strip()
                break  # 找到英文触发词后，跳出循环

    if is_generation_request:
        # 根据选择的模板，设置默认的特性描述，或者使用用户提供的
        if not current_characteristics_placeholder:
            if chosen_prompt_template == chinese_generation_prompt_template:
                final_characteristics_text = "创造一个独特而美味的鸡尾酒，使其具有吸引力。"
            else:
                final_characteristics_text = "Invent a unique and delicious cocktail."
        else:
            final_characteristics_text = current_characteristics_placeholder

        # 构建最终的生成 Prompt 文本
        generation_prompt_text = chosen_prompt_template.format(characteristics_placeholder=final_characteristics_text)

        # 直接实例化 LLM 进行生成
        llm_for_generation = CustomChatDashScope(
            model="qwen-plus",
            api_key=DASHSCOPE_API_KEY,
            temperature=0.8
        )

        try:
            generated_recipe = llm_for_generation.invoke(generation_prompt_text)
            return {"response": generated_recipe}
        except Exception as e:
            return {"response": f"Error generating new recipe: {str(e)}"}
    else:
        # 如果不是生成配方的请求，则执行标准 RAG 查找
        try:
            rag_chain = create_rag_chain(
                csv_path=str(
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "final_cocktails.csv")),
                dashscope_api_key=DASHSCOPE_API_KEY,
                columns_to_use=["name", "ingredients", "ingredientMeasures", "alcoholic", "category", "glassType",
                                "instructions"]
            )
            response = rag_chain.invoke(user_message)
            return {"response": response}
        except Exception as e:
            return {"response": f"Error retrieving cocktail information: {str(e)}"}