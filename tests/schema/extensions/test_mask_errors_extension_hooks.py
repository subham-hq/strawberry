from collections.abc import Iterator
from unittest.mock import Mock

import pytest

import strawberry
from strawberry.extensions import MaskErrors, SchemaExtension


def _extension_raising_in(hook: str) -> type[SchemaExtension]:
    def raise_error(self: SchemaExtension) -> Iterator[None]:
        raise ValueError("Secret error raised by an extension")
        yield  # pragma: no cover

    return type("RaisingExtension", (SchemaExtension,), {hook: raise_error})


@strawberry.type
class _HelloQuery:
    @strawberry.field
    def hello(self) -> str:
        return "Hello"


@pytest.mark.parametrize("hook", ["on_parse", "on_validate", "on_execute"])
def test_mask_errors_raised_in_extension_hooks_sync(hook: str):
    schema = strawberry.Schema(
        query=_HelloQuery, extensions=[MaskErrors(), _extension_raising_in(hook)]
    )

    result = schema.execute_sync("{ hello }")

    assert result.data is None
    assert result.errors is not None
    assert [error.message for error in result.errors] == ["Unexpected error."]


@pytest.mark.parametrize("hook", ["on_parse", "on_validate", "on_execute"])
async def test_mask_errors_raised_in_extension_hooks_async(hook: str):
    schema = strawberry.Schema(
        query=_HelloQuery, extensions=[MaskErrors(), _extension_raising_in(hook)]
    )

    result = await schema.execute("{ hello }")

    assert result.data is None
    assert result.errors is not None
    assert [error.message for error in result.errors] == ["Unexpected error."]


def test_process_errors_gets_original_error_raised_in_extension_hook():
    mock_process_error = Mock()

    class CustomSchema(strawberry.Schema):
        def process_errors(self, errors, execution_context):
            for error in errors:
                mock_process_error(error)

    schema = CustomSchema(
        query=_HelloQuery,
        extensions=[MaskErrors(), _extension_raising_in("on_execute")],
    )

    result = schema.execute_sync("{ hello }")

    assert result.errors is not None
    assert [error.message for error in result.errors] == ["Unexpected error."]
    assert mock_process_error.call_count == 1
    error = mock_process_error.call_args_list[0][0][0]
    assert error.message == "Secret error raised by an extension"
    assert isinstance(error.original_error, ValueError)
