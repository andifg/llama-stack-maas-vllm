from llama_stack_client.lib.agents.react.agent import ReActAgent
from llama_stack_client.lib.agents.react.tool_parser import ReActOutput
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client import LlamaStackClient
import json
from json import JSONDecodeError
from rich.pretty import pprint
from termcolor import cprint
import os


def step_printer(steps):
    """
    Print the steps of an agent's response in a formatted way.
    Note: stream need to be set to False to use this function.
    Args:
    steps: List of steps from an agent's response.
    """
    for i, step in enumerate(steps):
        step_type = type(step).__name__
        print("\n"+"-" * 10, f"📍 Step {i+1}: {step_type}","-" * 10)
        if step_type == "ToolExecutionStep":
            print("🔧 Executing tool...")
            try:
                pprint(json.loads(step.tool_responses[0].content))
            except (TypeError, JSONDecodeError):
                # tool response is not a valid JSON object
                pprint(step.tool_responses[0].content)
        else:
            if step.api_model_response.content:
                print("🤖 Model Response:")
                cprint(f"{step.api_model_response.content}\n", "magenta")
            elif step.api_model_response.tool_calls:
                tool_call = step.api_model_response.tool_calls[0]
                print("🛠️ Tool call Generated:")
                cprint(f"Tool call: {tool_call.tool_name}, Arguments: {json.loads(tool_call.arguments_json)}", "magenta")
    print("="*10, "Query processing completed","="*10,"\n")


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

print("Providers:")
print(client.providers.list())
print("After providers")
print("Tools:")
print(client.tools.list())
print("After tools")

agent = ReActAgent(
            client=client,
            model="llama-4-scout-17b-16e-w4a16",
            tools=[],
            response_format={
                "type": "json_schema",
                "json_schema": ReActOutput.model_json_schema(),
            },
            sampling_params=sampling_params,
            enable_session_persistence=True
        )
user_prompts = [
    "How are you?",
    "My name is Pedro",
    "What is my name?"
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
        for log in EventLogger().log(response):
            log.print()
    else:
        step_printer(response.steps) # print the steps of an agent's response in a formatted way.