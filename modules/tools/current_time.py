from langchain_core.tools import tool

@tool
def current_time(query: str):
    "Công cụ sử dụng để tra cứu thời gian hiện tại."
    return "current_time"