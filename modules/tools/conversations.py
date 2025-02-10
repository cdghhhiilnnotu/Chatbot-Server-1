from langchain_core.tools import tool

@tool
def converse(query: str) -> str:
    """
    Công cụ sử dụng để trả lời các câu hỏi query thông thường.
    """
    return "converse"