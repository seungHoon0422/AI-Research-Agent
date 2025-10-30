import streamlit as st
import pandas as pd
import random
import math
from datetime import datetime, timedelta
from streamlit_agraph import agraph, Node, Edge, Config

# 페이지 전체화면 설정
st.set_page_config(page_title="🍀 Document Hub", page_icon="🗺️", layout="wide")

# 키워드 기반 AI 기술 관계도를 시각화합니다.
# 검색된 자료의 키워드를 추출하여 지식 허브의 Document keyword 기반 관계도 생성합니다.
# 현재는 데이터가 연결되어있지 않은 상태로, dummy 데이터로 노출
# 키워드는 Vector, Model, Search, Database, Framework 등으로 임시 데이터를 생성하고, 하위 기술을 3,4개 씩 예시 논문 이름을 입력해서 데이터 생성

# 사용자에게 노출될 대시보드는 차트와 표 형식
# 차트에는 등록되어있는 키워드 하위의 기술 개수를 한눈에 볼 수 있게 생성
# 표에는 전체 키워드 선택, 키워드별 선택 기능을 통해서 해당 기술의 논문 이름을 표시

# Title 설정
col_title_1, col_title_2 = st.columns([0.8, 0.2])
with col_title_1:
    st.markdown('# 🍀 Document Hub')
with col_title_2:
    # 지식 허브 관련 Information Dialog 버튼
    from information.dialog import show_knowledge_hub_info_dialog
    from information.button import DOCUMENT_HUB_HELP_BUTTON_MESSAGE
    info_button_clicked = st.button(DOCUMENT_HUB_HELP_BUTTON_MESSAGE, use_container_width=True, help="Document Hub 사용법")
    if info_button_clicked:
        show_knowledge_hub_info_dialog()

st.markdown("---")

# 랜덤 시드 설정 (일관성 유지)
random.seed(42)

# 카테고리별 하위 키워드 (카테고리에 맞게 분류)
category_keywords = {
    "Vector": [
        "Embedding", "Vector DB", "FAISS", "Pinecone", "Weaviate",
        "Semantic Search", "Similarity", "Indexing", "Retrieval", "ANN"
    ],
    "Model": [
        "LLM", "GPT", "BERT", "Transformer", "Fine-tuning",
        "Training", "Inference", "Optimization", "Quantization", "Deployment"
    ],
    "Search": [
        "Full-text", "Keyword", "Fuzzy", "Semantic", "Hybrid",
        "Ranking", "Relevance", "Query", "Index", "Elasticsearch"
    ],
    "Database": [
        "PostgreSQL", "MongoDB", "Redis", "SQL", "NoSQL",
        "Sharding", "Replication", "Backup", "Performance", "ACID"
    ],
    "Framework": [
        "LangChain", "LlamaIndex", "Hugging Face", "PyTorch", "TensorFlow",
        "Streamlit", "FastAPI", "Flask", "Django", "Next.js"
    ]
}

# 기술 개수를 1~10 사이 랜덤으로 생성
def generate_random_count():
    return random.randint(1, 10)

# 랜덤 날짜 생성 함수
def generate_random_date():
    # 2025년 내에서, 오늘(2025-10-30)을 넘지 않도록 제한
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 10, 30)
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

# Dummy 데이터 생성
dummy_data = {
    "Vector": [],
    "Model": [],
    "Search": [],
    "Database": [],
    "Framework": []
}

