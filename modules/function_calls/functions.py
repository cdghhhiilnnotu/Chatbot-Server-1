from langchain_core.tools import tool

@tool
def current_time():
    "Truy vấn thời gian hiện tại"
    return "current_time"

function_tools = [current_time]

