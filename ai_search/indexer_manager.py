"""
Azure AI Search Indexer 관리 클래스
인덱서 실행, 상태 확인, 관리 기능을 제공합니다.
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class IndexerManager:
    """Azure AI Search Indexer를 관리하는 클래스"""
    
    def __init__(self):
        self.search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "").rstrip("/")
        self.admin_key = os.getenv("AZURE_AI_SEARCH_ADMIN_KEY") or os.getenv("AZURE_AI_SEARCH_API_KEY") or ""
        self.indexer_name = os.getenv("AZURE_AI_SEARCH_INDEXER_NAME", "aisearch-indexer")
        self.api_version = os.getenv("AZURE_AI_SEARCH_API_VERSION", "2020-06-30")
        
        if not self.search_endpoint or not self.admin_key:
            raise ValueError("환경변수 AZURE_AI_SEARCH_ENDPOINT 또는 AZURE_AI_SEARCH_ADMIN_KEY가 설정되지 않았습니다.")
    
    def run_indexer(self) -> Dict[str, Any]:
        """
        인덱서를 실행합니다.
        
        Returns:
            Dict[str, Any]: 실행 결과
        """
        url = f"{self.search_endpoint}/indexers/{self.indexer_name}/run"
        params = {"api-version": self.api_version}
        headers = {
            "Content-Type": "application/json",
            "Content-Length": "0",
            "api-key": self.admin_key,
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, timeout=20)
            
            result = {
                "success": response.status_code in (200, 202),
                "status_code": response.status_code,
                "message": "",
                "response_text": response.text
            }
            
            if result["success"]:
                result["message"] = f"인덱서 재실행 요청 전송 완료 (status: {response.status_code})"
            else:
                result["message"] = f"인덱서 재실행 실패 (status: {response.status_code})"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "message": f"인덱서 재실행 중 오류: {e}",
                "response_text": str(e)
            }
    
    def get_indexer_status(self) -> Dict[str, Any]:
        """
        인덱서 상태를 조회합니다.
        
        Returns:
            Dict[str, Any]: 인덱서 상태 정보
        """
        url = f"{self.search_endpoint}/indexers/{self.indexer_name}/status"
        params = {"api-version": self.api_version}
        headers = {
            "api-key": self.admin_key,
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "message": ""
            }
            
            if result["success"]:
                result["message"] = "인덱서 상태 조회 성공"
            else:
                result["message"] = f"인덱서 상태 조회 실패 (status: {response.status_code})"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "data": None,
                "message": f"인덱서 상태 조회 중 오류: {e}"
            }
    
    def get_indexer_info(self) -> Dict[str, Any]:
        """
        인덱서 정보를 조회합니다.
        
        Returns:
            Dict[str, Any]: 인덱서 정보
        """
        url = f"{self.search_endpoint}/indexers/{self.indexer_name}"
        params = {"api-version": self.api_version}
        headers = {
            "api-key": self.admin_key,
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "message": ""
            }
            
            if result["success"]:
                result["message"] = "인덱서 정보 조회 성공"
            else:
                result["message"] = f"인덱서 정보 조회 실패 (status: {response.status_code})"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "data": None,
                "message": f"인덱서 정보 조회 중 오류: {e}"
            }
    
    def reset_indexer(self) -> Dict[str, Any]:
        """
        인덱서를 리셋합니다.
        
        Returns:
            Dict[str, Any]: 리셋 결과
        """
        url = f"{self.search_endpoint}/indexers/{self.indexer_name}/reset"
        params = {"api-version": self.api_version}
        headers = {
            "Content-Type": "application/json",
            "api-key": self.admin_key,
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, timeout=20)
            
            result = {
                "success": response.status_code in (200, 204),
                "status_code": response.status_code,
                "message": "",
                "response_text": response.text
            }
            
            if result["success"]:
                result["message"] = f"인덱서 리셋 완료 (status: {response.status_code})"
            else:
                result["message"] = f"인덱서 리셋 실패 (status: {response.status_code})"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "message": f"인덱서 리셋 중 오류: {e}",
                "response_text": str(e)
            }
