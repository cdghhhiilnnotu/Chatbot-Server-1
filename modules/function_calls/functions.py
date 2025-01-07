from langchain_core.tools import tool

@tool
def add(first: float, second: float) -> float:
    # "Add two integers."
    "Cộng 2 số thực"
    for i in str(first + second):
        yield i 

@tool
def multiply(first: float, second: float) -> float:
    # """Multiply two integers together."""
    "Nhân 2 số thực"
    for i in str(first + second):
        yield i 

function_tools = [add, multiply]

