from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

from modules.routers import SemanticRouter, Route, specials, chitchats
from modules.rags import FAISSRag
from modules.storings import FAISSDatabase
from modules.embeddings import HFEmbedding
from modules.configs import FAISS_PATH
from utils import  LLM_NAME

sub_model = OllamaLLM(model=LLM_NAME)

sub_system_prompt = f"""
Bạn là trợ lý đắc lực của Phòng Đào tạo Trường Đại học Kiến Trúc Hà Nội trong việc hỗ trợ giao tiếp với sinh viên.
Tên của bạn là AIMAGE.
Hãy tận dụng các thông tin được cung cấp và trả lời câu hỏi 1 cách ngắn gọn và chính xác nhất có thể.
Nếu không biết câu trả lời hãy trả lời là không biết.
"""

modelEmbeding = HFEmbedding()

sub_prompt = ChatPromptTemplate.from_messages(
    [("system", sub_system_prompt), ("user", "{input}")]
)

sub_chain = sub_prompt | sub_model

specialRoute = Route(name='specials', samples=specials)
chitchatRoute = Route(name='chitchats', samples=chitchats)
semanticRouter = SemanticRouter(modelEmbeding, routes=[specialRoute, chitchatRoute])

vector_store = FAISSDatabase(modelEmbeding, FAISS_PATH)
rag = FAISSRag(vector_store)
histories = []