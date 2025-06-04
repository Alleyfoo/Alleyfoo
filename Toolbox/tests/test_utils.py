import pytest
from toolbox.utils import hello_world

def test_hello_world():
    assert hello_world() == "Hello from Toolbox!"
