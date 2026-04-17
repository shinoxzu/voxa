from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from app.config import Settings


@dataclass
class CreatedIssue:
    key: str
    url: str


class Tracker(ABC):
    @abstractmethod
    async def create_issue(
        self, queue: str, summary: str, assignee: str | None, deadline: str | None
    ) -> CreatedIssue: ...


class YandexTracker(Tracker):
    BASE_URL = "https://api.tracker.yandex.net/v3"

    def __init__(self, settings: Settings) -> None:
        self._token = settings.yandex_tracker_token
        self._org_id = settings.yandex_tracker_org_id
        self._cloud_org = settings.yandex_tracker_cloud_org

    async def create_issue(
        self, queue: str, summary: str, assignee: str | None, deadline: str | None
    ) -> CreatedIssue:
        body: dict = {"queue": {"key": queue}, "summary": summary}

        headers: dict[str, str] = {
            "Authorization": f"OAuth {self._token}",
        }
        if self._cloud_org:
            headers["X-Cloud-Org-ID"] = self._org_id
        else:
            headers["X-Org-ID"] = self._org_id

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/issues/",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        return CreatedIssue(
            key=data["key"],
            url=f"https://tracker.yandex.ru/{data['key']}",
        )
