"""Test tool utils."""
from typing import Optional, Type

import pytest
from pydantic import BaseModel

from langchain.agents.tools import Tool, tool
from langchain.tools.base import BaseTool


def test_unnamed_decorator() -> None:
    """Test functionality with unnamed decorator."""

    @tool
    def search_api(query: str) -> str:
        """Search the API for the query."""
        return "API result"

    assert isinstance(search_api, Tool)
    assert search_api.name == "search_api"
    assert not search_api.return_direct
    assert search_api("test") == "API result"


class _MockSchema(BaseModel):
    arg1: int
    arg2: bool
    arg3: Optional[dict] = None


class _MockStructuredTool(BaseTool):
    name = "structured_api"
    args_schema: Type[BaseModel] = _MockSchema
    description = "A Structured Tool"

    def _run(self, arg1: int, arg2: bool, arg3: Optional[dict] = None) -> str:
        return f"{arg1} {arg2} {arg3}"

    async def _arun(self, arg1: int, arg2: bool, arg3: Optional[dict] = None) -> str:
        raise NotImplementedError


def test_structured_args() -> None:
    """Test functionality with structured arguments."""
    structured_api = _MockStructuredTool()
    assert isinstance(structured_api, BaseTool)
    assert structured_api.name == "structured_api"
    expected_result = "1 True {'foo': 'bar'}"
    args = {"arg1": 1, "arg2": True, "arg3": {"foo": "bar"}}
    assert structured_api.run(args) == expected_result


def test_named_tool_decorator() -> None:
    """Test functionality when arguments are provided as input to decorator."""

    @tool("search")
    def search_api(query: str) -> str:
        """Search the API for the query."""
        return "API result"

    assert isinstance(search_api, Tool)
    assert search_api.name == "search"
    assert not search_api.return_direct


def test_named_tool_decorator_return_direct() -> None:
    """Test functionality when arguments and return direct are provided as input."""

    @tool("search", return_direct=True)
    def search_api(query: str) -> str:
        """Search the API for the query."""
        return "API result"

    assert isinstance(search_api, Tool)
    assert search_api.name == "search"
    assert search_api.return_direct


def test_unnamed_tool_decorator_return_direct() -> None:
    """Test functionality when only return direct is provided."""

    @tool(return_direct=True)
    def search_api(query: str) -> str:
        """Search the API for the query."""
        return "API result"

    assert isinstance(search_api, Tool)
    assert search_api.name == "search_api"
    assert search_api.return_direct


def test_missing_docstring() -> None:
    """Test error is raised when docstring is missing."""
    # expect to throw a value error if theres no docstring
    with pytest.raises(AssertionError):

        @tool
        def search_api(query: str) -> str:
            return "API result"


def test_create_tool_posistional_args() -> None:
    """Test that positional arguments are allowed."""
    test_tool = Tool("test_name", lambda x: x, "test_description")
    assert test_tool("foo") == "foo"
    assert test_tool.name == "test_name"
    assert test_tool.description == "test_description"


def test_create_tool_keyword_args() -> None:
    """Test that keyword arguments are allowed."""
    test_tool = Tool(name="test_name", func=lambda x: x, description="test_description")
    assert test_tool("foo") == "foo"
    assert test_tool.name == "test_name"
    assert test_tool.description == "test_description"


@pytest.mark.asyncio
async def test_create_async_tool() -> None:
    """Test that async tools are allowed."""

    async def _test_func(x: str) -> str:
        return x

    test_tool = Tool(
        name="test_name",
        func=lambda x: x,
        description="test_description",
        coroutine=_test_func,
    )
    assert test_tool("foo") == "foo"
    assert test_tool.name == "test_name"
    assert test_tool.description == "test_description"
    assert test_tool.coroutine is not None
    assert await test_tool.arun("foo") == "foo"
