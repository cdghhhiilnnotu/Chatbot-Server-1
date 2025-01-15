from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, JsonOutputToolsParser, SimpleJsonOutputParser
from langchain_core.tools import tool
from typing import Generator

from modules.function_calls import ToolCalling, function_tools
from modules.routers import SemanticRouter, Route, specials, chitchats
from modules.embeddings import HFEmbedding
from modules.configs import LLM_NAME, save_json, load_json, update_chat_data
from modules.rags import FAISSRag
from modules.storings import FAISSDatabase
from modules.tools import course_fix, course_cancel, search_schedule

model = OllamaLLM(model=LLM_NAME)

modelEmbeding = HFEmbedding()
specialRoute = Route(name='specials', samples=specials)
chitchatRoute = Route(name='chitchats', samples=chitchats)
semanticRouter = SemanticRouter(modelEmbeding, routes=[specialRoute, chitchatRoute])

vector_store = FAISSDatabase(modelEmbeding, './sources/database/faiss/v0')
rag = FAISSRag(vector_store)
history = []

@tool
def converse(query: str) -> str:
    "Trả lời cuộc hội thoại theo ngôn ngữ tự nhiên"
    print("converse")
    guidedRoute = semanticRouter.guide(query)[1]
    if guidedRoute == 'specials':
        print("Guide to RAGs")
        rag_context = rag.to_text(query)
        context = f"""\nĐây là lịch sử cuộc trò chuyện:\n{history}\nVới các thông tin sau (nếu có):\n{rag_context}.\nHãy trả lời câu hỏi:\n{query}"""
        # response = model.invoke(context)
        return model.stream(context)
    else:
        print("Guide to LLMs")
        context = f"""\nĐây là lịch sử cuộc trò chuyện:\n{history}.\nHãy trả lời câu hỏi:{query}"""
        # response = model.invoke(query
        return model.stream(context)
    

function_tools.append(converse)
function_tools.append(course_fix)
function_tools.append(course_cancel)
function_tools.append(search_schedule)

toolcall = ToolCalling(function_tools)
tool_render = toolcall.render()


system_prompt = f"""
Dựa vào câu hỏi đầu vào của người dùng, 
trả về dưới dạng JSON với
key 'name' là tên công cụ
value 'arguments' là 1 dictionary các tham số đầu vào.
Hãy sử dụng các công cụ sau đây:
{tool_render}
Trả lời câu hỏi ngắn gọn nhất có thể. Nếu không thể trả lời được câu hỏi hãy nói rằng không biết.
Hãy nhớ, bạn là trợ lý đắc lực của Phòng Đào tạo Trường Đại học Kiến Trúc Hà Nội trong việc hỗ trợ trả lời các câu hỏi của sinh viên.
Tên bạn là AIMAGE, hãy nhớ điều đó.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", "{input}")]
)

chain = prompt | model | JsonOutputParser() | toolcall.chain

def chat(data):
    update_chat_data("chats.json", data)
    global history 
    history = data['history']
    # print(data)
    for chunk in chain.invoke(data['query']):
        yield str(chunk)
    data['history'] = history
    update_chat_data("chats.json", data)
    
