import os
import io
from azure.storage.blob import BlobServiceClient
# from storage.storage import Storage
from dotenv import load_dotenv

load_dotenv()
# Create the BlobServiceClient object

class AzureBlobStorage:
    def __init__(self):
        self.account_url = os.getenv("AZURE_BLOB_STORAGE_ENDPOINT")
        self.blob_access_key = os.getenv("AZURE_BLOB_STORAGE_ACCOUNT_KEY")
        self.container_name = os.getenv("AZURE_BLOB_STORAGE_CONTAINER_NAME")
        self.blob_service_client = BlobServiceClient(account_url=self.account_url, credential=self.blob_access_key)


    def upload_blob_file(self, file_path: str, file_name: str):
        container_client = self.blob_service_client.get_container_client(container=self.container_name)
        full_file_path = os.path.join(file_path, file_name)
        with open(file=full_file_path, mode="rb") as data:
            blob_client = container_client.upload_blob(name=file_name, data=data, overwrite=True)

    def upload_blob_file_from_streamlit(self, uploaded_file) -> str:
        """Streamlit UploadedFile 객체를 직접 Blob Storage에 업로드 (예전 방식 복원)

        반환: 업로드된 Blob의 URL
        """
        try:
            container_client = self.blob_service_client.get_container_client(container=self.container_name)
            blob_name = uploaded_file.name

            # UploadedFile -> bytes (작은 파일) 또는 buffer 기반 업로드
            data_bytes = uploaded_file.getvalue()
            blob_client = container_client.get_blob_client(blob=blob_name)
            blob_client.upload_blob(data=data_bytes, overwrite=True)
            return blob_client.url
        except Exception as e:
            raise e


    def get_file_url(self, file_path: str, file_name: str) -> str:
        try:
            blob_service_client = BlobServiceClient(account_url=self.account_url, credential=self.blob_access_key)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
            return blob_client.url
        except Exception as e:
            raise e

    def delete_file(self, file_path: str, file_name: str) -> bool:
        try:
            blob_service_client = BlobServiceClient(account_url=self.account_url, credential=self.blob_access_key)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
            blob_client.delete_blob()
            return True
        except Exception as e:
            raise e