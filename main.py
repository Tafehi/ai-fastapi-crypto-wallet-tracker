from fastAPI.RestAPI import app

def main():
    print("Hello from ai-fastapi-crypto-wallet-tracker!")


if __name__ == "__main__":
    main()

from dotenv import load_dotenv
import os
from PIL import Image
import json
import asyncio
from mcp_server.client import agent_instance
import streamlit as st
from mcp_server import client

# ---------------------------------------
# Command-line interface (commented out, kept for testing)
# ---------------------------------------
# if __name__ == "__main__":
#     load_dotenv()
#     try:
#         aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
#         aws_secret_key_id = os.getenv("AWS_SECRET_ACCESS_KEY")
#         aws_session_token = os.getenv("AWS_SESSION_TOKEN")
#     except Exception as e:
#         raise RuntimeError(f"Failed to load AWS credentials from environment: {e}")
#     user_prompt = input("Enter your research topic or keywords: ")
#     asyncio.run(
#         client.agent_instance(user_prompt, model="eu.anthropic.claude-sonnet-4-5-20250929-v1:0", aws_access_key_id=aws_access_key_id, 
#                               aws_secret_key_id=aws_secret_key_id, aws_session_token=aws_session_token, 
#                               aws_region="eu-west-1",
#                               temperature=0)
#     )
