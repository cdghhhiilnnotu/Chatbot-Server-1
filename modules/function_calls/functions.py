from langchain_core.tools import tool
from datetime import datetime
import pytz
from processing import sub_chain

@tool
def time_now():
    "Truy vấn thời gian hiện tại"
    vn_timezone = pytz.timezone("Asia/Ho_Chi_Minh")  # Múi giờ Việt Nam
    vn_time = datetime.now(vn_timezone)
    current_time = vn_time.strftime("%Y-%m-%d %H:%M:%S")
    for i in sub_chain.stream(f"Trả lời truy vấn về thời gian hiện tại: {current_time}"):
        yield i 

function_tools = [time_now]

