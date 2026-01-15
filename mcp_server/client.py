import os
import traceback
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from models.bedrock_model import BedrockLLM
from prompts.prompt import task_prompt, security_prompt



# Load environment variables
load_dotenv()


async def agent_instance(
    user_prompt: str,
    model: str,
    temperature: float,
    aws_access_key_id: str,
    aws_secret_key_id: str,
    aws_session_token: str,
    aws_region: str,
) -> str:
    """
    Creates and runs an agent instance with MCP tools.

    Args:
        user_prompt (str): The user's research query
        model (str): The LLM model to use (e.g., 'anthropic.claude-3-sonnet-20240229-v1:0', 'anthropic.claude-3-haiku-20240307-v1:0', 'amazon.titan-text-express-v1')
        temperature (float): Temperature for response generation (0.0 - 1.0)
        timeout (int): Timeout for API calls in seconds

    Returns:
        str: The agent's response
    """
    # Input validation
    try:
        if not user_prompt or not isinstance(user_prompt, str):
            raise ValueError("user_prompt must be a non-empty string")

        if not model or not isinstance(model, str):
            raise ValueError("model must be a non-empty string")

        if not isinstance(temperature, (int, float)) or not (0.0 <= temperature <= 1.0):
            raise ValueError("temperature must be a number between 0.0 and 1.0")

    except Exception as e:
        print(f"Input validation error: {e}")
        raise

    # Define all tools in one MultiServerMCPClient config
    mcp_tools = MultiServerMCPClient(
        {

            # "math": {
            #     "command": "python",
            #     "args": ["tools/math_tools.py"],
            #     "transport": "stdio",
            # },
        }
    )
    print("Connecting to MCP tools and agents")  # Initialize the MCP client

    # await is a part of async function to wait for the MCP client to be ready
    try:
        tools = await mcp_tools.get_tools()
    except Exception as e:
        print(f"Error getting tools from MCP client: {e}")
        traceback.print_exception(e)
        raise RuntimeError("Failed to get tools from MCP client.")

    print(f"Loaded Tools: {[tool.name for tool in tools]}")

    ## Initialize the Bedrock LLM with provided parameters
    llm = BedrockLLM(
        model=model,
        temperature=temperature,
        aws_access_key_id=aws_access_key_id,
        aws_secret_key_id=aws_secret_key_id,
        aws_session_token=aws_session_token,
        aws_region=aws_region,
    )
    ## Create the agent with the specified LLM and tools
    agent = create_react_agent(
        model=llm.get_llm(),
        tools=tools,
    )  # Create the agent with the LLM and tools

    # Combine task and security prompts to ensure credential protection
    system_prompt = task_prompt() + "\n\n" + security_prompt()

    resposne = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        }
    )

    print("Agent response received")
    print(f"Agent Response: {resposne['messages'][-1].content}")
    return resposne["messages"][-1].content
