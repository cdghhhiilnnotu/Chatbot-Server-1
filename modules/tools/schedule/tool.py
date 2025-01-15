from modules.tools.schedule.utils import *
from langchain_core.tools import tool

@tool
def search_schedule(msv: str, date_to_search: str):
    # "Cancel or Add course has maTC to student has msv"
    "Tra cứu lịch học của sinh viên theo ngày date_to_search và msv"
    tkb = TKB(f"./students/{msv}.csv")

    results = {}
    try:
        results = tkb.find_item_by_date(date_to_search)
        for i in model.stream(f"Thông báo nội dung sau: {str(results)}"):
            yield i
    except:
        # print(f"There are no conent like: {maTC}")
        for i in f"Xảy ra lỗi, đây là tất cả những gì tôi làm được {str(results)}".split(""):
            yield i
