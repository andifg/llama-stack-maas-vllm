from llama_stack_client.lib.agents.react.agent import ReActAgent
from llama_stack_client.lib.agents.react.agent import get_tool_defs
from llama_stack_client.lib.agents.react.tool_parser import ReActOutput
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client import LlamaStackClient
from termcolor import cprint
import os
from maas_remote_stack.custom_prompts import REACT_AGENT_SYSTEM_PROMPT_TEMPLATE

def create_react_instructions(client, tools):
    """Create ReAct agent instructions by replacing placeholders with tool descriptions."""
    
    # Get tool definitions using the llama-stack client function
    tool_defs = get_tool_defs(client, tools, ())
    
    # tool_names = ", ".join([x["name"] for x in tool_defs])
    # tool_descriptions = "\n".join([f"- {x['name']}: {x}" for x in tool_defs])

    # Format tool names and descriptions
    tool_names = ", ".join([x["name"] for x in tool_defs])
    tool_descriptions = "\n".join([f"- {x['name']}: {x}" for x in tool_defs])
    
    # Replace placeholders in the template
    instruction = REACT_AGENT_SYSTEM_PROMPT_TEMPLATE.replace("<<tool_names>>", tool_names).replace(
        "<<tool_descriptions>>", tool_descriptions
    )
    
    return instruction


stream = True


temperature = float(os.getenv("TEMPERATURE", 0.0))
if temperature > 0.0:
    top_p = float(os.getenv("TOP_P", 0.95))
    strategy = {"type": "top_p", "temperature": temperature, "top_p": top_p}
else:
    strategy = {"type": "greedy"}

max_tokens = int(os.getenv("MAX_TOKENS", 512))

# sampling_params will later be used to pass the parameters to Llama Stack Agents/Inference APIs
sampling_params = {
    "strategy": strategy,
    "max_tokens": max_tokens,
}


client = LlamaStackClient(
    base_url="http://localhost:8321"
)

tools = [
    "builtin::websearch",
]

agent = ReActAgent(
            client=client,
            model="llama-4-scout-17b-16e-w4a16",
            tools=tools,
            instructions=create_react_instructions(client, tools),
            response_format={
                "type": "json_schema",
                "json_schema": ReActOutput.model_json_schema(),
            },
            sampling_params=sampling_params,
            enable_session_persistence=True
        )
user_prompts = [
    # "How are you?",
    # "My name is Pedro",
    # "What is my name?",
    # "search for the last result of Borussia Dortmund!",
    # "search for the current date today",
    "Whats was the last game of FC Bayern Munich?"
]
session_id = agent.create_session("web-session2")
for prompt in user_prompts:
    print("\n"+"="*50)
    cprint(f"Processing user query: {prompt}", "blue")
    print("="*50)
    response = agent.create_turn(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        session_id=session_id,
        stream=stream
    )

    if stream:
        # print("Streaming response:")
        # print("="*100)
        # for chunk in response:
        #     print("*"*100)
        #     print(chunk)
        
        # print("#"*100)

        for log in EventLogger().log(response):
            log.print() 
    else:
        step_printer(response.steps) # print the steps of an agent's response in a formatted way.