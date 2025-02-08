from langchain_core.tools import tool

from modals import TKB
from modules.configs import SCHEDULES_PATH
from processing import sub_chain, queries

@tool
def reject_query(input: str):
    "Khi người dùng không đồng ý xác nhận thực hiện yêu cầu hủy hoặc thay đổi học phần trong input."
    print("Từ chối yêu cầu")

    global sub_chain

    try:
        queries.pop(queries.keys()[-1])
        query = f"""
Đã ngừng yêu cầu trong {input}
"""
        for i in sub_chain.stream(query):
            yield i
    except Exception as e:
        print(e)

        query = f"""
Xảy ra lỗi khi ngừng yêu cầu trong {input}
"""
        for i in sub_chain.stream(query):
            yield i