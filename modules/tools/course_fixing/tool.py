from modules.tools.course_fixing.utils import *
from langchain_core.tools import tool
import sys
sys.path.append('./modules/tools/course_fixing')

@tool
def course_fix(msv: str, maTC: str):
    # "Cancel or Add course has maTC to student has msv"
    "Thay đổi học phần có mã tín chỉ maTC vào thời khóa biểu của sinh viên có mã sinh viên msv"
    tkb = TKB(f'./modules/tools/course_fixing/schedules/{msv}.csv')
    hp = MonHoc(f'./modules/tools/course_fixing/courses/{maTC}.csv')

    try:
        tkb.delete_content(maTC)
    except:
        print(f"There are no conent like: {maTC}")
    
    available_lopTC = find_available(hp.get_days(), tkb.get_days())
    # print(available_lopTC)
    print(available_lopTC.keys())
    if len(available_lopTC):
        available_name = list(available_lopTC.keys())[0]
        available_hp = hp.get_content()[available_name]
        tkb.add_content({available_name:available_hp})
        hp.success_submit()
        for i in "Cập nhật lịch học thành công!":
            yield i
    for i in "Có lỗi xảy ra!":
        yield i

@tool
def course_cancel(msv: str, maTC: str):
    # "Cancel or Add course has maTC to student has msv"
    "Hủy học phần có mã tín chỉ maTC vào thời khóa biểu của sinh viên có mã sinh viên msv"
    tkb = TKB(f'./modules/tools/course_fixing/schedules/{msv}.csv')

    try:
        tkb.delete_content(maTC)
        for i in "Cập nhật lịch học thành công!":
            yield i
    except:
        # print(f"There are no conent like: {maTC}")
        for i in "Có lỗi xảy ra!":
            yield i

if __name__ == "__main__":
    course_fix('2055010051', 'TH4309')


