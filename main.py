import asyncio
import os
import sys

from manager import ResearchManager
from agents import set_default_openai_key

async def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    
    set_default_openai_key(api_key)
    query = input("请输入提示词：")
    await ResearchManager().run(query)


if __name__ == "__main__":
    # 检查是否通过streamlit运行
    if 'streamlit' in sys.modules:
        # 如果是通过streamlit运行，不执行main函数
        pass
    else:
        # 如果是直接运行，执行main函数
        asyncio.run(main())