# 각 키워드별로 랜덤 개수만큼 자료 생성
paper_titles = [
    ("Vector Indexing for Semantic Search", "vector_semantic_search.pdf"),
    ("Machine Learning Models", "ml_models_guide.docx"),
    ("Neural Search Systems", "neural_search.pdf"),
    ("Vector Database Design", "vector_db_design.pdf"),
    ("Deep Learning Framework Comparison", "dl_framework.pdf"),
    ("Transformer Architecture Overview", "transformer_arch.pdf"),
    ("Hybrid Search Implementation", "hybrid_search.pdf"),
    ("Distributed Vector Storage", "dist_vector_storage.pdf"),
    ("LLM Framework Development", "llm_framework.pdf"),
    ("Semantic Embeddings", "semantic_embeddings.pdf"),
    ("BERT and GPT Models", "bert_gpt.pdf"),
    ("Information Retrieval Systems", "ir_systems.pdf"),
    ("NoSQL for AI Applications", "nosql_ai.pdf"),
    ("RAG Pipeline Framework", "rag_pipeline.pdf"),
    ("Vector Similarity Search", "vector_similarity.pdf"),
    ("Neural Information Extraction", "neural_extraction.pdf"),
    ("Graph Database Optimization", "graph_db.pdf"),
    ("AI Development Framework", "ai_dev_framework.pdf"),
    ("Semantic Search Algorithms", "semantic_algorithms.pdf"),
    ("Large Language Models", "llm_guide.pdf")
]

# 키워드별로 랜덤 개수의 자료 할당
keyword_list = list(dummy_data.keys())
title_idx = 0
for keyword in keyword_list:
    count = generate_random_count()
    for i in range(count):
        if title_idx >= len(paper_titles):
            title_idx = 0
        
        title, filename = paper_titles[title_idx]
        # 카테고리에 맞는 하위 키워드 선택
        available_keywords = category_keywords.get(keyword, [])
        num_sub_keywords = min(random.randint(2, 3), len(available_keywords))
        sub_keywords = random.sample(available_keywords, num_sub_keywords)
        
        dummy_data[keyword].append({
            "자료명": title,
            "파일명": filename,
            "생성일자": generate_random_date(),
            "하위키워드": sub_keywords
        })
        title_idx += 1

# 키워드별 기술 개수 데이터 (랜덤)
keyword_counts = {
    "카테고리": list(dummy_data.keys()),
    "기술 개수": [len(data) for data in dummy_data.values()]
}

# 1로우: 키워드 관계도 3, 상세통계 1
col_graph, col_stats = st.columns([3, 1])

