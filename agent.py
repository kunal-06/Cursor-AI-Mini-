from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import os
import subprocess
from langchain_core.tools import tool
from pathlib import Path
from dotenv import load_dotenv
import json
load_dotenv()

SANDBOX_DIR = Path("D:\Project\Cursor_mini\work") .resolve()
SANDBOX_DIR.mkdir(exist_ok=True)

memory = MemorySaver()
gemini_model = init_chat_model(model="gemini-2.0-flash",model_provider="google_genai")


   
prompt = r'''
            you are a helpful assistent,
            and you have some tools which you can use accourding user query,
            you can access the memory of privious invoke history and accordingly complete the next process,
            if any error encounter then solve that error 
            return the result in specific formate 
                example: '{"status": Completed/Panding/Done/Error, "output":LLm responce}'
            
            if task is big then divide it into a small parts, and perform it sequentially, and mark status Panding until it's not completed or any error ouccer,
            each invoke do perticular part of task.
            example:
               message : create a html file in that create a button with animation and triger a tost message when click 

                first invoke
                    task 1: create html file
                    status: panding
               
                Second invoke
                    task 2: create css file
                    status: panding
                Third invoke
                    task 3: create js file
                    status: completed
             
         '''


def safe_path(filename: str) -> Path:
    """Resolve path and ensure it's inside SANDBOX_DIR."""
    path = (SANDBOX_DIR / filename).resolve()
    if not str(path).startswith(str(SANDBOX_DIR)):
        raise ValueError("Access outside sandbox is not allowed.")
    return path


@tool
def create_file(filename : str,content : str)-> str:
    """
    Create or Overwrite a file with given content inside work folder
    """
    try:
        path = safe_path(filename)
        with open(path,'w',encoding='utf-8') as f:
            f.write(content)
        return f"File Created at {path}"
    except Exception as e:
        return f"Error: {e}"
    
@tool
def list_files()-> str:
    """
    List all files in the work folder
    """
    try: 
        files = [p.name for p in SANDBOX_DIR.iterdir() if p.is_file()]
        return "\n".join(files) if files else "no file found" 
    except Exception as e:
        return f"Error {e}"
    
@tool
def read_file(filename : str)-> str:
    """
      Read file within given content inside sendbox
    """
    try:
        path = safe_path(filename)
        with open(path,'r') as f:
            return f.read()
    except Exception as e:
        return f"Error {e}"


@tool
def command_exec(command : list[str])->str:
    """
        Execute Command in windows cmd and return the result 
        example: input given [ping,www.google.com]
                 tool will execute that command and return the result                
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=False ,
            cwd=SANDBOX_DIR
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

agent = create_react_agent(model=gemini_model,tools=[read_file,list_files,create_file,command_exec],checkpointer=memory,prompt=prompt)
config = {"configurable": {"thread_id": "1111"}}

def invoke_agent(message:str):   
    res = agent.invoke({"messages": message},config)
    result = res["messages"][-1].content    
    return result


from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage

# Define schema for state
class AgentState(TypedDict):
    messages: list[AnyMessage]
    status: Literal["Pending", "Completed", "Error"]

# Build workflow
workflow = StateGraph(AgentState)

def should_continue(state: AgentState) -> bool:
    return state["status"] != "Completed"

# Add agent node
workflow.add_node("agent", agent)
workflow.set_entry_point("agent")

# Add conditional loop
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {True: "agent", False: END}
)

# Compile
app = workflow.compile()

import json
while True: 
    msg = input("Write Hear : ")
    result = invoke_agent(msg)
    result = result.replace("```","")
    result = result.replace("\n","")
    result = result.replace("json","")
    start_index = result.find("{")
    end_index = result.rfind("}")
    result = result[start_index:end_index+1]
    print()
    print("*"*10," AI Responce ","*"*10)
    print(result)
    result = json.loads(result)

    if result['status'] in ["Completed","Error"]:
        print(result['output'])
        break


