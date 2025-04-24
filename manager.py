from __future__ import annotations

import asyncio
import time

from rich.console import Console

from agents import Runner, custom_span, gen_trace_id, trace

from my_agents.planner_agent import WebSearchItem, WebSearchPlan, planner_agent
from my_agents.search_agent import search_agent
from my_agents.writer_agent import ReportData, writer_agent
from printer import Printer


class ResearchManager:
    def __init__(self, progress_bar=None, status_elements=None):
        self.console = Console()
        self.printer = Printer(self.console)
        self.progress_bar = progress_bar
        self.status_elements = status_elements
        self.is_streamlit = progress_bar is not None

    def update_streamlit_status(self, key, message, progress=None, is_done=False):
        """更新Streamlit界面上的状态"""
        if not self.is_streamlit:
            return
            
        if key in self.status_elements and self.status_elements[key] is not None:
            if key == "status_text":
                self.status_elements[key].text(message)
            elif key == "progress_bar" and progress is not None:
                self.status_elements[key].progress(progress)
            else:
                # 为完成的任务添加✅标记
                display_text = f"✅ {message}" if is_done else f"⏳ {message}"
                self.status_elements[key].text(display_text)

    async def run(self, query: str) -> str:
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                f"查看追踪: https://platform.openai.com/traces/{trace_id}",
                is_done=True,
                hide_checkmark=True,
            )

            self.printer.update_item(
                "starting",
                "开始研究...",
                is_done=True,
                hide_checkmark=True,
            )
            
            # 规划搜索
            self.update_streamlit_status("planning", "正在规划搜索...")
            search_plan = await self._plan_searches(query)
            self.update_streamlit_status("planning", "搜索规划完成", is_done=True)
            self.update_streamlit_status("progress_bar", 0.3)
            
            # 输出 WebSearchPlan 的具体内容
            print("\n\n===== WebSearchPlan 内容 =====\n")
            for i, search_item in enumerate(search_plan.searches, 1):
                print(f"搜索项 {i}:")
                print(f"  搜索词: {search_item.query}")
                print(f"  搜索理由: {search_item.reason}")
                print()
            print("===== WebSearchPlan 内容结束 =====\n\n")
            
            # 执行搜索
            self.update_streamlit_status("searching", "正在执行搜索...")
            search_results = await self._perform_searches(search_plan)
            self.update_streamlit_status("searching", "搜索完成", is_done=True)
            self.update_streamlit_status("progress_bar", 0.6)
            
            # 撰写报告
            self.update_streamlit_status("writing", "正在撰写报告...")
            report = await self._write_report(query, search_results)
            self.update_streamlit_status("writing", "报告撰写完成", is_done=True)
            self.update_streamlit_status("progress_bar", 1.0)
            self.update_streamlit_status("status_text", "研究完成！")

        print("\n\n=====Agent输出=====\n\n")
        print(f"{report.markdown_report}")
        
        # 返回markdown报告内容
        return report.markdown_report

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        self.printer.update_item("planning", "正在规划搜索...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        plan_message = f"将执行 {len(result.final_output.searches)} 次搜索"
        self.printer.update_item(
            "planning",
            plan_message,
            is_done=True,
        )
        return result.final_output_as(WebSearchPlan)

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        with custom_span("Search the web"):
            self.printer.update_item("searching", "正在搜索...")
            num_completed = 0
            tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
            results = []
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                num_completed += 1
                search_status = f"正在搜索... {num_completed}/{len(tasks)} 已完成"
                self.printer.update_item("searching", search_status)
                
                # 更新Streamlit搜索进度
                if self.is_streamlit:
                    self.update_streamlit_status("searching", search_status)
                    search_progress = 0.3 + (0.3 * num_completed / len(tasks))
                    self.update_streamlit_status("progress_bar", search_progress)
                    
            self.printer.mark_item_done("searching")
            return results
            
    async def _search(self, item: WebSearchItem) -> str | None:
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            print("\n===== 搜索结果 =====")
            print(f"搜索词: {item.query}")
            print(f"搜索结果: {result.final_output}")
            print("===================\n")
            return str(result.final_output)
        except Exception:
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        self.printer.update_item("writing", "正在思考报告内容...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = Runner.run_streamed(
            writer_agent,
            input,
        )
        update_messages = [
            "正在思考内容...",
            "正在规划结构...",
            "正在组织信息...",
            "正在生成内容...",
            "正在整理格式...",
            "正在完善内容...",
            "即将完成...",
        ]

        last_update = time.time()
        next_message = 0
        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(update_messages):
                message = update_messages[next_message]
                self.printer.update_item("writing", message)
                
                # 更新Streamlit写作进度
                if self.is_streamlit:
                    self.update_streamlit_status("writing", message)
                    write_progress = 0.6 + (0.4 * next_message / len(update_messages))
                    self.update_streamlit_status("progress_bar", min(0.95, write_progress))
                    
                next_message += 1
                last_update = time.time()

        self.printer.mark_item_done("writing")
        return result.final_output_as(ReportData)
