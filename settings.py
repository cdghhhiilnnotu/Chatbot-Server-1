from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

from modules.function_calls import ToolCalling, function_tools
from modules.configs import  CHATS_PATH
from modules.tools import converse, course_fix, course_cancel, search_schedule, search_exams
from modals import HAUChat
from utils import LLM_NAME, get_history
from processing import histories, sub_model

function_tools.append(converse)
function_tools.append(course_fix)
function_tools.append(course_cancel)
function_tools.append(search_schedule)
function_tools.append(search_exams)
toolcall = ToolCalling(function_tools)
tool_render = toolcall.render()

main_system_prompt = f"""
Sử dụng các công cụ sau đây:
{tool_render}
Dựa vào câu hỏi của người dùng, hãy trả về dưới dạng JSON với
- key 'name' là tên công cụ cần sử dụng
- value 'arguments' là 1 dictionary các tham số đầu vào của công cụ đó.
Hãy tận dụng các công cụ đó một cách hợp lý, nếu không hãy trả lời theo cách thông thường.
"""

main_prompt = ChatPromptTemplate.from_messages(
    [("system", main_system_prompt), ("user", "{input}")]
)

main_chain = main_prompt | sub_model | JsonOutputParser() | toolcall.chain

def get_response(user_id, data):
    # user_id = data['username']
    user_id = user_id
    chat_id = data['chat_id']
    content = data['query']
    global histories
    # Load the chat history from the JSON file
    chats = HAUChat.from_json(chat_id=chat_id, json_path=f'{CHATS_PATH}/{user_id}.json')
    histories.append(get_history(chats.messages))

    print(content)

    # Add the user's message to the chat history
    chats.add_message(sender="User", content=content)

    try:
        response = ""
        # Process the query and collect the response from the chain
        for chunk in main_chain.invoke(data['query']):
            response += str(chunk)  # Accumulate the response chunks
            yield str(chunk)  # Yield each chunk as it's generated

    except Exception as e:
        print(f"Error: {e}")
        response = "Xảy ra lỗi khi đưa ra câu trả lời"
        for chunk in response:
            yield chunk  # Yield the error message

    # Add the bot's response to the chat history
    chats.add_message(sender="AIMAGE", content=response)

    # Save the updated chat history to the JSON file
    chats.to_json(f'{CHATS_PATH}/{user_id}.json')
