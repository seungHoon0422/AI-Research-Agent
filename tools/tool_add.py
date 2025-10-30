# AI 모델에서 사용할 수 있는 간단한 a+b 계산 기능

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b


# Azure OpenAI Tool 정의 - get_current_time 함수
def get_current_time(location: str = "UTC") -> str:
    """
    특정 위치의 현재 시간을 반환합니다
    
    Args:
        location: 위치 이름 (예: "Seoul", "New York", "Tokyo")
    
    Returns:
        JSON 형식의 시간 정보
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    import json
    
    # 간단한 타임존 매핑
    timezone_map = {
        "seoul": "Asia/Seoul",
        "new york": "America/New_York",
        "tokyo": "Asia/Tokyo",
        "paris": "Europe/Paris",
        "london": "Europe/London",
        "san francisco": "America/Los_Angeles",
        "los angeles": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "utc": "UTC"
    }
    
    location_lower = location.lower()
    tz_name = timezone_map.get(location_lower, "UTC")
    
    try:
        current_time = datetime.now(ZoneInfo(tz_name))
        return json.dumps({
            "location": location,
            "timezone": tz_name,
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "formatted_time": current_time.strftime("%I:%M %p")
        })
    except Exception as e:
        return json.dumps({
            "location": location,
            "error": str(e)
        })


# Azure OpenAI Tool 정의 리스트
CURRENT_TIME_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "특정 위치의 현재 시간을 가져옵니다. 지원되는 위치: Seoul, New York, Tokyo, Paris, London, San Francisco, Los Angeles, Chicago, UTC",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "시간을 확인할 위치 (예: Seoul, New York, Tokyo, Paris, London, San Francisco, Los Angeles, Chicago, UTC)"
                    }
                },
                "required": ["location"]
            }
        }
    }
]


# Tavily 검색 함수
def tavily_search(query: str, max_results: int = 5) -> str:
    """
    Tavily를 사용하여 웹 검색을 수행합니다
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수 (기본값: 5)
    
    Returns:
        JSON 형식의 검색 결과
    """
    import os
    import requests
    import json
    
    tavily_url = os.getenv("TAVILY_MCP_URL", "http://localhost:8000")
    api_key = os.getenv("TAVILY_API_KEY", "")
    
    try:
        # Tavily API 호출
        response = requests.post(
            f"{tavily_url}/search",
            json={
                "query": query,
                "max_results": max_results
            },
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            } if api_key else {"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return json.dumps(response.json())
        else:
            return json.dumps({"error": f"Search failed with status {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# Tavily Tool 정의
TAVILY_SEARCH_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "웹에서 최신 정보를 검색합니다. 뉴스, 기술 문서, 최신 동향 등을 검색할 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 쿼리 (예: '최신 AI 기술 트렌드', 'Python async programming')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "최대 결과 수 (기본값: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
]