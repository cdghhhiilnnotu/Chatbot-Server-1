from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime
from langchain.output_parsers import OutputFixingParser
from langchain_core.exceptions import OutputParserException
import pytz

from modules.function_calls import ToolCalling
from modals import TKB, MonHoc, find_available
from modals import LichThi
from modals.hau_chats import HAUChat
from modules.configs import EXAMS_PATH, SCHEDULES_PATH, ACTIVE_COURSES_PATH, CHATS_PATH
from utils import load_query


class HauChain:

    def __init__(self, chat_id, user_id, main_model, sub_model, tool_refs, semantic_router, rag):
        self.user_id = user_id
        self.chat_id = chat_id
        self.main_model = main_model
        self.sub_model = sub_model
        self.tool_refs = tool_refs
        self.semantic_router = semantic_router
        self.rag = rag
        self.sub_chain = None
        self.main_chain = None
        self.queries = {}
        self.histories = []
        self.setup_tools()
        self.setup_chain()

    def setup_tools(self):
        self.toolcall = ToolCalling(self.tool_refs)
        self.tool_render = self.toolcall.render()
        # print(self.tool_render)

    def converse(self, query: str):
        print(query)
        guidedRoute = self.semantic_router.guide(query)[1]
        if guidedRoute == 'specials':
            print("1-Sử dụng RAG")

            rag_context = self.rag.to_text(query)
            context = f"""
Với các thông tin sau (nếu có):
{rag_context}
Và lịch sử trò chuyện:
{self.histories}
Hãy trả lời câu hỏi:
{query}
    """
            for i in self.sub_chain.stream(context):
                yield i
        else:
            print("2-Sử dụng LLM.")

            context = f"""
Với lịch sử trò chuyện:
{self.histories}
Hãy trả lời câu hỏi:
{query}
"""         
            print(context)
            print(self.sub_chain)
            print(self.sub_chain.invoke(context))
            for i in self.sub_chain.stream(context):
                yield i

    def course_fix(self, maTC: str):
        print("3-Tool Course Fix")
        if load_query(self.queries, 'course_fix'):
            tkb = TKB(f'{SCHEDULES_PATH}/{self.user_id}.csv')
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
    Khi cố gắng thay đổi lịch học của sinh viên có mã sinh viên {self.user_id}, đã phát hiện lỗi 
    {e}
    """
                for i in self.sub_chain.stream(query):
                    yield i
        else:
            self.queries['course_fix'] = f"Thay đổi học phần có mã tín chỉ {maTC} vào thời khóa biểu của sinh viên có mã sinh viên {self.user_id}."
            for i in self.sub_chain.stream("Thay đổi lịch học sẽ ảnh hưởng trực tiếp đến thời khóa biểu của sinh viên, hãy xác nhận rằng sinh viên muốn thực hiện nó"):
                yield i

    def course_cancel(self, maTC: str):
        print("4-Tool Course Cancel")
        if load_query(self.queries, 'course_cancel'):
            tkb = TKB(f'{SCHEDULES_PATH}/{self.user_id}.csv')

            try:
                tkb.delete_content(maTC)
                for i in "Cập nhật lịch học thành công!":
                    yield i
            except Exception as e:
                print(e)
                query = f"""
        Khi cố gắng thay đổi lịch học của sinh viên có mã sinh viên {self.user_id}, đã phát hiện lỗi 
        {e}
        """
                for i in self.sub_chain.stream(query):
                    yield i
        else:
            self.queries['course_cancel'] = f"Hủy học phần có mã tín chỉ {maTC} vào thời khóa biểu của sinh viên có mã sinh viên {self.user_id}."
            for i in self.sub_chain.stream("Thay đổi lịch học sẽ ảnh hưởng trực tiếp đến thời khóa biểu của sinh viên, hãy xác nhận rằng sinh viên muốn thực hiện nó"):
                yield i

    def search_exams(self, date_to_search: str):
        print("5-Tool Search Exams")
        results = {}
        try:
            lichthi = LichThi(f"{EXAMS_PATH}/{self.user_id}.csv")
            results = lichthi.find_exams_by_date(date_to_search)
            for i in self.sub_chain.stream(f"Thông báo lịch thi ngày {date_to_search}: {str(results)}"):
                yield i
        except Exception as e:
            for i in self.sub_chain.stream(e):
                yield i

    def search_schedule(self, date_to_search: str):
        print("6-Tool Search Schedule")
        tkb = TKB(f"{SCHEDULES_PATH}/{self.user_id}.csv")
        results = {}
        try:
            results = tkb.find_item_by_date(date_to_search)
            for i in self.sub_chain.stream(f"Thông báo lịch học ngày {date_to_search}: {str(results)}"):
                yield i
        except Exception as e:
            print(e)
            query = f"""
    Khi cố gắng truy lịch học ngày {date_to_search}: {str(results)}, đã phát hiện lỗi 
    {e}
    """
            for i in self.sub_chain.stream(query):
                yield i

    def reset_query(self, query_type):
        print("7-Tool Reset Query")
        if query_type in self.queries.keys():
            self.queries.pop(list(self.queries.keys()).index(query_type))
        for i in self.sub_chain.stream(f"Yêu cầu đã được xóa khỏi hàng chờ."):
            yield i 

    def current_time(self):
        print("8-Tool Current Time")
        vn_timezone = pytz.timezone("Asia/Ho_Chi_Minh")  # Múi giờ Việt Nam
        vn_time = datetime.now(vn_timezone)
        current_time = vn_time.strftime("%Y-%m-%d %H:%M:%S")
        for i in self.sub_chain.stream(f"Trả lời truy vấn về thời gian hiện tại: {current_time}."):
            yield i 

    def setup_chain(self):
        # print(self.tool_render)
        main_system = f"""
