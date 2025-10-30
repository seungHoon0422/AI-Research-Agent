# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# PATH에 uv 추가
export PATH="$HOME/.local/bin:$PATH"

uv venv



source .venv/bin/activate


echo 'pwd: '
pwd

echo 'ls -al: '
ls -al

echo '패키지 설치 ==== uv pip install -r pyproject.toml'
uv pip install -r pyproject.toml


echo 'streamlit 실행 ==== uv run streamlit run main.py --server.port 8000 --server.address 0.0.0.0'
uv run streamlit run main.py --server.port $PORT --server.address 0.0.0.0