with col_graph:
    st.markdown("#### 📊 Document Hub Graph")
    
    # 노드와 엣지 생성
    nodes = []
    edges = []
    
    # Document Hub 중심 노드 추가
    nodes.append(
        Node(
            id="Document Hub",
            label="Document Hub",
            size=50,
            color="#FF0000",
            font={"size": 24, "face": "Arial", "color": "white"},
            shape="dot",
            title="Document Hub"
        )
    )
    
    # 메인 키워드를 카테고리 노드로 추가
    main_keywords = list(dummy_data.keys())
    
    for keyword in main_keywords:
        nodes.append(
            Node(
                id=keyword,
                label=keyword,
                size=35,
                color="#FF6B6B",
                font={"size": 16, "face": "Arial", "color": "white"},
                shape="dot",
                title=keyword
            )
        )
        # Document Hub와 카테고리 노드 연결
        edges.append(
            Edge(
                source="Document Hub",
                target=keyword,
                color="#FFFFFF",
                width=3
            )
        )
    
    # 하위키워드 수집 및 노드 추가
    all_sub_keywords_set = set()
    sub_keyword_to_main = {}  # 하위키워드가 어떤 메인 키워드에 속하는지 추적
    
    for keyword, papers in dummy_data.items():
        for paper in papers:
            for sub_keyword in paper['하위키워드']:
                all_sub_keywords_set.add(sub_keyword)
                if sub_keyword not in sub_keyword_to_main:
                    sub_keyword_to_main[sub_keyword] = []
                sub_keyword_to_main[sub_keyword].append(keyword)
    
    # 하위키워드를 메인 키워드별로 그룹화하여 추가 (중복 방지)
    main_keyword_colors = {
        "Vector": "#4ECDC4",
        "Model": "#FFA07A",
        "Search": "#98D8C8",
        "Database": "#F7DC6F",
        "Framework": "#BB8FCE"
    }
    added_nodes = set()  # (sub_keyword, main_keyword) 튜플로 추적
    
    for sub_keyword, main_keywords_list in sub_keyword_to_main.items():
        for main_keyword in main_keywords_list:
            # (하위키워드, 메인키워드) 조합으로 중복 체크
            if (sub_keyword, main_keyword) not in added_nodes:
                nodes.append(
                    Node(
                        id=f"{sub_keyword}_{main_keyword}",
                        label=sub_keyword,
                        size=15,
                        color=main_keyword_colors.get(main_keyword, "#85C1E2"),
                        font={"size": 11, "face": "Arial", "color": "white"},
                        shape="dot",
                        group=main_keyword  # 그룹 지정
                    )
                )
                added_nodes.add((sub_keyword, main_keyword))
            
            edges.append(
                Edge(
                    source=main_keyword,
                    target=f"{sub_keyword}_{main_keyword}",
                    color=main_keyword_colors.get(main_keyword, "#CCCCCC"),
                    width=1.5
                )
            )
    
    # 그래프 설정
    config = Config(
        width="100%",
        height=500,
        directed=False,
        hierarchical=False,
        layout={
            "hierarchical": False,
            "improvedLayout": True
        },
        node={
            "labelProperty": "label",
            "font": {"size": 12}
        },
        edge={
            "smooth": {
                "enabled": True, 
                "type": "curvedCW",
                "roundness": 0.3
            },
            "length": 100,  # 짧게 설정
            "width": 2
        },
        # 노드 간 거리 조정 (계층 구조: Data Hub -> 카테고리 -> 하위키워드)
        physics={
            "enabled": True,
            "stabilization": True,
            "barnesHut": {
                "gravitationalConstant": -500,
                "centralGravity": 0.0,
                "springLength": 60,
                "springConstant": 0.15,
                "damping": 0.2,
                "avoidOverlap": 1
            }
        },
        # 노드 선택 기능
        interaction={
            "hover": True,
            "selectConnectedEdges": True,
            "selectConnectedNodes": True,
            "tooltipDelay": 300,
            "dragNodes": True,
            "dragView": True
        }
    )
    
    # 키워드별 기술 개수 데이터프레임 생성
    chart_df = pd.DataFrame(keyword_counts)
    
    # 선택된 카테고리에 따라 필터링
    if 'selected_category' in st.session_state and st.session_state.selected_category:
        # 선택된 카테고리만 표시
        filtered_nodes = []
        filtered_edges = []
        
        # Document Hub는 항상 표시
        for node in nodes:
            if node.id == "Document Hub":
                filtered_nodes.append(node)
            elif node.id == st.session_state.selected_category:
                filtered_nodes.append(node)
            elif hasattr(node, 'group') and node.group == st.session_state.selected_category:
                filtered_nodes.append(node)
        
        # 필터링된 노드에 연결된 엣지만 표시
        node_ids = {node.id for node in filtered_nodes}
        for edge in edges:
            # Edge 객체의 속성 접근
            edge_source = getattr(edge, 'source', None)
            edge_target = getattr(edge, 'target', None)
            if edge_source in node_ids or edge_target in node_ids:
                filtered_edges.append(edge)
        
        nodes = filtered_nodes
        edges = filtered_edges
    
    # 그래프 렌더링
    try:
        agraph(nodes=nodes, edges=edges, config=config)
    except Exception as e:
        st.error(f"그래프 렌더링 오류: {e}")
        st.info("일반 차트로 대체 표시합니다.")
        st.bar_chart(chart_df.set_index("카테고리"))

with col_stats:
    st.markdown("#### 📈 카테고리 통계")
    st.dataframe(
        chart_df,
        use_container_width=True,
        hide_index=True
    )
    
    # 그래프 카테고리 선택
    st.markdown("#### 🔍 카테고리 필터")
    filter_options = ["전체"] + list(dummy_data.keys())
    
    if 'graph_category_filter' not in st.session_state:
        st.session_state.graph_category_filter = "전체"
    
    selected_filter = st.selectbox(
        "표시할 카테고리",
        filter_options,
        key="graph_filter",
        help="그래프에 표시할 카테고리를 선택하세요"
    )
    
    # 필터 선택 시 업데이트
    if selected_filter != st.session_state.graph_category_filter:
        st.session_state.graph_category_filter = selected_filter
        if selected_filter == "전체":
            st.session_state.selected_category = None
        else:
            st.session_state.selected_category = selected_filter
        st.rerun()

