# -*- coding: utf-8 -*-
"""
This allows to use global variables inside the FastAPI application using async mode.

# Usage
Just import `g` and then access (set/get) attributes of it:
```python
from your_project.globals import g
g.foo = "foo"
# In some other code
assert g.foo == "foo"
```
Best way to utilize the global `g` in your code is to set the desired
value in a FastAPI dependency, like so:
```python
async def set_global_foo() -> None:
    g.foo = "foo"
@app.get("/test/", dependencies=[Depends(set_global_foo)])
async def test():
    assert g.foo == "foo"
```
# Setup
Add the `GlobalsMiddleware` to your app:
```python
app = fastapi.FastAPI(
    title="Your app API",
)
app.add_middleware(GlobalsMiddleware)  # <-- This line is necessary
```
Then just use it. ;-)
# Default values
You may use `g.set_default("name", some_value)` to set a default value
for a global variable. This default value will then be used instead of `None`
when the variable is accessed before it was set.
Note that default values should only be set at startup time, never
inside dependencies or similar. Otherwise you may run into the issue that
the value was already used any thus have a value of `None` set already, which
would result in the default value not being used.

Reference: https://gist.github.com/ddanier/ead419826ac6c3d75c96f9d89bea9bd0
"""
from collections.abc import Awaitable, Callable
from contextvars import ContextVar, copy_context
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class Globals:
    """Globals context."""

    __slots__ = (
        "_vars",
        "_defaults",
    )

    _vars: dict[
        str,
        ContextVar,
    ]
    _defaults: dict[
        str,
        Any,
    ]

    def __init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "_vars",
            {},
        )
        object.__setattr__(
            self,
            "_defaults",
            {},
        )

    def cleanup(
        self,
    ) -> None:
        """Clear all variables and free memory."""

        self._vars.clear()
        self._defaults.clear()
        del self._vars
        del self._defaults

    def set_default(
        self,
        name: str,
        default: Any,
    ) -> None:
        """Set a default value for a variable."""

        # Ignore if default is already set and is the same value
        if name in self._defaults and default is self._defaults[name]:
            return

        # Ensure we don't have a value set already - the default will have
        # no effect then
        if name in self._vars:
            raise RuntimeError(
                f"Cannot set default as variable {name} was already set",
            )

        # Set the default already!
        self._defaults[name] = default

    def _get_default_value(
        self,
        name: str,
    ) -> Any:
        """Get the default value for a variable."""

        default = self._defaults.get(
            name,
            None,
        )

        return default

    def _ensure_var(
        self,
        name: str,
    ) -> None:
        """Ensure a ContextVar exists for a variable."""
        if name not in self._vars:
            default = self._get_default_value(name)
            self._vars[name] = ContextVar(
                f"globals:{name}",
                default=default,
            )

    def __getattr__(
        self,
        name: str,
    ) -> Any:
        """Get the value of a variable."""

        self._ensure_var(name)
        return self._vars[name].get()

    def __setattr__(
        self,
        name: str,
        value: Any,
    ) -> None:
        """Set the value of a variable."""

        self._ensure_var(name)
        self._vars[name].set(value)


async def globals_middleware_dispatch(
    request: Request,
    call_next: Callable,
) -> Response:
    """Dispatch the request in a new context to allow globals to be used."""

    ctx = copy_context()

    def _call_next() -> Awaitable[Response]:
        return call_next(request)

    return await ctx.run(_call_next)


class GlobalsMiddleware(BaseHTTPMiddleware):  # noqa
    """Middleware to setup the globals context using globals_middleware_dispatch()."""

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(
            app,
            globals_middleware_dispatch,
        )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        return await call_next(request)


g = Globals()
