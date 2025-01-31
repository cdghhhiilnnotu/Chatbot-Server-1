from langchain_core.tools import tool

from modals import TKB
from modules.configs import SCHEDULES_PATH
from processing import sub_chain

@tool
def search_schedule(msv: str, date_to_search: str):
    "Tra cứu lịch học của sinh viên có mã sinh viên msv theo ngày date_to_search."
    print("Sử dụng tool Tra cứu lịch học.")

    global sub_chain

    tkb = TKB(f"{SCHEDULES_PATH}/{msv}.csv")
    results = {}
    try:
        results = tkb.find_item_by_date(date_to_search)
        for i in sub_chain.stream(f"Thông báo lịch học ngày {date_to_search}: {str(results)}"):
            yield i
    except Exception as e:
        print(e)
        for i in f"Xảy ra lỗi, đây là tất cả những gì tôi làm được {str(results)}".split(""):
            yield i