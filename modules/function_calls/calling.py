import sys
sys.path.append('../../../demo-5')

import inspect
from operator import itemgetter
from langchain.tools.render import render_text_description


class ToolCalling():

    def __init__(self, tools):
        self.functions = tools

    def render(self):
        return render_text_description(self.functions)
    
    def chain(self, model_output):
        func_map = {func.name: func for func in self.functions}
        chosen_func = func_map[model_output["name"]]
        return itemgetter("arguments") | chosen_func

if __name__ == '__main__':
    from langchain_ollama import OllamaLLM
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from modules.function_calls import function_tools

    model = OllamaLLM(model='llama3.1')

    toolcall = ToolCalling(function_tools)
    tool_render = toolcall.render()


    print(tool_render)

    system_prompt = f"""You are an assistant that has access to the following set of tools.
    Here are the names and descriptions for each tool:
    {tool_render}
    Given the user input, return the name and input of the tool to use.
    Return your response as a JSON blob with 'name' and 'arguments' keys.
    The value associated with the 'arguments' key should be a dictionary of parameters.
    Answer the question as short as possible."""

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{input}")]
    )

    chain = prompt | model | JsonOutputParser() | toolcall.chain

    response = chain.invoke("Chào bạn")

    print(response)

