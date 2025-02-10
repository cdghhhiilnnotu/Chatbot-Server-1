from langchain_core.tools import tool
@tool
def course_fix(maTC: str):
    """
    Công cụ sử dụng để thay đổi, đăng kí học phần có mã tín chỉ maTC cho sinh viên.
    """
    return "course_fix"

@tool
def course_cancel(maTC: str):
    """
    Công cụ sử dụng để hủy học phần có mã tín chỉ maTC cho sinh viên.
    """
    return "course_cancel"