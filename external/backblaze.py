from b2sdk.v2 import B2Api, InMemoryAccountInfo, AuthInfoCache
from typing import Dict, Any

class BackBlazeCDN:
    B2_API: B2Api = None
    bucket = None

    @staticmethod
    def update_config(b2_config: Dict[str, Any]) -> None:
        apiID = b2_config.get('key-id', '')
        apiKey = b2_config.get('auth-key', '')
        BackBlazeCDN.bucket = b2_config.get('bucket-name', '')

        info = InMemoryAccountInfo()
        BackBlazeCDN.B2_API = B2Api(info, cache=AuthInfoCache(info))
        BackBlazeCDN.B2_API.authorize_account("production", apiID, apiKey)
        
    def upload(self, file: bytes, filepath: str):
        if self.B2_API:
            bucket = self.B2_API.get_bucket_by_name(self.bucket)
            bucket.upload_bytes(
                    data_bytes=file,
                    file_name=filepath,
                )
            return True
        else:
            return False