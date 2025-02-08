from langchain_core.tools import tool

from modals import TKB, MonHoc, find_available
from modules.configs import SCHEDULES_PATH, ACTIVE_COURSES_PATH
from processing import queries, sub_chain
from utils import load_query

@tool
def course_fix(maTC: str, msv: str):
    "Thay đổi học phần có mã tín chỉ maTC vào thời khóa biểu của sinh viên có mã sinh viên msv."
    print("Sử dụng tool Thay đổi học phần.")
    if load_query(queries, 'course_fix'):
        tkb = TKB(f'{SCHEDULES_PATH}/{msv}.csv')
        hp = MonHoc(f'{ACTIVE_COURSES_PATH}/{maTC}.csv')

        try:
            tkb.delete_content(maTC)
        except Exception as e:
            print(e)
            for i in "Có lỗi xảy ra!":
                yield i
        
        try:
            available_lopTC = find_available(hp.get_days(), tkb.get_days())
            if len(available_lopTC):
                available_name = list(available_lopTC.keys())[0]
                available_hp = hp.get_content()[available_name]
                tkb.add_content({available_name:available_hp})
                hp.success_submit()
                for i in "Cập nhật lịch học thành công!":
                    yield i
        except Exception as e:
            print(e)
            query = f"""
Khi cố gắng thay đổi lịch học của sinh viên có mã sinh viên {msv}, đã phát hiện lỗi 
{e}
"""
            for i in sub_chain.stream(query):
                yield i
    else:
        queries['course_fix'] = f"Thay đổi học phần có mã tín chỉ {maTC} vào thời khóa biểu của sinh viên có mã sinh viên {msv}."
        for i in sub_chain.stream("Thay đổi lịch học sẽ ảnh hưởng trực tiếp đến thời khóa biểu của bạn, hãy xác nhận rằng bạn muốn thực hiện nó"):
            yield i

@tool
def course_cancel(msv: str, maTC: str):
    "Hủy học phần có mã tín chỉ maTC vào thời khóa biểu của sinh viên có mã sinh viên msv."
    print("Sử dụng tool Hủy học phần.")
    if load_query(queries, 'course_cancel'):
        tkb = TKB(f'{SCHEDULES_PATH}/{msv}.csv')

        try:
            tkb.delete_content(maTC)
            for i in "Cập nhật lịch học thành công!":
                yield i
        except Exception as e:
            print(e)
            query = f"""
    Khi cố gắng thay đổi lịch học của sinh viên có mã sinh viên {msv}, đã phát hiện lỗi 
    {e}
    """
            for i in sub_chain.stream(query):
                yield i
    else:
        queries['course_cancel'] = f"Hủy học phần có mã tín chỉ {maTC} vào thời khóa biểu của sinh viên có mã sinh viên {msv}."
        for i in sub_chain.stream("Thay đổi lịch học sẽ ảnh hưởng trực tiếp đến thời khóa biểu của bạn, hãy xác nhận rằng bạn muốn thực hiện nó"):
            yield i