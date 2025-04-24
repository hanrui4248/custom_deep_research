import streamlit as st
import asyncio
import os
from manager import ResearchManager
from agents import set_default_openai_key

st.set_page_config(
    page_title="研究助手",
    page_icon="🔍",
    layout="wide"
)

async def run_research(query, progress_placeholder, status_placeholder):
    manager = ResearchManager(progress_placeholder, status_placeholder)
    report = await manager.run(query)
    return report

def main():
    st.title("🔍 AI4DeepSearch")
    st.markdown("输入您的研究问题，AI将为您搜索并整合相关信息")
    
    # 侧边栏设置
    with st.sidebar:
        st.header("设置")
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            set_default_openai_key(api_key)
    
    # 主界面
    query = st.text_area("请输入您的研究问题", height=100)
    
    if st.button("开始研究", type="primary"):
        if not query:
            st.error("请输入研究问题")
            return
        
        if not api_key:
            st.error("请输入OpenAI API Key")
            return
        
        # 创建进度显示区域
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            trace_id_text = st.empty()
            
            # 创建各阶段状态显示
            planning_status = st.empty()
            searching_status = st.empty()
            writing_status = st.empty()
            
            # 将所有状态元素打包成字典传递给manager
            status_elements = {
                "progress_bar": progress_bar,
                "status_text": status_text,
                "trace_id": trace_id_text,
                "planning": planning_status,
                "searching": searching_status,
                "writing": writing_status
            }
        
        # 创建报告显示区域
        report_container = st.container()
        
        with st.spinner("正在进行研究..."):
            report = asyncio.run(run_research(query, progress_bar, status_elements))
            
            # 显示研究报告
            with report_container:
                st.markdown("## 研究报告")
                st.markdown(report)

if __name__ == "__main__":
    main() 