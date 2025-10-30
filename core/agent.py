# 키워드, 도메인 등 에이전트 종류에 따른 에이전트 호출 추상화 모듈
# 모델 호출 request, response 처리 모듈
# 다양한 에이전트 호출 방식에 대한 공통 인터페이스 제공
# 사용 기술 : langGraph, Azure Open AI, LangChain 등

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Union
import json
import time


@dataclass
class AgentConfig:
    """
    에이전트 공통 설정 구조체
    - provider: 'azure' | 'openai' | 'local' 등
    - model: 모델 식별자
    - timeout: 요청 타임아웃(초)
    - extra: 공급자/에이전트별 추가 설정
    """
    provider: str = "openai"
    model: str = "gpt-4"
    timeout: int = 60
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRequest:
    """
    에이전트에 전달되는 표준 요청 포맷
    - messages: 채팅형 입력 (role/content)
    - metadata: 문서 id, 원본 URL 등 추가 정보
    """
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """
    에이전트 응답 표준 포맷
    - content: 모델이 생성한 텍스트
    - raw: 원시 응답(공급자별)
    - usage: 비용/토큰 정보(있을 경우)
    - error: 에러가 발생한 경우 메시지
    """
    content: str
    raw: Optional[Any] = None
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency: Optional[float] = None


class AgentInterface(ABC):
    """
    에이전트 추상 인터페이스
    목적:
    - 키워드, 도메인 등 에이전트 종류에 따른 호출 추상화
    - 모델 호출 request/response 처리 공통화
    - 다양한 에이전트 호출 방식에 대한 공통 인터페이스 제공
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.state: Dict[str, Any] = {}
        self._last_response: Optional[AgentResponse] = None

    @abstractmethod
    def prepare_request(self, request: AgentRequest) -> Dict[str, Any]:
        """
        공급자/구현체별 실제 API 호출에 맞는 payload를 생성.
        """
        raise NotImplementedError

    @abstractmethod
    def send_request(self, payload: Dict[str, Any]) -> Any:
        """
        실제 외부 API 호출을 수행. 동기 또는 비동기 구현 허용.
        반환값은 공급자 원시 응답.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_response(self, raw_response: Any) -> AgentResponse:
        """
        공급자 원시 응답을 AgentResponse 표준 형식으로 변환.
        """
        raise NotImplementedError

    def run(self, request: AgentRequest) -> AgentResponse:
        """
        표준 실행 흐름:
        1) payload 준비
        2) 외부 호출
        3) 응답 파싱 및 로깅/상태 저장
        """
        start = time.time()
        payload = self.prepare_request(request)
        raw = None
        try:
            raw = self.send_request(payload)
            resp = self.parse_response(raw)
            resp.latency = time.time() - start
            self._last_response = resp
            self._on_success(request, resp)
            return resp
        except Exception as e:
            latency = time.time() - start
            resp = AgentResponse(content="", raw=raw, error=str(e), latency=latency)
            self._last_response = resp
            self._on_error(request, resp)
            return resp

    # 선택적 훅 / 유틸리티 메서드
    def set_config(self, config: AgentConfig) -> None:
        self.config = config

    def get_config(self) -> AgentConfig:
        return self.config

    def get_last_response(self) -> Optional[AgentResponse]:
        return self._last_response

    def save_state(self, key: str, value: Any) -> None:
        self.state[key] = value

    def load_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def _on_success(self, request: AgentRequest, response: AgentResponse) -> None:
        """
        성공 후 처리(로깅, 메트릭 등). 필요시 서브클래스에서 override.
        """
        # 기본 동작: 간단한 로그를 상태에 저장
        self.save_state("last_success", {"request_meta": request.metadata, "response_len": len(response.content)})

    def _on_error(self, request: AgentRequest, response: AgentResponse) -> None:
        """
        에러 처리. 필요시 서브클래스에서 override.
        """
        self.save_state("last_error", {"metadata": request.metadata, "error": response.error})
