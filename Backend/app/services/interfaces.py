from typing import Protocol, TypeVar, Any, Sequence, Optional
from uuid import UUID

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class IService(Protocol[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract interface defining common operations expected from all domain services.
    Ensures consistency across the service layer and facilitates mocking for tests.
    """

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new entity based on the provided schema.

        Args:
            obj_in: The data required to create the new entity.

        Returns:
            The created domain model.
        """
        ...

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Retrieve a single entity by its unique identifier.

        Args:
            id: The UUID of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    async def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """
        Update an existing entity with the provided data.

        Args:
            id: The UUID of the entity to update.
            obj_in: The updated data schema.

        Returns:
            The updated domain model, or None if not found.
        """
        ...

    async def delete(self, id: UUID) -> bool:
        """
        Delete an entity by its unique identifier.

        Args:
            id: The UUID of the entity to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        ...

    async def list(self, **kwargs: Any) -> Sequence[ModelType]:
        """
        Retrieve a list of entities matching the given criteria.

        Args:
            **kwargs: Filtering criteria.

        Returns:
            A sequence of matching domain models.
        """
        ...
