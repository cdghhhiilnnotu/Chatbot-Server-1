from langchain_core.tools import tool

@tool
def reset_query(input: str):
    """
    Công cụ sử dụng khi người dùng không xác nhận yêu cầu course_fix, hoặc course_cancel
    """
    return "reset_query"