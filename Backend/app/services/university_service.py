from collections.abc import Sequence
from typing import Any

from app.models.university import University
from app.repositories.params import PaginatedResult, PaginationParams
from app.repositories.transaction import TransactionManager
from app.repositories.university_repository import UniversityRepository
from app.services.base import BaseService


class UniversityService(BaseService[University, Any, Any]):
    repository: UniversityRepository

    def __init__(
        self, repository: UniversityRepository, transaction_manager: TransactionManager
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    def _to_model(self, obj_in: Any) -> University:
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else obj_in.copy() if isinstance(obj_in, dict) else dict(obj_in)
        )
        return University(**data)

    async def list_universities(
        self, pagination: PaginationParams
    ) -> PaginatedResult[University]:
        return await self.repository.list_universities(pagination)

    async def search(self, **kwargs: Any) -> Sequence[University]:
        return await self.repository.search(**kwargs)
