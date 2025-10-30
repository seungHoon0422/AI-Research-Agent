# from typing import List, Any
# import os
# from dotenv import load_dotenv
# from storage.azure_blob_storage import AzureBlobStorage
# from abc import ABC, abstractmethod
# from collections.abc import Generator

# load_dotenv()



# # Storage 인터페이스 객체 구현
# # 구현 기능 :
# #   1. 파일 업로드
# #   2. 파일 조회
# #   3. 파일 삭제


# """Abstract interface for file storage implementations."""
# class Storage(ABC):
#     def __init__(self):
#         self.storage = None
#         self.storage_type = os.getenv("STORAGE_TYPE")
#         if self.storage_type == "AZURE_BLOB":
#             self.storage = AzureBlobStorage()
#         # elif self.storage_type == "LOCAL":
#         #     self.storage = LocalStorageManager()
#         else:
#             raise ValueError(f"Invalid storage type: {self.storage_type}")

#     @abstractmethod
#     def upload_files(self, files: List[Any]) -> List[str]:
#         raise NotImplementedError

#     @abstractmethod
#     def upload_files_stream(self, filename, file_stream):
#         """
#         스트림으로 파일 저장 (추상 메서드)
#         메모리 효율적인 파일 업로드를 위해 사용
        
#         :param filename: 저장할 파일 경로
#         :param file_stream: 파일 스트림 객체
#         """
#         raise NotImplementedError

#     @abstractmethod
#     def get_file_url(self, file_path, file_name: str) -> str:
#         raise NotImplementedError

#     @abstractmethod
#     def delete_file(self, file_path, file_name: str) -> bool:
#         raise NotImplementedError





# class BaseStorage(ABC):
#     """
#     Interface for file storage.
#     """

#     def __init__(self):
#         pass

#     @abstractmethod
#     def save(self, filename, data):
#         raise NotImplementedError
        
#     @abstractmethod
#     def save_stream(self, filename, file_stream):
#         """
#         스트림으로 파일 저장 (추상 메서드)
#         메모리 효율적인 파일 업로드를 위해 사용
        
#         :param filename: 저장할 파일 경로
#         :param file_stream: 파일 스트림 객체
#         """
#         raise NotImplementedError

#     @abstractmethod
#     def load_once(self, filename: str) -> bytes:
#         raise NotImplementedError

#     @abstractmethod
#     def load_stream(self, filename: str) -> Generator:
#         raise NotImplementedError

#     @abstractmethod
#     def download(self, filename, target_filepath):
#         raise NotImplementedError

#     @abstractmethod
#     def exists(self, filename):
#         raise NotImplementedError

#     @abstractmethod
#     def delete(self, filename):
#         raise NotImplementedError
