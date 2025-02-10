from langchain_core.tools import tool

@tool
def search_schedule(date_to_search: str):
    "Công cụ sử dụng để tra cứu lịch thi của sinh viên theo ngày date_to_search có dạng DD/MM/YYYY."
    return "search_schedule"