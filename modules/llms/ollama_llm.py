from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from modules.llms import BaseLLM

class OllamaModel(BaseLLM):

    def __init__(self, name, toolcall):
        super().__init__(name, toolcall)
        self.system_prompt = f"""
Dựa vào câu hỏi đầu vào của người dùng, 
trả về dưới dạng JSON với
key 'name' là tên công cụ
value 'arguments' là 1 dictionary các tham số đầu vào.
Hãy sử dụng các công cụ sau đây:
{toolcall.render()}
Trả lời câu hỏi ngắn gọn nhất có thể. Nếu không thể trả lời được câu hỏi hãy nói rằng không biết.
Hãy nhớ, bạn là trợ lý đắc lực của Phòng Đào tạo Trường Đại học Kiến Trúc Hà Nội trong việc hỗ trợ trả lời các câu hỏi của sinh viên.
"""
        self.model = OllamaLLM(model=name)
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "{input}")]
        )
        self.chain = self.prompt | self.model | JsonOutputParser() | toolcall.chain

