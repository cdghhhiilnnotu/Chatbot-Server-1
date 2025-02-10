from langchain_ollama import OllamaLLM

from modules.function_calls import function_tools
from modules.tools import converse, course_fix, course_cancel, search_schedule, search_exams, reset_query
from modals import HauChain
from modules.routers import SemanticRouter, Route, specials, chitchats
from modules.rags import FAISSRag
from modules.storings import FAISSDatabase
from modules.embeddings import HFEmbedding
from modules.configs import FAISS_PATH, SUB_LLM, MAIN_LLM

sub_model = OllamaLLM(model=SUB_LLM)
main_model = OllamaLLM(model=MAIN_LLM)

modelEmbeding = HFEmbedding()

specialRoute = Route(name='specials', samples=specials)
chitchatRoute = Route(name='chitchats', samples=chitchats)
semantic_router = SemanticRouter(modelEmbeding, routes=[specialRoute, chitchatRoute])

vector_store = FAISSDatabase(modelEmbeding, FAISS_PATH)
rag = FAISSRag(vector_store)

function_tools.append(converse)
function_tools.append(course_fix)
function_tools.append(course_cancel)
function_tools.append(search_schedule)
function_tools.append(search_exams)
function_tools.append(reset_query)

chains = {}

def get_response(user_id, data):
    chat_id = data['chat_id']

    if user_id in chains:
        if chat_id in chains[user_id]:
            user_chain = chains[user_id][chat_id]
            print(f"User {user_id} tiếp tục {chat_id}")
            return user_chain.response(data)

        else:
            user_chain = HauChain(chat_id, user_id, main_model, sub_model, function_tools, semantic_router, rag)
            chains[user_id][chat_id] = user_chain
            print(f"User {user_id} mở {chat_id}")
            return user_chain.response(data)
    else:
        chains[user_id] = {}
        user_chain = HauChain(chat_id, user_id, main_model, sub_model, function_tools, semantic_router, rag)
        chains[user_id][chat_id] = user_chain
        print(f"User {user_id} bắt đầu {chat_id}")
        return user_chain.response(data)
