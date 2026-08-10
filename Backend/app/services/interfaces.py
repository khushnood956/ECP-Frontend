from collections.abc import Sequence
from typing import Any, Protocol, TypeVar
from uuid import UUID

ModelType_co = TypeVar("ModelType_co", covariant=True)
CreateSchemaType_contra = TypeVar("CreateSchemaType_contra", contravariant=True)
UpdateSchemaType_contra = TypeVar("UpdateSchemaType_contra", contravariant=True)


class IService(Protocol[ModelType_co, CreateSchemaType_contra, UpdateSchemaType_contra]):
    """
    Abstract interface defining common operations expected from all domain services.
    Ensures consistency across the service layer and facilitates mocking for tests.
    """

    async def create(self, obj_in: CreateSchemaType_contra) -> ModelType_co:
        """
        Create a new entity based on the provided schema.

        Args:
            obj_in: The data required to create the new entity.

        Returns:
            The created domain model.
        """
        ...

    async def get_by_id(self, id: UUID) -> ModelType_co | None:
        """
        Retrieve a single entity by its unique identifier.

        Args:
            id: The UUID of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    async def update(self, id: UUID, obj_in: UpdateSchemaType_contra) -> ModelType_co | None:
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

    async def list(self, **kwargs: Any) -> Sequence[ModelType_co]:
        """
        Retrieve a list of entities matching the given criteria.

        Args:
            **kwargs: Filtering criteria.

        Returns:
            A sequence of matching domain models.
        """
        ...
