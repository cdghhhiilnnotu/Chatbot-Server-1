from langchain_core.tools import tool
from processing import sub_chain, semanticRouter, rag, histories

@tool
def converse(query: str) -> str:
    "Trả lời các câu hỏi thông thường."
    global semanticRouter
    global rag
    global histories

    global sub_chain
    history = histories[-1]
    print(history)
    guidedRoute = semanticRouter.guide(query)[1]
    if guidedRoute == 'specials':
        print("Sử dụng RAG")

        rag_context = rag.to_text(query)
        context = f"""
Đây là lịch sử cuộc trò chuyện:
{history}
Với các thông tin sau (nếu có):
{rag_context}
Hãy trả lời câu hỏi:
{query}
"""
        return sub_chain.stream(context)
    else:
        print("Sử dụng LLM.")

        context = f"""
Đây là lịch sử cuộc trò chuyện:
{history}
Hãy nhớ nó và trả lời câu hỏi:
{query}
"""
        return sub_chain.stream(context)