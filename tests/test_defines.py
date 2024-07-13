from datetime import datetime
from entities.defines import floor_datetime

def test_floor_datetime():
    # Arrange
    input_datetime = datetime.fromisoformat("2000-01-01T01:02:03.456+01:00")

    # Act
    result = floor_datetime(input_datetime)

    # Assert
    expectedResult = datetime.fromisoformat("2000-01-01T01:02:00.000+01:00")

    assert result == expectedResult


def test_floor_datetime_already_floored():
    # Arrange
    input_datetime = datetime.fromisoformat("2000-01-01T01:02:00.000+01:00")

    # Act
    result = floor_datetime(input_datetime)

    # Assert
    expectedResult = datetime.fromisoformat("2000-01-01T01:02:00.000+01:00")

    assert result == expectedResult