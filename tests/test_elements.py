import uuid

import pytest

from wda import Element, Client, Selector


@pytest.fixture
def mock_client(monkeypatch):
    yield Client()


def test_eq(mock_client):
    el1 = Element(session=mock_client, id=uuid.uuid4().hex)
    el2 = Element(session=mock_client, id=uuid.uuid4().hex)
    assert el1 != el2
    assert el1 == el1


def test_find_elements_eq(mock_client, monkeypatch):
    el = Element(session=mock_client, id=uuid.uuid4().hex)
    monkeypatch.setattr(Selector, "find_element_ids", lambda *args, **kwargs: [el])
    el1 = mock_client(type="XCUIElementTypeStaticText").get(0)
    el2 = mock_client(type="XCUIElementTypeStaticText").get(0)
    assert el1 == el2

def test_find_elements_not_eq(mock_client, monkeypatch):
    def find_element_ids(*args, **kwargs):
        return [Element(session=mock_client, id=uuid.uuid4().hex)]
    monkeypatch.setattr(Selector, "find_element_ids", find_element_ids)
    el1 = mock_client(type="XCUIElementTypeStaticText").get(0)
    el2 = mock_client(type="XCUIElementTypeStaticText").get(0)
    assert el1 != el2