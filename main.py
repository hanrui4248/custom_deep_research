import asyncio
import os

from manager import ResearchManager
from agents import set_default_openai_key

async def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    
    set_default_openai_key(api_key)
    query = input("请输入提示词：")
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())