st.markdown("---")

# 2로우: 논문 목록
st.markdown("#### 📋 Document Hub 목록")

# 카테고리 선택 드롭다운
keyword_options = ["전체"] + list(dummy_data.keys())

# 논문 목록 키워드 필터 초기화
if 'paper_keyword_filter' not in st.session_state:
    st.session_state.paper_keyword_filter = "전체"

# 기본 인덱스 계산
if st.session_state.paper_keyword_filter in keyword_options:
    default_idx = keyword_options.index(st.session_state.paper_keyword_filter)
else:
    default_idx = 0

selected_keyword = st.selectbox(
    "카테고리 선택",
    keyword_options,
    index=default_idx,
    help="전체 또는 특정 카테고리를 선택하여 목록을 확인하세요",
    key="keyword_selectbox"
)

# 선택된 값이 변경되면 세션 상태 업데이트
if selected_keyword != st.session_state.paper_keyword_filter:
    st.session_state.paper_keyword_filter = selected_keyword

# 필터링된 데이터
if selected_keyword == "전체":
    filtered_data = []
    for keyword, papers in dummy_data.items():
        for paper in papers:
            filtered_data.append({
                "카테고리": keyword,
                **paper
            })
else:
    filtered_data = []
    for paper in dummy_data[selected_keyword]:
        filtered_data.append({
            "카테고리": selected_keyword,
            **paper
        })

# 표로 표시
if filtered_data:
    # 표용 데이터프레임 생성
    table_data = []
    for item in filtered_data:
        sub_keywords_str = ", ".join(item['하위키워드'])
        table_data.append({
            "카테고리": item['카테고리'],
            "자료명": item['자료명'],
            "파일명": item['파일명'],
            "생성일자": item['생성일자'],
            "하위키워드": sub_keywords_str
        })
    
    table_df = pd.DataFrame(table_data)
    
    # 페이지네이션 설정
    items_per_page = 10
    total_pages = (len(table_df) + items_per_page - 1) // items_per_page
    
    # 현재 페이지 상태 관리
    page_key = f"page_{selected_keyword}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    current_page = st.session_state[page_key]
    
    # 현재 페이지 데이터 표시
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    # 표용 데이터프레임 생성
    display_data = []
    for item in filtered_data[start_idx:end_idx]:
        keywords_text = " ".join([f"[{keyword}]" for keyword in item['하위키워드']])
        display_data.append({
            "카테고리": item['카테고리'],
            "자료명": f"📄 {item['자료명']}",
            "파일명": f"📂 {item['파일명']}",
            "생성일자": f"📅 {item['생성일자']}",
            "하위키워드": keywords_text
        })
    
    # 항상 10개 행으로 고정 (부족하면 빈 행 추가)
    while len(display_data) < items_per_page:
        display_data.append({
            "키워드": "",
            "자료명": "",
            "파일명": "",
            "생성일자": "",
            "하위키워드": ""
        })
    
    display_df = pd.DataFrame(display_data)
    
    # 표로 표시
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # 페이지 선택 버튼 (표 아래에 배치, 오른쪽 정렬)
    col_left, col_right = st.columns([6, 2])
    with col_left:
        st.caption(f"총 {len(filtered_data)}개 | 페이지: {current_page}/{total_pages}")
    with col_right:
        # 이전/다음 버튼을 한 줄에 배치
        col_prev, col_next = st.columns(2)
        with col_prev:
            if total_pages > 1:
                prev_disabled = current_page == 1
                if st.button("◀ 이전", disabled=prev_disabled, key=f"prev_{page_key}", use_container_width=True):
                    st.session_state[page_key] = max(1, current_page - 1)
                    st.rerun()
        with col_next:
            if total_pages > 1:
                next_disabled = current_page >= total_pages
                if st.button("다음 ▶", disabled=next_disabled, key=f"next_{page_key}", use_container_width=True):
                    st.session_state[page_key] = min(total_pages, current_page + 1)
                    st.rerun()
else:
    st.info("선택한 키워드에 대한 자료가 없습니다.")