from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings
from app.services.analyzer import Analyzer, PydanticAIAnalyzer
from app.services.diarizer import Diarizer, PyAnnoteDiarizer
from app.services.processor import MeetingProcessor
from app.services.tracker import Tracker, YandexTracker
from app.services.transcriber import Transcriber, WhisperCppTranscriber


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    def get_engine(self, settings: Settings) -> AsyncEngine:
        return create_async_engine(settings.database_url)

    @provide(scope=Scope.APP)
    def get_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.APP)
    def get_transcriber(self, settings: Settings) -> Transcriber:
        return WhisperCppTranscriber(settings)

    @provide(scope=Scope.APP)
    def get_diarizer(self, settings: Settings) -> Diarizer:
        return PyAnnoteDiarizer(settings)

    @provide(scope=Scope.APP)
    def get_analyzer(self, settings: Settings) -> Analyzer:
        return PydanticAIAnalyzer(settings.openrouter_llm_model, settings.openrouter_token)

    @provide(scope=Scope.APP)
    def get_processor(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        transcriber: Transcriber,
        diarizer: Diarizer,
        analyzer: Analyzer,
    ) -> MeetingProcessor:
        return MeetingProcessor(session_factory, transcriber, diarizer, analyzer)


class RequestProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_tracker(self, settings: Settings) -> Tracker:
        return YandexTracker(settings)