Sử dụng các công cụ sau đây:
{self.tool_render}
Bắt buộc phải trả về dưới dạng JSON với
- key 'name' là tên công cụ cần sử dụng
- value 'arguments' là 1 dictionary các tham số đầu vào của công cụ đó theo thứ tự được định nghĩa trong công cụ.
Đọc kỹ hướng dẫn sử dụng các công cụ để đưa câu trả lời về dạng JSON phù hợp
"""
        # print(main_system)
        main_prompt = ChatPromptTemplate.from_messages(
            [("system", main_system), ("user", "{input}")]
        )
        
        self.main_chain = main_prompt | self.main_model | JsonOutputParser()

        sub_system = f"""
Bạn là trợ lý đắc lực của Phòng Đào tạo Trường Đại học Kiến Trúc Hà Nội trong việc hỗ trợ giao tiếp với sinh viên.
Tên của bạn là AIMAGE.
Hãy tận dụng các thông tin được cung cấp và trả lời câu hỏi 1 cách ngắn gọn và chính xác nhất có thể.
Nếu không biết câu trả lời hãy trả lời là không biết.
Không được trả về câu trả lời rỗng.
"""
        sub_prompt = ChatPromptTemplate.from_messages(
            [("system", sub_system), ("user", "{input}")]
        )
        
        self.sub_chain = sub_prompt | self.sub_model
    
    def response(self, data):
        content = data['query']
        # Load the chat history from the JSON file
        chats = HAUChat.from_json(chat_id=self.chat_id, json_path=f'{CHATS_PATH}/{self.user_id}.json')

        self.histories = chats.messages
        chats.add_message(sender="User", content=content)
        response = ""
        query = f"""
Hãy xem lịch sử trò chuyện:
{self.histories}
Hãy trả lời câu hỏi:
{content}
Hãy trả lời câu hỏi ngắn nhất có thể.
"""
        try:
            select_function = self.main_chain.invoke(query)
            if select_function['name'] == "converse":
                for i in self.converse(content):
                    response += i
                    yield i
            if select_function['name'] == "course_fix":
                for i in self.course_fix(select_function['arguments'][list(select_function['arguments'].keys())[0]]):
                    response += i
                    yield i
            if select_function['name'] == "course_cancel":
                for i in self.course_cancel(select_function['arguments'][list(select_function['arguments'].keys())[0]]):
                    response += i
                    yield i
            if select_function['name'] == "search_exams":
                for i in self.search_exams(select_function['arguments'][list(select_function['arguments'].keys())[0]]):
                    response += i
                    yield i
            if select_function['name'] == "search_schedule":
                for i in self.search_schedule(select_function['arguments'][list(select_function['arguments'].keys())[0]]):
                    response += i
                    yield i
            if select_function['name'] == "reset_query":
                for i in self.reset_query(select_function['arguments'][list(select_function['arguments'].keys())[0]]):
                    response += i
                    yield i
            if select_function['name'] == "current_time":
                for i in self.current_time():
                    response += i
                    yield i
        except OutputParserException as e:
            for i in self.converse(content):
                response += i
                yield i
        except Exception as e:
            print(e)
            response = "Xin lỗi, tôi không thể trả lời lúc này."
            for i in response:
                yield i

        chats.add_message(sender="AIMAGE", content=response)

        # Save the updated chat history to the JSON file
        chats.to_json(f'{CHATS_PATH}/{self.user_id}.json')