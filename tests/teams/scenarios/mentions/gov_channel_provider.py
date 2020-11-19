from botframework.connector.auth import ChannelProvider

class GovChannelProvider(ChannelProvider):
    async def get_channel_service(self) -> str:
        return "https://botframework.azure.us"

    def is_government(self) -> bool:
        return True
    
    def is_public_azure(self) -> bool:
        return False
    