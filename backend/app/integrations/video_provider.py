from uuid import uuid4


class JitsiVideoProvider:
    def __init__(self, provider: str, base_url: str) -> None:
        self.provider = provider
        self.base_url = base_url.rstrip("/")

    def create_room(self) -> dict[str, str]:
        room = f"diagnosure-{uuid4().hex}"
        return {
            "video_provider": self.provider,
            "video_room": room,
            "video_url": f"{self.base_url}/{room}",
        }
