from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.exceptions import RepositoryError
from app.repositories.params import (
    FilterCondition,
    FilterOperator,
    PaginationParams,
    SortParams,
)
from app.repositories.transaction import TransactionManager


@pytest_asyncio.fixture
async def base_user(db_session: AsyncSession):
    user = User(
        id=str(uuid4()),
        email=f"{uuid4()}@example.com",
        password_hash="hash",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_base_repository_create_and_get(
    db_session: AsyncSession, base_user: User
):
    repo = BaseRepository(StudentProfile, db_session)
    profile_id = str(uuid4())

    # Test Create
    new_profile = StudentProfile(
        id=profile_id,
        user_id=base_user.id,
        first_name="John",
        last_name="Doe",
    )
    created = await repo.create(new_profile)
    assert created.id == profile_id
    assert created.first_name == "John"

    # Test Get by ID
    fetched = await repo.get_by_id(profile_id)
    assert fetched is not None
    assert fetched.id == profile_id
    assert fetched.last_name == "Doe"

    # Test Not Found
    not_found = await repo.get_by_id(str(uuid4()))
    assert not_found is None


@pytest.mark.asyncio
async def test_base_repository_update_and_delete(
    db_session: AsyncSession, base_user: User
):
    repo = BaseRepository(StudentProfile, db_session)
    profile_id = str(uuid4())

    new_profile = StudentProfile(
        id=profile_id,
        user_id=base_user.id,
        first_name="Jane",
        last_name="Smith",
    )
    await repo.create(new_profile)

    # Test Update
    updated = await repo.update(profile_id, {"first_name": "Janet"})
    assert updated is not None
    assert updated.first_name == "Janet"
    assert updated.last_name == "Smith"  # Unchanged

    # Test Delete
    deleted = await repo.delete(profile_id)
    assert deleted is True

    fetched = await repo.get_by_id(profile_id)
    assert fetched is None

    # Delete non-existent
    deleted_again = await repo.delete(profile_id)
    assert deleted_again is False


@pytest.mark.asyncio
async def test_base_repository_list(db_session: AsyncSession, base_user: User):
    repo = BaseRepository(StudentProfile, db_session)

    p1 = StudentProfile(
        id=str(uuid4()), user_id=base_user.id, first_name="Alice", last_name="B"
    )
    await repo.create(p1)

    results = await repo.list(first_name="Alice")
    assert len(results) == 1
    assert results[0].first_name == "Alice"


@pytest.mark.asyncio
async def test_transaction_commit(db_session: AsyncSession, base_user: User):
    tm = TransactionManager(db_session)
    repo = BaseRepository(StudentProfile, db_session)

    profile_id = str(uuid4())
    async with tm.transaction():
        profile = StudentProfile(
            id=profile_id, user_id=base_user.id, first_name="Tx", last_name="Commit"
        )
        await repo.create(profile)

    # Transaction closed and committed
    stmt = select(StudentProfile).where(StudentProfile.id == profile_id)
    result = await db_session.execute(stmt)
    saved = result.scalar_one_or_none()
    assert saved is not None
    assert saved.first_name == "Tx"


@pytest.mark.asyncio
async def test_transaction_rollback(db_session: AsyncSession, base_user: User):
    tm = TransactionManager(db_session)
    repo = BaseRepository(StudentProfile, db_session)

    profile_id = str(uuid4())

    class DummyException(Exception):
        pass

    try:
        async with tm.transaction():
            profile = StudentProfile(
                id=profile_id,
                user_id=base_user.id,
                first_name="Tx",
                last_name="Rollback",
            )
            await repo.create(profile)
            raise DummyException("Force rollback")
    except DummyException:
        pass

    # Should not exist
    stmt = select(StudentProfile).where(StudentProfile.id == profile_id)
    result = await db_session.execute(stmt)
    saved = result.scalar_one_or_none()
    assert saved is None


@pytest.mark.asyncio
async def test_pagination_and_sorting(db_session: AsyncSession):
    repo = BaseRepository(StudentProfile, db_session)

    # Create 25 records
    users = []
    for i in range(25):
        u = User(
            id=str(uuid4()),
            email=f"test{i}@x.com",
            password_hash="h",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
        )
        users.append(u)

    db_session.add_all(users)
    await db_session.flush()

    profiles = []
    for i in range(25):
        profiles.append(
            StudentProfile(
                id=str(uuid4()),
                user_id=users[i].id,
                first_name=f"User{i:02d}",
                last_name="Test",
            )
        )

    await repo.bulk_create(profiles)
    await db_session.flush()

    # Test pagination
    paginated = await repo.list_paginated(
        pagination=PaginationParams(page=1, page_size=10)
    )
    assert paginated.total == 25
    assert len(paginated.items) == 10
    assert paginated.total_pages == 3
    assert paginated.page == 1

    # Test sorting
    sorted_res = await repo.list_paginated(
        pagination=PaginationParams(page=1, page_size=10),
        sort=SortParams(sort_by="first_name", sort_order="desc"),
    )
    assert sorted_res.items[0].first_name == "User24"


@pytest.mark.asyncio
async def test_filtering(db_session: AsyncSession, base_user: User):
    repo = BaseRepository(StudentProfile, db_session)
    p1 = StudentProfile(
        id=str(uuid4()),
        user_id=base_user.id,
        first_name="Alice",
        last_name="Smith",
        city="NY",
    )
    await repo.create(p1)

    # test EQ
    res = await repo.list_paginated(
        pagination=PaginationParams(page=1, page_size=10),
        filters=[
            FilterCondition(
                field="first_name", operator=FilterOperator.EQ, value="Alice"
            )
        ],
    )
    assert res.total == 1

    # test IN
    res2 = await repo.list_paginated(
        pagination=PaginationParams(page=1, page_size=10),
        filters=[
            FilterCondition(
                field="city", operator=FilterOperator.IN, value=["NY", "LA"]
            )
        ],
    )
    assert res2.total == 1

    # test LIKE
    res3 = await repo.list_paginated(
        pagination=PaginationParams(page=1, page_size=10),
        filters=[
            FilterCondition(
                field="last_name", operator=FilterOperator.LIKE, value="mit"
            )
        ],
    )
    assert res3.total == 1

    # test IS_NULL
    res4 = await repo.list_paginated(
        pagination=PaginationParams(page=1, page_size=10),
        filters=[
            FilterCondition(field="bio", operator=FilterOperator.IS_NULL, value=True)
        ],
    )
    assert res4.total == 1

    # test Invalid Field
    with pytest.raises(RepositoryError):
        await repo.list_paginated(
            pagination=PaginationParams(page=1, page_size=10),
            filters=[
                FilterCondition(
                    field="invalid_col", operator=FilterOperator.EQ, value="val"
                )
            ],
        )


@pytest.mark.asyncio
async def test_bulk_operations(db_session: AsyncSession):
    repo = BaseRepository(StudentProfile, db_session)

    users = [
        User(
            id=str(uuid4()),
            email=f"b{i}@x.com",
            password_hash="h",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
        )
        for i in range(3)
    ]
    db_session.add_all(users)
    await db_session.flush()

    profiles = [
        StudentProfile(
            id=str(uuid4()), user_id=users[0].id, first_name="A", last_name="A"
        ),
        StudentProfile(
            id=str(uuid4()), user_id=users[1].id, first_name="B", last_name="B"
        ),
        StudentProfile(
            id=str(uuid4()), user_id=users[2].id, first_name="C", last_name="C"
        ),
    ]

    # Bulk Create
    created = await repo.bulk_create(profiles)
    assert len(created) == 3
    await db_session.flush()

    # Bulk Update
    updates = [
        (profiles[0].id, {"first_name": "A_mod"}),
        (profiles[1].id, {"first_name": "B_mod"}),
    ]
    affected = await repo.bulk_update(updates)
    assert affected == 2
    await db_session.flush()

    p0 = await repo.get_by_id(profiles[0].id)
    assert p0.first_name == "A_mod"

    # Bulk Delete
    deleted_count = await repo.bulk_delete([profiles[0].id, profiles[1].id])
    assert deleted_count == 2
    await db_session.flush()

    remaining = await repo.list()
    assert len(remaining) == 1
    assert remaining[0].id == profiles[2].id
