# test_qwen_connection.py
import os
from dotenv import load_dotenv
import dashscope
from dashscope import Generation

load_dotenv()
dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]

response = Generation.call(
    model="qwen-turbo",
    messages=[{"role": "user", "content": "Say hello in 5 words"}]
)
print(response.output.text)