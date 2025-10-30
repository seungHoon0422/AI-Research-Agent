
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# PATH에 uv 추가
export PATH="$HOME/.local/bin:$PATH"

uv sync

# streamlit 실행
uv run streamlit run main.py --server.port=8000 --server.address=0.0.0.0
