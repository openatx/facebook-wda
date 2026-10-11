import re
import uuid

import pytest

from wda import Element, Client, Selector
from wda.utils import convert


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


@pytest.fixture
def fake_wda(mock_client, monkeypatch):
    """ Answer POST /elements with two matches and record the queries.
    A trailing [n] in the class chain picks one match like WebDriverAgent:
    positions start at 1, negative ones count from the end.
    """
    matches = ["el-0", "el-1"]
    queries = []

    def _fetch(method, urlpath, data=None, with_session=False, timeout=None):
        assert (method, urlpath) == ("POST", "/elements")
        queries.append(data["value"])
        found = matches
        m = re.search(r"\[(-?\d+)\]$", data["value"])
        if m and int(m.group(1)):
            pos = int(m.group(1))
            if abs(pos) > len(matches):
                found = []
            else:
                found = [matches[pos - 1 if pos > 0 else pos]]
        return convert({"value": [{"ELEMENT": el} for el in found]})

    monkeypatch.setattr(mock_client, "_fetch", _fetch)
    return queries


@pytest.mark.parametrize("index, position", [(0, ""), (1, "[2]"), (2, "[3]")])
def test_class_chain_index(mock_client, fake_wda, index, position):
    mock_client(name="Cell")[index].find_element_ids()
    assert fake_wda == ["**/XCUIElementTypeAny[`name == 'Cell'`]" + position]


@pytest.mark.parametrize("flag, word", [(True, "true"), (False, "false")])
def test_class_chain_visible_enabled(mock_client, fake_wda, flag, word):
    mock_client(name="Cell", visible=flag, enabled=flag).find_element_ids()
    want = "visible == %s AND enabled == %s" % (word, word)
    assert fake_wda == ["**/XCUIElementTypeAny[`name == 'Cell' AND %s`]" % want]


def test_index_exists_and_get(mock_client, fake_wda):
    assert mock_client(name="Cell")[0].get().id == "el-0"
    assert mock_client(name="Cell")[1].exists
    assert mock_client(name="Cell")[1].get().id == "el-1"
    assert mock_client(name="Cell", index=1).get().id == "el-1"
    assert mock_client(name="Cell")[-1].get().id == "el-1"
    assert not mock_client(name="Cell")[2].exists
