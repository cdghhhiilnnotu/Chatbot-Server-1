from langchain_core.tools import tool

from modals import TKB, MonHoc, find_available
from modules.configs import SCHEDULES_PATH, ACTIVE_COURSES_PATH

@tool
def course_fix(msv: str, maTC: str):
    "Thay đổi học phần sẽ gây ảnh hưởng trực tiếp đến thời khóa biểu của sinh viên, hãy xác nhận là sinh viên muốn thực hiện."
    "Thay đổi học phần có mã tín chỉ maTC vào thời khóa biểu của sinh viên có mã sinh viên msv."
    print("Sử dụng tool Thay đổi học phần.")

    tkb = TKB(f'{SCHEDULES_PATH}/{msv}.csv')
    hp = MonHoc(f'{ACTIVE_COURSES_PATH}/{maTC}.csv')

    try:
        tkb.delete_content(maTC)
    except:
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
        for i in "Có lỗi xảy ra!":
            yield i

@tool
def course_cancel(msv: str, maTC: str):
    "Hủy học phần sẽ gây ảnh hưởng trực tiếp đến thời khóa biểu của sinh viên, hãy xác nhận là sinh viên muốn thực hiện."
    "Hủy học phần có mã tín chỉ maTC vào thời khóa biểu của sinh viên có mã sinh viên msv."
    print("Sử dụng tool Hủy học phần.")
    tkb = TKB(f'{SCHEDULES_PATH}/{msv}.csv')

    try:
        tkb.delete_content(maTC)
        for i in "Cập nhật lịch học thành công!":
            yield i
    except:
        for i in "Có lỗi xảy ra!":
            yield i