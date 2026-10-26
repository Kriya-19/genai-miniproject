from dataclasses import dataclass


@dataclass
class NotificationResult:
    status: str
    message: str


class NotificationProvider:
    def send(self, user_id: str, title: str) -> NotificationResult:
        raise NotImplementedError


class LocalNotificationProvider(NotificationProvider):
    def send(self, user_id: str, title: str) -> NotificationResult:
        return NotificationResult("recorded_locally", "No external notification provider is configured.")


def get_notification_provider(provider_name: str) -> NotificationProvider:
    if provider_name == "local":
        return LocalNotificationProvider()
    if provider_name == "fcm":
        return LocalNotificationProvider()
    raise ValueError(f"Unsupported notification provider: {provider_name}")
