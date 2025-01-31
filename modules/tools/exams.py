from langchain_core.tools import tool

from modals import LichThi
from modules.configs import EXAMS_PATH
from processing import sub_chain

@tool
def search_exams(msv: str, date_to_search: str):
    "Tra cứu lịch thi của sinh viên có mã sinh viên msv theo ngày date_to_search."
    print("Sử dụng tool Tra cứu lịch thi.")

    global sub_chain
    results = {}
    try:
        lichthi = LichThi(f"{EXAMS_PATH}/{msv}.csv")
        results = lichthi.find_exams_by_date(date_to_search)
        for i in sub_chain.stream(f"Thông báo lịch thi ngày {date_to_search}: {str(results)}"):
            yield i
    except Exception as e:
        print(e)
        for i in f"Xảy ra lỗi, đây là tất cả những gì tôi làm được {str(results)}".split(""):
            yield i