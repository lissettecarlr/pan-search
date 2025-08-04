"""
网盘搜索Web应用
"""
import streamlit as st
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app import PanSearchApp
from src.models import SearchResponse


# 页面配置
st.set_page_config(
    page_title="聚合网盘资源搜索",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 不使用任何自定义CSS样式，完全使用默认的Streamlit样式


@st.cache_resource
def get_search_app():
    """获取搜索应用实例"""
    app = PanSearchApp()
    # 同步初始化
    asyncio.run(app.initialize())
    return app


def display_search_results(response: SearchResponse):
    """显示搜索结果"""
    if not response.merged_by_type:
        st.info("未找到任何资源，请尝试其他关键词。")
        return
    
    # 过滤掉 "others" 分类，只显示实际存在的分类
    filtered_types = {k: v for k, v in response.merged_by_type.items() if k != "others"}
    
    if not filtered_types:
        st.info("未找到任何资源，请尝试其他关键词。")
        return
    
    # 按类型显示结果
    type_names = list(filtered_types.keys())
    tabs = st.tabs([f"{t} ({len(filtered_types[t])})" for t in type_names])
    
    # 添加CSS样式
    st.markdown("""
    <style>
    .result-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background-color: #fff;
        transition: box-shadow 0.3s ease;
    }
    
    @media (prefers-color-scheme: dark) {
        .result-card {
            border: 1px solid #444;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            background-color: #2d2d2d;
        }
    }
    
    .result-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    @media (prefers-color-scheme: dark) {
        .result-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }
    }
    
    .result-title {
        margin: 0 0 1rem 0;
        color: #333;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    @media (prefers-color-scheme: dark) {
        .result-title {
            color: #ddd;
        }
    }
    
    .result-meta {
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #333;
    }
    
    @media (prefers-color-scheme: dark) {
        .result-meta {
            color: #ddd;
        }
    }
    
    .source-tag {
        background-color: #f0f0f0;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #666;
    }
    
    @media (prefers-color-scheme: dark) {
        .source-tag {
            background-color: #444;
            color: #ccc;
        }
    }
    
    .result-link {
        word-break: break-all;
        color: #1976d2;
        text-decoration: none;
    }
    
    @media (prefers-color-scheme: dark) {
        .result-link {
            color: #64b5f6;
        }
    }
    
    .result-link:hover {
        text-decoration: underline;
    }
    
    .password {
        font-family: monospace;
        background-color: #f5f5f5;
        padding: 0.1rem 0.3rem;
        border-radius: 3px;
        font-weight: bold;
        color: #333;
    }
    
    @media (prefers-color-scheme: dark) {
        .password {
            background-color: #444;
            color: #fff;
        }
    }
    
    strong {
        color: #333;
    }
    
    @media (prefers-color-scheme: dark) {
        strong {
            color: #ddd;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    for idx, resource_type in enumerate(type_names):
        with tabs[idx]:
            links = filtered_types[resource_type]
            
            for i, link in enumerate(links):
                with st.container():
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-title">{link.note}</div>
                        <div class="result-meta">
                            <span class="source-tag">来源: {link.source if link.source else '未知'}</span>
                        </div>
                        <div class="result-meta">
                            <strong>链接:</strong> 
                            <a href="{link.url}" target="_blank" class="result-link">{link.url}</a>
                        </div>
                        <div class="result-meta">
                            <strong>提取码:</strong> 
                            <span class="password">{link.password if link.password else '无'}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


def main():
    """主函数"""
    # 使用默认的Streamlit标题
    st.title("聚合网盘资源搜索")
    
    # 获取应用实例
    app = get_search_app()
    
    # 主界面
    # 使用默认的Streamlit布局
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        keyword = st.text_input(
            "请输入要搜索的资源",
            placeholder="..."
        )
    
    with col2:
        search_btn = st.button("搜索", type="primary", use_container_width=True)
    
    # 执行搜索
    if search_btn and keyword.strip():
        try:
            with st.spinner("正在搜索中，请稍候..."):
                result = asyncio.run(app.search(keyword.strip()))
            
            if result and result.total > 0:
                st.success(f"搜索完成！")
                display_search_results(result)
            else:
                st.info("未找到任何资源，请尝试其他关键词。")
                
        except Exception as e:
            st.error(f"搜索失败: {str(e)}")
            st.info("请检查网络连接或稍后重试")
    
    elif search_btn and not keyword.strip():
        st.warning("请输入搜索关键词")
    

if __name__ == "__main__":
    main()