from dataclasses import dataclass


@dataclass
class MockUser:
    user_id: int
    role: str
    dept_id: int | None = None


def get_mock_user() -> MockUser:
    """Mock user dependency — Week 2 placeholder.

    Trả về HR_Manager mặc định.
    Week 6 thay bằng JWT decode thật.
    """
    return MockUser(user_id=1, role="HR_Manager", dept_id=1)
