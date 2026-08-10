from collections.abc import Sequence
from typing import Any, Generic, TypeVar, cast
from uuid import UUID

from app.db.base import UUIDPrimaryKeyMixin
from app.repositories.interfaces import IRepository
from app.repositories.transaction import TransactionManager
from app.services.exceptions import BusinessRuleViolation, EntityNotFound
from app.services.interfaces import IService

ModelType = TypeVar("ModelType", bound=UUIDPrimaryKeyMixin)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(
    IService[ModelType, CreateSchemaType, UpdateSchemaType],
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
    """
    Generic base service implementation providing common CRUD operations.
    Follows SOLID principles by relying on abstractions (IRepository).
    Business logic avoiding database connections/FastAPI specifics directly.
    """

    def __init__(
        self,
        repository: IRepository[ModelType],
        transaction_manager: TransactionManager,
    ) -> None:
        """
        Initialize the base service using constructor dependency injection.

        Args:
            repository: The repository responsible for data access operations.
            transaction_manager: The manager handling database transactions.
        """
        self.repository = repository
        self.transaction_manager = transaction_manager

    async def _require_entity(self, id: UUID) -> ModelType:
        """
        Verify that an entity exists by its ID and return it.

        Args:
            id: The UUID of the entity to verify.

        Returns:
            The domain model if found.

        Raises:
            EntityNotFound: If the entity with the given ID does not exist.
        """
        existing_obj = await self.repository.get_by_id(id)
        if not existing_obj:
            raise EntityNotFound(f"Entity with id {id} not found.")
        return existing_obj

    def _prevent_redundant_state(
        self, current_state: Any, target_state: Any, error_message: str
    ) -> None:
        """
        Validates that an entity is not already in the target state.
        Raises BusinessRuleViolation if the current state matches the target state.
        """
        if current_state == target_state:
            raise BusinessRuleViolation(error_message)

    def _to_model(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Convert a creation schema into an ORM model instance.
        Must be implemented by concrete services.
        """
        raise NotImplementedError(
            "Subclasses must implement _to_model to convert CreateSchemaType to ModelType."
        )

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new entity wrapped in a transaction.

        Args:
            obj_in: The schema containing the data for the new entity.

        Returns:
            The created domain model.
        """
        async with self.transaction_manager.transaction():
            model_instance = self._to_model(obj_in)
            return await self.repository.create(model_instance)

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """
        Retrieve an entity by its unique identifier.

        Args:
            id: The UUID of the entity.

        Returns:
            The domain model if found, None otherwise.
        """
        return await self.repository.get_by_id(id)

    async def update(self, id: UUID, obj_in: UpdateSchemaType) -> ModelType | None:
        """
        Update an existing entity wrapped in a transaction.
        Checks for existence before updating.

        Args:
            id: The UUID of the entity to update.
            obj_in: The schema containing the updated data.

        Returns:
            The updated domain model.

        Raises:
            EntityNotFound: If the entity with the given ID does not exist.
        """
        async with self.transaction_manager.transaction():
            await self._require_entity(id)

            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else cast(dict[str, Any], obj_in)
            )
            return await self.repository.update(id, update_data)

    async def delete(self, id: UUID) -> bool:
        """
        Delete an entity by its unique identifier wrapped in a transaction.
        Checks for existence before deleting.

        Args:
            id: The UUID of the entity to delete.

        Returns:
            True if deleted successfully.

        Raises:
            EntityNotFound: If the entity with the given ID does not exist.
        """
        async with self.transaction_manager.transaction():
            await self._require_entity(id)

            return await self.repository.delete(id)

    async def list(self, **kwargs: Any) -> Sequence[ModelType]:
        """
        Retrieve a list of entities based on provided kwargs filtering.

        Args:
            **kwargs: Arbitrary filtering criteria.

        Returns:
            A sequence of matching domain models.
        """
        return await self.repository.list(**kwargs)
