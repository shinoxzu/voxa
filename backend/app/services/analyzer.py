from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider


@dataclass
class DiarizedSegment:
    start: float
    end: float
    speaker: str
    text: str


@dataclass
class ActionItemResult:
    assignee: str
    task: str
    deadline: str | None = None


@dataclass
class AnalysisResult:
    summary: str
    action_items: list[ActionItemResult] = field(default_factory=list)


class Analyzer(ABC):
    @abstractmethod
    async def analyze(self, segments: list[DiarizedSegment]) -> AnalysisResult: ...


class AnalyzedActionItem(BaseModel):
    """Задача, извлечённая из транскрипта встречи."""

    assignee: str = Field(description="ID спикера-исполнителя (например SPEAKER_00)")
    task: str = Field(description="Описание задачи")
    deadline: str | None = Field(
        default=None, description="Дедлайн в формате YYYY-MM-DD, если упомянут"
    )


class MeetingAnalysis(BaseModel):
    """Результат анализа встречи."""

    summary: str = Field(description="Краткое резюме встречи (3-5 предложений)")
    action_items: list[AnalyzedActionItem] = Field(
        default_factory=list,
        description="Конкретные задачи с исполнителями",
    )


class PydanticAIAnalyzer(Analyzer):
    def __init__(self, openrouter_model: str, openrouter_token: str) -> None:
        self._agent = Agent(  # type: ignore[no-matching-overload]
            OpenRouterModel(
                openrouter_model,
                provider=OpenRouterProvider(api_key=openrouter_token),
            ),
            system_prompt=(
                "Ты — ассистент для анализа рабочих встреч. "
                "Тебе дают транскрипт встречи с указанием спикеров. "
                "Твоя задача:\n"
                "1. Написать краткое резюме встречи (3-5 предложений)\n"
                "2. Выделить конкретные задачи (action items) с указанием "
                "исполнителя (speaker ID) и дедлайна (если упомянут)"
            ),
            output_type=MeetingAnalysis,
        )

    async def analyze(self, segments: list[DiarizedSegment]) -> AnalysisResult:
        transcript_text = "\n".join(
            f"[{seg.start:.1f}s] {seg.speaker}: {seg.text}" for seg in segments
        )

        result = await self._agent.run(transcript_text)
        data: MeetingAnalysis = result.output  # ty: ignore

        return AnalysisResult(
            summary=data.summary,
            action_items=[
                ActionItemResult(
                    assignee=item.assignee,
                    task=item.task,
                    deadline=item.deadline,
                )
                for item in data.action_items
            ],
        )
