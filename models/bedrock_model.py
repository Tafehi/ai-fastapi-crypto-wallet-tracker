import os
import boto3
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv


class BedrockLLM:
    def __init__(
        self,
        model: str,
        temperature: float,
        aws_access_key_id: str,
        aws_secret_key_id: str,
        aws_session_token: str,
        aws_region: str,
    ):
        load_dotenv()
        self._model = model
        self._temperature = temperature
        self._access_key = aws_access_key_id
        self._secret_key = aws_secret_key_id
        self._session_token = aws_session_token
        self._region = aws_region

    def __check_credentials(self):
        try:
            if not self._access_key or not self._secret_key or not self._session_token:
                raise ValueError("AWS credentials are not set.")
            if not self._model:
                raise ValueError("LLM_MODEL is not set.")
        except Exception as e:
            raise RuntimeError(f"Credential check failed: {e}")
        
    def get_llm(self):
        self.__check_credentials()
        bedrock_client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            aws_session_token=self._session_token,
            region_name=self._region,
        )

        return ChatBedrockConverse(
            model_id=self._model,
            client=bedrock_client,
            temperature=self._temperature,
        )
