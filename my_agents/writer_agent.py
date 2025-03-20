# Agent used to synthesize a final report from the individual summaries.
from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "你是一位资深信息整合专家,负责根据用户需求用中文生成整合结果。"
    "你将获得所有原始的搜索问题,以及研究助理完成的初步总结结果。\n"
    "你需要判断是生成一个深度研究型报告还是只需进行简单的结果整合。\n"
    "最终输出应该采用 markdown 格式，markdown最后一个section的标题为“参考文献”，包含所有参考文献的url。"
    
)


class ReportData(BaseModel):
    # short_summary: str
    # """简短总结,2-3句话概括主要内容。"""

    markdown_report: str
    """根据用户需求生成的整合结果。"""

    references: list[str]
    """参考文献的url列表。"""


writer_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    model="gpt-4o",
    output_type=ReportData,
)
