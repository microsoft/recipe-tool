# gradio-app/gradio/gradio

[git-collector-data]

**URL:** https://github.com/gradio-app/gradio/tree/main/gradio  
**Date:** 6/18/2025, 12:11:09 PM  
**Files:** 10  

=== File: gradio/blocks.py ===
from __future__ import annotations

import asyncio
import copy
import dataclasses
import hashlib
import inspect
import json
import os
import random
import re
import secrets
import string
import sys
import threading
import time
import warnings
import webbrowser
from collections import defaultdict
from collections.abc import AsyncIterator, Callable, Coroutine, Sequence, Set
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Literal, Union, cast
from urllib.parse import urlparse, urlunparse

import anyio
import fastapi
import httpx
from anyio import CapacityLimiter
from gradio_client import utils as client_utils
from gradio_client.documentation import document
from groovy import transpile

from gradio import (
    analytics,
    components,
    networking,
    processing_utils,
    queueing,
    themes,
    utils,
    wasm_utils,
)
from gradio.blocks_events import BLOCKS_EVENTS, BlocksEvents, BlocksMeta
from gradio.context import (
    Context,
    LocalContext,
    get_blocks_context,
    get_render_context,
    set_render_context,
)
from gradio.data_classes import (
    APIEndpointInfo,
    APIInfo,
    BlocksConfigDict,
    DeveloperPath,
    FileData,
    GradioModel,
    GradioRootModel,
    Layout,
)
from gradio.events import (
    EventData,
    EventListener,
    EventListenerMethod,
)
from gradio.exceptions import (
    ChecksumMismatchError,
    DuplicateBlockError,
    InvalidApiNameError,
    InvalidComponentError,
)
from gradio.helpers import create_tracker, skip, special_args
from gradio.i18n import I18n, I18nData
from gradio.node_server import start_node_server
from gradio.route_utils import API_PREFIX, MediaStream
from gradio.routes import INTERNAL_ROUTES, VERSION, App, Request
from gradio.state_holder import SessionState, StateHolder
from gradio.themes import Default as DefaultTheme
from gradio.themes import ThemeClass as Theme
from gradio.tunneling import (
    BINARY_FILENAME,
    BINARY_FOLDER,
    BINARY_PATH,
    BINARY_URL,
    CURRENT_TUNNELS,
)
from gradio.utils import (
    TupleNoPrint,
    check_function_inputs_match,
    component_or_layout_class,
    get_cancelled_fn_indices,
    get_node_path,
    get_package_version,
    get_upload_folder,
)

try:
    import spaces  # type: ignore
except Exception:
    spaces = None


if TYPE_CHECKING:  # Only import for type checking (is False at runtime).
    from gradio.components.base import Component
    from gradio.mcp import GradioMCPServer
    from gradio.renderable import Renderable

BUILT_IN_THEMES: dict[str, Theme] = {
    t.name: t
    for t in [
        themes.Base(),
        themes.Default(),
        themes.Monochrome(),
        themes.Soft(),
        themes.Glass(),
        themes.Origin(),
        themes.Citrus(),
        themes.Ocean(),
    ]
}


class Block:
    def __init__(
        self,
        *,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        visible: bool = True,
        proxy_url: str | None = None,
    ):
        key_to_id_map = LocalContext.key_to_id_map.get()
        if key is not None and key_to_id_map and key in key_to_id_map:
            self.is_render_replacement = True
            self._id = key_to_id_map[key]
        else:
            self.is_render_replacement = False
            self._id = Context.id
            Context.id += 1
            if key is not None and key_to_id_map is not None:
                key_to_id_map[key] = self._id
        self.visible = visible
        self.elem_id = elem_id
        self.elem_classes = (
            [elem_classes] if isinstance(elem_classes, str) else elem_classes
        )
        self.proxy_url = proxy_url
        self.share_token = secrets.token_urlsafe(32)
        self.parent: BlockContext | None = None
        self.rendered_in: Renderable | None = None
        self.page: str
        self.is_rendered: bool = False
        self._constructor_args: list[dict]
        self.state_session_capacity = 10000
        self.temp_files: set[str] = set()
        self.GRADIO_CACHE = get_upload_folder()
        self.key = key
        self.preserved_by_key = (
            [preserved_by_key]
            if isinstance(preserved_by_key, str)
            else (preserved_by_key or [])
        )
        self.mcp_server_obj = None

        # Keep tracks of files that should not be deleted when the delete_cache parmameter is set
        # These files are the default value of the component and files that are used in examples
        self.keep_in_cache = set()
        self.has_launched = False

        if render:
            self.render()

    def unique_key(self) -> int | None:
        if self.key is None:
            return None
        return hash((self.rendered_in._id if self.rendered_in else None, self.key))

    @property
    def stateful(self) -> bool:
        return False

    @property
    def skip_api(self) -> bool:
        return False

    @property
    def constructor_args(self) -> dict[str, Any]:
        """Get the arguments passed to the component's initializer.

        Only set classes whose metaclass is ComponentMeta
        """
        # the _constructor_args list is appended based on the mro of the class
        # so the first entry is for the bottom of the hierarchy
        return self._constructor_args[0] if self._constructor_args else {}

    @property
    def events(
        self,
    ) -> list[EventListener]:
        return getattr(self, "EVENTS", [])

    def render(self):
        """
        Adds self into appropriate BlockContext
        """
        root_context = get_blocks_context()
        render_context = get_render_context()
        self.rendered_in = LocalContext.renderable.get()
        if (
            root_context is not None
            and self._id in root_context.blocks
            and not self.is_render_replacement
        ):
            raise DuplicateBlockError(
                f"A block with id: {self._id} has already been rendered in the current Blocks."
            )
        if render_context is not None:
            if root_context:
                self.page = root_context.root_block.current_page
            render_context.add(self)
            self.parent = render_context
        if root_context is not None:
            root_context.blocks[self._id] = self
            self.is_rendered = True
            if isinstance(self, components.Component):
                root_context.root_block.temp_file_sets.append(self.temp_files)
        return self

    def unrender(self):
        """
        Removes self from BlockContext if it has been rendered (otherwise does nothing).
        Removes self from the layout and collection of blocks, but does not delete any event triggers.
        """
        root_context = get_blocks_context()
        if hasattr(self, "parent") and self.parent is not None:
            try:
                self.parent.children.remove(self)
                self.parent = None
            except ValueError:
                pass
        if root_context is not None:
            try:
                del root_context.blocks[self._id]
                self.is_rendered = False
            except KeyError:
                pass
        return self

    def get_block_name(self) -> str:
        """
        Gets block's class name. If it is template component it gets the parent's class name.
        This is used to identify the Svelte file to use in the frontend. Override this method
        if a component should use a different Svelte file than the default naming convention.
        """
        return (
            self.__class__.__base__.__name__.lower()  # type: ignore
            if hasattr(self, "is_template")
            else self.__class__.__name__.lower()
        )

    def get_block_class(self) -> str:
        """
        Gets block's class name. If it is template component it gets the parent's class name.
        Very similar to the get_block_name method, but this method is used to reconstruct a
        Gradio app that is loaded from a Space using gr.load(). This should generally
        NOT be overridden.
        """
        return (
            self.__class__.__base__.__name__.lower()  # type: ignore
            if hasattr(self, "is_template")
            else self.__class__.__name__.lower()
        )

    def get_expected_parent(self) -> type[BlockContext] | None:
        return None

    def get_config(self):
        config = {}
        signature = inspect.signature(self.__class__.__init__)
        for parameter in signature.parameters.values():
            if hasattr(self, parameter.name):
                value = getattr(self, parameter.name)
                if dataclasses.is_dataclass(value):
                    value = dataclasses.asdict(value)  # type: ignore
                config[parameter.name] = value
        for e in self.events:
            to_add = e.config_data()
            if to_add:
                config = {**to_add, **config}
        config.pop("render", None)
        config = {**config, "proxy_url": self.proxy_url, "name": self.get_block_class()}
        for event_attribute in ["_selectable", "_undoable", "_retryable", "likeable"]:
            if (attributable := getattr(self, event_attribute, None)) is not None:
                config[event_attribute] = attributable
        return config

    @classmethod
    def recover_kwargs(
        cls, props: dict[str, Any], additional_keys: list[str] | None = None
    ):
        """
        Recovers kwargs from a dict of props.
        """
        additional_keys = additional_keys or []
        signature = inspect.signature(cls.__init__)
        kwargs = {}
        for parameter in signature.parameters.values():
            if parameter.name in props and parameter.name not in additional_keys:
                kwargs[parameter.name] = props[parameter.name]
        return kwargs

    async def async_move_resource_to_block_cache(
        self, url_or_file_path: str | Path | None
    ) -> str | None:
        """Moves a file or downloads a file from a url to a block's cache directory, adds
        to to the block's temp_files, and returns the path to the file in cache. This
        ensures that the file is accessible to the Block and can be served to users.

        This async version of the function is used when this is being called within
        a FastAPI route, as this is not blocking.
        """
        if url_or_file_path is None:
            return None
        if isinstance(url_or_file_path, Path):
            url_or_file_path = str(url_or_file_path)

        if client_utils.is_http_url_like(url_or_file_path):
            temp_file_path = await processing_utils.async_ssrf_protected_download(
                url_or_file_path, cache_dir=self.GRADIO_CACHE
            )

            self.temp_files.add(temp_file_path)
        else:
            url_or_file_path = str(utils.abspath(url_or_file_path))
            if not utils.is_in_or_equal(url_or_file_path, self.GRADIO_CACHE):
                try:
                    temp_file_path = processing_utils.save_file_to_cache(
                        url_or_file_path, cache_dir=self.GRADIO_CACHE
                    )
                except FileNotFoundError:
                    # This can happen if when using gr.load() and the file is on a remote Space
                    # but the file is not the `value` of the component. For example, if the file
                    # is the `avatar_image` of the `Chatbot` component. In this case, we skip
                    # copying the file to the cache and just use the remote file path.
                    return url_or_file_path
            else:
                temp_file_path = url_or_file_path
            self.temp_files.add(temp_file_path)

        return temp_file_path

    def move_resource_to_block_cache(
        self, url_or_file_path: str | Path | None
    ) -> str | None:
        """Moves a file or downloads a file from a url to a block's cache directory, adds
        to to the block's temp_files, and returns the path to the file in cache. This
        ensures that the file is accessible to the Block and can be served to users.

        This sync version of the function is used when this is being called outside of
        a FastAPI route, e.g. when examples are being cached.
        """
        if url_or_file_path is None:
            return None
        if isinstance(url_or_file_path, Path):
            url_or_file_path = str(url_or_file_path)

        if client_utils.is_http_url_like(url_or_file_path):
            temp_file_path = processing_utils.save_url_to_cache(
                url_or_file_path, cache_dir=self.GRADIO_CACHE
            )

            self.temp_files.add(temp_file_path)
        else:
            url_or_file_path = str(utils.abspath(url_or_file_path))
            if not utils.is_in_or_equal(url_or_file_path, self.GRADIO_CACHE):
                try:
                    temp_file_path = processing_utils.save_file_to_cache(
                        url_or_file_path, cache_dir=self.GRADIO_CACHE
                    )
                except FileNotFoundError:
                    # This can happen if when using gr.load() and the file is on a remote Space
                    # but the file is not the `value` of the component. For example, if the file
                    # is the `avatar_image` of the `Chatbot` component. In this case, we skip
                    # copying the file to the cache and just use the remote file path.
                    return url_or_file_path
            else:
                temp_file_path = url_or_file_path
            self.temp_files.add(temp_file_path)

        return temp_file_path

    def serve_static_file(
        self, url_or_file_path: str | Path | dict | None
    ) -> dict | None:
        """If a file is a local file, moves it to the block's cache directory and returns
        a FileData-type dictionary corresponding to the file. If the file is a URL, returns a
        FileData-type dictionary corresponding to the URL. This ensures that the file is
        accessible in the frontend and can be served to users.

        Examples:
        >>> block.serve_static_file("https://gradio.app/logo.png") -> {"path": "https://gradio.app/logo.png", "url": "https://gradio.app/logo.png"}
        >>> block.serve_static_file("logo.png") -> {"path": "logo.png", "url": "/file=logo.png"}
        >>> block.serve_static_file({"path": "logo.png", "url": "/file=logo.png"}) -> {"path": "logo.png", "url": "/file=logo.png"}
        """
        if url_or_file_path is None:
            return None
        if isinstance(url_or_file_path, dict):
            return url_or_file_path
        if isinstance(url_or_file_path, Path):
            url_or_file_path = str(url_or_file_path)
        if client_utils.is_http_url_like(url_or_file_path):
            return FileData(path=url_or_file_path, url=url_or_file_path).model_dump()
        else:
            data = {"path": url_or_file_path, "meta": {"_type": "gradio.FileData"}}
            try:
                return processing_utils.move_files_to_cache(data, self)
            except AttributeError:  # Can be raised if this function is called before the Block is fully initialized.
                return data


class BlockContext(Block):
    def __init__(
        self,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        visible: bool = True,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            visible: If False, this will be hidden but included in the Blocks config file (its visibility can later be updated).
            render: If False, this will not be included in the Blocks config file at all.
        """
        self.children: list[Block] = []
        Block.__init__(
            self,
            elem_id=elem_id,
            elem_classes=elem_classes,
            visible=visible,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )

    TEMPLATE_DIR = DeveloperPath("./templates/")
    FRONTEND_DIR = "../../frontend/"

    @property
    def skip_api(self):
        return True

    @classmethod
    def get_component_class_id(cls) -> str:
        module_name = cls.__module__
        module_path = sys.modules[module_name].__file__
        module_hash = hashlib.sha256(
            f"{cls.__name__}_{module_path}".encode()
        ).hexdigest()
        return module_hash

    @property
    def component_class_id(self):
        return self.get_component_class_id()

    def add_child(self, child: Block):
        self.children.append(child)

    def __enter__(self):
        render_context = get_render_context()
        self.parent = render_context
        set_render_context(self)
        return self

    def add(self, child: Block):
        child.parent = self
        self.children.append(child)

    def fill_expected_parents(self):
        root_context = get_blocks_context()
        children = []
        pseudo_parent = None
        for child in self.children:
            expected_parent = child.get_expected_parent()
            if not expected_parent or isinstance(self, expected_parent):
                pseudo_parent = None
                children.append(child)
            else:
                if pseudo_parent is not None and isinstance(
                    pseudo_parent, expected_parent
                ):
                    pseudo_parent.add_child(child)
                else:
                    key = None
                    if child.key is not None:
                        if isinstance(child.key, tuple):
                            key = child.key + ("_parent",)
                        else:
                            key = (child.key, "_parent")
                    pseudo_parent = expected_parent(render=False, key=key)
                    pseudo_parent.parent = self
                    children.append(pseudo_parent)
                    pseudo_parent.add_child(child)
                    pseudo_parent.page = child.page
                    if root_context:
                        root_context.blocks[pseudo_parent._id] = pseudo_parent
                child.parent = pseudo_parent
        self.children = children

    def __exit__(self, exc_type: type[BaseException] | None = None, *args):
        set_render_context(self.parent)
        if exc_type is not None:
            return
        if getattr(self, "allow_expected_parents", True):
            self.fill_expected_parents()

    def postprocess(self, y):
        """
        Any postprocessing needed to be performed on a block context.
        """
        return y


class BlockFunction:
    def __init__(
        self,
        fn: Callable | None,
        inputs: Sequence[Component | BlockContext],
        outputs: Sequence[Component | BlockContext],
        preprocess: bool,
        postprocess: bool,
        inputs_as_dict: bool,
        targets: list[tuple[int | None, str]],
        _id: int,
        batch: bool = False,
        max_batch_size: int = 4,
        concurrency_limit: int | None | Literal["default"] = "default",
        concurrency_id: str | None = None,
        tracks_progress: bool = False,
        api_name: str | Literal[False] = False,
        js: str | Literal[True] | None = None,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        show_progress_on: Sequence[Component] | None = None,
        cancels: list[int] | None = None,
        collects_event_data: bool = False,
        trigger_after: int | None = None,
        trigger_only_on_success: bool = False,
        trigger_mode: Literal["always_last", "once", "multiple"] = "once",
        queue: bool = True,
        scroll_to_output: bool = False,
        show_api: bool = True,
        renderable: Renderable | None = None,
        rendered_in: Renderable | None = None,
        render_iteration: int | None = None,
        is_cancel_function: bool = False,
        connection: Literal["stream", "sse"] = "sse",
        time_limit: float | None = None,
        stream_every: float = 0.5,
        like_user_message: bool = False,
        event_specific_args: list[str] | None = None,
        page: str = "",
        js_implementation: str | None = None,
        key: str | int | tuple[int | str, ...] | None = None,
    ):
        self.fn = fn
        self._id = _id
        self.inputs = inputs
        self.outputs = outputs
        self.preprocess = preprocess
        self.postprocess = postprocess
        self.tracks_progress = tracks_progress
        self.concurrency_limit: int | None | Literal["default"] = concurrency_limit
        self.concurrency_id = concurrency_id or str(id(fn))
        self.batch = batch
        self.max_batch_size = max_batch_size
        self.total_runtime = 0
        self.total_runs = 0
        self.inputs_as_dict = inputs_as_dict
        self.targets = targets
        self.name = getattr(fn, "__name__", "fn") if fn is not None else None
        self.api_name = api_name
        self.js = js
        self.show_progress = show_progress
        self.show_progress_on = show_progress_on
        self.cancels = cancels or []
        self.collects_event_data = collects_event_data
        self.trigger_after = trigger_after
        self.trigger_only_on_success = trigger_only_on_success
        self.trigger_mode = trigger_mode
        self.queue = False if fn is None else queue
        self.scroll_to_output = False if utils.get_space() else scroll_to_output
        self.show_api = show_api
        self.types_generator = inspect.isgeneratorfunction(
            self.fn
        ) or inspect.isasyncgenfunction(self.fn)
        self.renderable = renderable
        self.rendered_in = rendered_in
        self.render_iteration = render_iteration
        self.page = page
        if js_implementation:
            self.fn.__js_implementation__ = js_implementation  # type: ignore

        # We need to keep track of which events are cancel events
        # so that the client can call the /cancel route directly
        self.is_cancel_function = is_cancel_function
        self.time_limit = time_limit
        self.stream_every = stream_every
        self.connection = connection
        self.like_user_message = like_user_message
        self.event_specific_args = event_specific_args
        self.key = key

        self.spaces_auto_wrap()

    def spaces_auto_wrap(self):
        if spaces is None:
            return
        if utils.get_space() is None:
            return
        self.fn = spaces.gradio_auto_wrap(self.fn)

    def __str__(self):
        return str(
            {
                "fn": self.name,
                "preprocess": self.preprocess,
                "postprocess": self.postprocess,
            }
        )

    def __repr__(self):
        return str(self)

    def get_config(self):
        return {
            "id": self._id,
            "targets": self.targets,
            "inputs": [block._id for block in self.inputs],
            "outputs": [block._id for block in self.outputs],
            "backend_fn": self.fn is not None,
            "js": self.js,
            "queue": self.queue,
            "api_name": self.api_name,
            "scroll_to_output": self.scroll_to_output,
            "show_progress": self.show_progress,
            "show_progress_on": None
            if self.show_progress_on is None
            else [block._id for block in self.show_progress_on],
            "batch": self.batch,
            "max_batch_size": self.max_batch_size,
            "cancels": self.cancels,
            "types": {
                "generator": self.types_generator,
                "cancel": self.is_cancel_function,
            },
            "collects_event_data": self.collects_event_data,
            "trigger_after": self.trigger_after,
            "trigger_only_on_success": self.trigger_only_on_success,
            "trigger_mode": self.trigger_mode,
            "show_api": self.show_api,
            "rendered_in": self.rendered_in._id if self.rendered_in else None,
            "render_id": self.renderable._id if self.renderable else None,
            "connection": self.connection,
            "time_limit": self.time_limit,
            "stream_every": self.stream_every,
            "like_user_message": self.like_user_message,
            "event_specific_args": self.event_specific_args,
            "js_implementation": getattr(self.fn, "__js_implementation__", None),
        }


def postprocess_update_dict(
    block: Component | BlockContext, update_dict: dict, postprocess: bool = True
):
    """
    Converts a dictionary of updates into a format that can be sent to the frontend to update the component.
    E.g. {"value": "2", "visible": True, "invalid_arg": "hello"}
    Into -> {"__type__": "update", "value": 2.0, "visible": True}
    Parameters:
        block: The Block that is being updated with this update dictionary.
        update_dict: The original update dictionary
        postprocess: Whether to postprocess the "value" key of the update dictionary.
    """
    value = update_dict.pop("value", components._Keywords.NO_VALUE)
    update_dict = {k: getattr(block, k) for k in update_dict if hasattr(block, k)}
    if value is not components._Keywords.NO_VALUE:
        if postprocess:
            update_dict["value"] = block.postprocess(value)
            if isinstance(update_dict["value"], (GradioModel, GradioRootModel)):
                update_dict["value"] = update_dict["value"].model_dump()
        else:
            update_dict["value"] = value
    update_dict["__type__"] = "update"
    return update_dict


def convert_component_dict_to_list(
    outputs_ids: list[int], predictions: dict
) -> list | dict:
    """
    Converts a dictionary of component updates into a list of updates in the order of
    the outputs_ids and including every output component. Leaves other types of dictionaries unchanged.
    E.g. {"textbox": "hello", "number": {"__type__": "generic_update", "value": "2"}}
    Into -> ["hello", {"__type__": "generic_update"}, {"__type__": "generic_update", "value": "2"}]
    """
    keys_are_blocks = [isinstance(key, Block) for key in predictions]
    if all(keys_are_blocks):
        reordered_predictions = [skip() for _ in outputs_ids]
        for component, value in predictions.items():
            if component._id not in outputs_ids:
                raise ValueError(
                    f"Returned component {component} not specified as output of function."
                )
            output_index = outputs_ids.index(component._id)
            reordered_predictions[output_index] = value
        predictions = utils.resolve_singleton(reordered_predictions)
    elif any(keys_are_blocks):
        raise ValueError(
            "Returned dictionary included some keys as Components. Either all keys must be Components to assign Component values, or return a List of values to assign output values in order."
        )
    return predictions


class BlocksConfig:
    def __init__(self, root_block: Blocks):
        self._id: int = 0
        self.root_block = root_block
        self.blocks: dict[int, Component | Block] = {}
        self.fns: dict[int, BlockFunction] = {}
        self.fn_id: int = 0

    def set_event_trigger(
        self,
        targets: Sequence[EventListenerMethod],
        fn: Callable | None,
        inputs: (
            Component
            | BlockContext
            | Sequence[Component | BlockContext]
            | Set[Component | BlockContext]
            | None
        ),
        outputs: (
            Component
            | BlockContext
            | Sequence[Component | BlockContext]
            | Set[Component | BlockContext]
            | None
        ),
        preprocess: bool = True,
        postprocess: bool = True,
        scroll_to_output: bool = False,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        show_progress_on: Component | Sequence[Component] | None = None,
        api_name: str | None | Literal[False] = None,
        js: str | Literal[True] | None = None,
        no_target: bool = False,
        queue: bool = True,
        batch: bool = False,
        max_batch_size: int = 4,
        cancels: list[int] | None = None,
        collects_event_data: bool | None = None,
        trigger_after: int | None = None,
        trigger_only_on_success: bool = False,
        trigger_mode: Literal["once", "multiple", "always_last"] | None = "once",
        concurrency_limit: int | None | Literal["default"] = "default",
        concurrency_id: str | None = None,
        show_api: bool = True,
        renderable: Renderable | None = None,
        is_cancel_function: bool = False,
        connection: Literal["stream", "sse"] = "sse",
        time_limit: float | None = None,
        stream_every: float = 0.5,
        like_user_message: bool = False,
        event_specific_args: list[str] | None = None,
        js_implementation: str | None = None,
        key: str | int | tuple[int | str, ...] | None = None,
    ) -> tuple[BlockFunction, int]:
        """
        Adds an event to the component's dependencies.
        Parameters:
            targets: a list of EventListenerMethod objects that define the event trigger
            fn: the function to run when the event is triggered
            inputs: the list of input components whose values will be passed to the function
            outputs: the list of output components whose values will be updated by the function
            preprocess: whether to run the preprocess methods of the input components before running the function
            postprocess: whether to run the postprocess methods of the output components after running the function
            scroll_to_output: whether to scroll to output of dependency on trigger
            show_progress: how to show the progress animation while event is running: "full" shows a spinner which covers the output component area as well as a runtime display in the upper right corner, "minimal" only shows the runtime display, "hidden" shows no progress animation at all
            show_progress_on: Component or list of components to show the progress animation on. If None, will show the progress animation on all of the output components.
            api_name: defines how the endpoint appears in the API docs. Can be a string, None, or False. If set to a string, the endpoint will be exposed in the API docs with the given name. If None (default), the name of the function will be used as the API endpoint. If False, the endpoint will not be exposed in the API docs and downstream apps (including those that `gr.load` this app) will not be able to use this event.
            js: Optional frontend js method to run before running 'fn'. Input arguments for js method are values of 'inputs' and 'outputs', return should be a list of values for output components
            no_target: if True, sets "targets" to [], used for the Blocks.load() event and .then() events
            queue: If True, will place the request on the queue, if the queue has been enabled. If False, will not put this event on the queue, even if the queue has been enabled. If None, will use the queue setting of the gradio app.
            batch: whether this function takes in a batch of inputs
            max_batch_size: the maximum batch size to send to the function
            cancels: a list of other events to cancel when this event is triggered. For example, setting cancels=[click_event] will cancel the click_event, where click_event is the return value of another components .click method.
            collects_event_data: whether to collect event data for this event
            trigger_after: if set, this event will be triggered after 'trigger_after' function index
            trigger_only_on_success: if True, this event will only be triggered if the previous event was successful (only applies if `trigger_after` is set)
            trigger_mode: If "once" (default for all events except `.change()`) would not allow any submissions while an event is pending. If set to "multiple", unlimited submissions are allowed while pending, and "always_last" (default for `.change()` and `.key_up()` events) would allow a second submission after the pending event is complete.
            concurrency_limit: If set, this is the maximum number of this event that can be running simultaneously. Can be set to None to mean no concurrency_limit (any number of this event can be running simultaneously). Set to "default" to use the default concurrency limit (defined by the `default_concurrency_limit` parameter in `queue()`, which itself is 1 by default).
            concurrency_id: If set, this is the id of the concurrency group. Events with the same concurrency_id will be limited by the lowest set concurrency_limit.
            show_api: whether to show this event in the "view API" page of the Gradio app, or in the ".view_api()" method of the Gradio clients. Unlike setting api_name to False, setting show_api to False will still allow downstream apps as well as the Clients to use this event. If fn is None, show_api will automatically be set to False.
            is_cancel_function: whether this event cancels another running event.
            connection: The connection format, either "sse" or "stream".
            time_limit: The time limit for the function to run. Parameter only used for the `.stream()` event.
            stream_every: The latency (in seconds) at which stream chunks are sent to the backend. Defaults to 0.5 seconds. Parameter only used for the `.stream()` event.
        Returns: dependency information, dependency index
        """
        # Support for singular parameter
        _targets = [
            (
                target.block._id if not no_target and target.block else None,
                target.event_name,
            )
            for target in targets
        ]
        if isinstance(inputs, Set):
            inputs_as_dict = True
            inputs = sorted(inputs, key=lambda x: x._id)
        else:
            inputs_as_dict = False
            if inputs is None:
                inputs = []
            elif not isinstance(inputs, Sequence):
                inputs = [inputs]

        if isinstance(outputs, Set):
            outputs = sorted(outputs, key=lambda x: x._id)
        elif outputs is None:
            outputs = []
        elif not isinstance(outputs, Sequence):
            outputs = [outputs]
        if show_progress_on and not isinstance(show_progress_on, Sequence):
            show_progress_on = [show_progress_on]

        if fn is not None and not cancels:
            check_function_inputs_match(fn, inputs, inputs_as_dict)

        if _targets and trigger_mode is None:
            if _targets[0][1] in ["change", "key_up"]:
                trigger_mode = "always_last"
            elif _targets[0][1] in ["stream"]:
                trigger_mode = "multiple"
        if trigger_mode is None:
            trigger_mode = "once"
        elif trigger_mode not in ["once", "multiple", "always_last"]:
            raise ValueError(
                f"Invalid value for parameter `trigger_mode`: {trigger_mode}. Please choose from: {['once', 'multiple', 'always_last']}"
            )

        fn_to_analyze = renderable.fn if renderable else fn
        _, progress_index, event_data_index = (
            special_args(fn_to_analyze) if fn_to_analyze else (None, None, None)
        )

        # If api_name is None or empty string, use the function name
        if api_name is None or isinstance(api_name, str) and api_name.strip() == "":
            if fn is not None:
                if not hasattr(fn, "__name__"):
                    if hasattr(fn, "__class__") and hasattr(fn.__class__, "__name__"):
                        name = fn.__class__.__name__
                    else:
                        name = "unnamed"
                else:
                    name = fn.__name__
                api_name = "".join(
                    [s for s in name if s not in set(string.punctuation) - {"-", "_"}]
                )
            elif js is not None:
                api_name = "js_fn"
                show_api = False
            else:
                api_name = "unnamed"
                show_api = False

        if api_name is not False:
            api_name = utils.append_unique_suffix(
                api_name,
                [
                    fn.api_name
                    for fn in self.fns.values()
                    if isinstance(fn.api_name, str)
                ],
            )
        else:
            show_api = False

        # The `show_api` parameter is False if: (1) the user explicitly sets it (2) the user sets `api_name` to False
        # or (3) the user sets `fn` to None (there's no backend function)

        if collects_event_data is None:
            collects_event_data = event_data_index is not None

        rendered_in = LocalContext.renderable.get()

        if js is True and inputs:
            raise ValueError(
                "Cannot create event: events with js=True cannot have inputs."
            )

        reuse_id = False
        fn_id = self.fn_id
        render_iteration = rendered_in.render_iteration if rendered_in else None

        if rendered_in and key is not None:
            for existing_fn in self.fns.values():
                if existing_fn.key == key:
                    reuse_id = True
                    fn_id = existing_fn._id
                    break

        block_fn = BlockFunction(
            fn,
            inputs,
            outputs,
            preprocess,
            postprocess,
            _id=fn_id,
            inputs_as_dict=inputs_as_dict,
            targets=_targets,
            batch=batch,
            max_batch_size=max_batch_size,
            concurrency_limit=concurrency_limit,
            concurrency_id=concurrency_id,
            tracks_progress=progress_index is not None,
            api_name=api_name,
            js=js,
            show_progress=show_progress,
            show_progress_on=show_progress_on,
            cancels=cancels,
            collects_event_data=collects_event_data,
            trigger_after=trigger_after,
            trigger_only_on_success=trigger_only_on_success,
            trigger_mode=trigger_mode,
            queue=queue,
            scroll_to_output=scroll_to_output,
            show_api=show_api,
            renderable=renderable,
            rendered_in=rendered_in,
            render_iteration=render_iteration,
            is_cancel_function=is_cancel_function,
            connection=connection,
            time_limit=time_limit,
            stream_every=stream_every,
            like_user_message=like_user_message,
            event_specific_args=event_specific_args,
            page=self.root_block.current_page,
            js_implementation=js_implementation,
            key=key,
        )

        self.fns[fn_id] = block_fn
        if not reuse_id:
            self.fn_id += 1
        return block_fn, block_fn._id

    @staticmethod
    def config_for_block(
        _id: int,
        rendered_ids: list[int],
        block: Block | Component,
        renderable: Renderable | None = None,
    ) -> dict:
        if renderable and _id not in rendered_ids:
            return {}
        props = block.get_config() if hasattr(block, "get_config") else {}

        skip_none_deletion = []
        if (
            renderable and block.key
        ):  # Nones are important for replacing a value in a keyed component
            skip_none_deletion = [
                prop for prop, val in block.constructor_args.items() if val is None
            ]
        utils.delete_none(props, skip_props=skip_none_deletion)

        block_config = {
            "id": _id,
            "type": block.get_block_name(),
            "props": props,
            "skip_api": block.skip_api,
            "component_class_id": getattr(block, "component_class_id", None),
            "key": block.unique_key(),
        }
        if renderable:
            block_config["renderable"] = renderable._id
        if block.rendered_in is not None:
            block_config["rendered_in"] = block.rendered_in._id
        if not block.skip_api:
            block_config["api_info"] = block.api_info()  # type: ignore
            if hasattr(block, "api_info_as_input"):
                block_config["api_info_as_input"] = block.api_info_as_input()  # type: ignore
            else:
                block_config["api_info_as_input"] = block.api_info()  # type: ignore
            if hasattr(block, "api_info_as_output"):
                block_config["api_info_as_output"] = block.api_info_as_output()  # type: ignore
            else:
                block_config["api_info_as_output"] = block.api_info()  # type: ignore
            block_config["example_inputs"] = block.example_inputs()  # type: ignore

        return block_config

    def get_config(self, renderable: Renderable | None = None):
        config = {
            "page": {},
            "components": [],
            "dependencies": [],
        }

        for page, _ in self.root_block.pages:
            if page not in config["page"]:
                config["page"][page] = {
                    "layout": {"id": self.root_block._id, "children": []},
                    "components": [],
                    "dependencies": [],
                }

        rendered_ids = []

        def get_layout(block: Block) -> Layout:
            rendered_ids.append(block._id)
            if not isinstance(block, BlockContext):
                return {"id": block._id}
            children_layout = []
            for child in block.children:
                layout = get_layout(child)
                children_layout.append(layout)
            return {"id": block._id, "children": children_layout}

        if renderable:
            root_block = self.blocks[renderable.container_id]
        else:
            root_block = self.root_block
        layout = get_layout(root_block)
        config["layout"] = layout

        for root_child in layout.get("children", []):
            if isinstance(root_child, dict) and root_child["id"] in self.blocks:
                block = self.blocks[root_child["id"]]
                config["page"][block.page]["layout"]["children"].append(root_child)

        blocks_items = list(
            self.blocks.items()
        )  # freeze as list to prevent concurrent re-renders from changing the dict during loop, see https://github.com/gradio-app/gradio/issues/9991
        for _id, block in blocks_items:
            block_config = self.config_for_block(_id, rendered_ids, block, renderable)
            if not block_config:
                continue
            config["components"].append(block_config)
            config["page"][block.page]["components"].append(block._id)

        dependencies = []
        for fn in self.fns.values():
            if renderable is None or fn.rendered_in == renderable:
                dependency_config = fn.get_config()
                dependencies.append(dependency_config)
                config["page"][fn.page]["dependencies"].append(dependency_config["id"])

        config["dependencies"] = dependencies
        return config

    def __copy__(self):
        new = BlocksConfig(self.root_block)
        new.blocks = copy.copy(self.blocks)
        new.fns = copy.copy(self.fns)
        new.fn_id = self.fn_id
        return new

    def attach_load_events(self, rendered_in: Renderable | None = None):
        """Add a load event for every component whose initial value requires a function call to set."""
        for component in self.blocks.values():
            if rendered_in is not None and component.rendered_in != rendered_in:
                continue
            if (
                isinstance(component, components.Component)
                and component.load_event_to_attach
            ):
                load_fn, triggers, inputs = component.load_event_to_attach
                has_target = len(triggers) > 0
                triggers += [(self.root_block, "load")]
                # Use set_event_trigger to avoid ambiguity between load class/instance method

                dep = self.set_event_trigger(
                    [EventListenerMethod(*trigger) for trigger in triggers],
                    load_fn,
                    inputs,
                    component,
                    no_target=not has_target,
                    show_progress="hidden" if has_target else "full",
                )[0]
                component.load_event = dep.get_config()


@document("launch", "queue", "integrate", "load", "unload")
class Blocks(BlockContext, BlocksEvents, metaclass=BlocksMeta):
    """
    Blocks is Gradio's low-level API that allows you to create more custom web
    applications and demos than Interfaces (yet still entirely in Python).


    Compared to the Interface class, Blocks offers more flexibility and control over:
    (1) the layout of components (2) the events that
    trigger the execution of functions (3) data flows (e.g. inputs can trigger outputs,
    which can trigger the next level of outputs). Blocks also offers ways to group
    together related demos such as with tabs.


    The basic usage of Blocks is as follows: create a Blocks object, then use it as a
    context (with the "with" statement), and then define layouts, components, or events
    within the Blocks context. Finally, call the launch() method to launch the demo.

    Example:
        import gradio as gr
        def update(name):
            return f"Welcome to Gradio, {name}!"

        with gr.Blocks() as demo:
            gr.Markdown("Start typing below and then click **Run** to see the output.")
            with gr.Row():
                inp = gr.Textbox(placeholder="What is your name?")
                out = gr.Textbox()
            btn = gr.Button("Run")
            btn.click(fn=update, inputs=inp, outputs=out)

        demo.launch()
    Demos: blocks_hello, blocks_flipper, blocks_kinematics
    Guides: blocks-and-event-listeners, controlling-layout, state-in-blocks, custom-CSS-and-JS, using-blocks-like-functions
    """

    def __init__(
        self,
        theme: Theme | str | None = None,
        analytics_enabled: bool | None = None,
        mode: str = "blocks",
        title: str | I18nData = "Gradio",
        css: str | None = None,
        css_paths: str | Path | Sequence[str | Path] | None = None,
        js: str | Literal[True] | None = None,
        head: str | None = None,
        head_paths: str | Path | Sequence[str | Path] | None = None,
        fill_height: bool = False,
        fill_width: bool = False,
        delete_cache: tuple[int, int] | None = None,
        **kwargs,
    ):
        """
        Parameters:
            theme: A Theme object or a string representing a theme. If a string, will look for a built-in theme with that name (e.g. "soft" or "default"), or will attempt to load a theme from the Hugging Face Hub (e.g. "gradio/monochrome"). If None, will use the Default theme.
            analytics_enabled: Whether to allow basic telemetry. If None, will use GRADIO_ANALYTICS_ENABLED environment variable or default to True.
            mode: A human-friendly name for the kind of Blocks or Interface being created. Used internally for analytics.
            title: The tab title to display when this is opened in a browser window.
            css: Custom css as a code string. This css will be included in the demo webpage.
            css_paths: Custom css as a pathlib.Path to a css file or a list of such paths. This css files will be read, concatenated, and included in the demo webpage. If the `css` parameter is also set, the css from `css` will be included first.
            js: Custom js as a code string. The custom js should be in the form of a single js function. This function will automatically be executed when the page loads. For more flexibility, use the head parameter to insert js inside <script> tags.
            head: Custom html code to insert into the head of the demo webpage. This can be used to add custom meta tags, multiple scripts, stylesheets, etc. to the page.
            head_paths: Custom html code as a pathlib.Path to a html file or a list of such paths. This html files will be read, concatenated, and included in the head of the demo webpage. If the `head` parameter is also set, the html from `head` will be included first.
            fill_height: Whether to vertically expand top-level child components to the height of the window. If True, expansion occurs when the scale value of the child components >= 1.
            fill_width: Whether to horizontally expand to fill container fully. If False, centers and constrains app to a maximum width. Only applies if this is the outermost `Blocks` in your Gradio app.
            delete_cache: A tuple corresponding [frequency, age] both expressed in number of seconds. Every `frequency` seconds, the temporary files created by this Blocks instance will be deleted if more than `age` seconds have passed since the file was created. For example, setting this to (86400, 86400) will delete temporary files every day. The cache will be deleted entirely when the server restarts. If None, no cache deletion will occur.
        """
        self.limiter = None
        if theme is None:
            theme = DefaultTheme()
        elif isinstance(theme, str):
            if theme.lower() in BUILT_IN_THEMES:
                theme = BUILT_IN_THEMES[theme.lower()]
            else:
                try:
                    theme = Theme.from_hub(theme)
                except Exception as e:
                    warnings.warn(f"Cannot load {theme}. Caught Exception: {str(e)}")
                    theme = DefaultTheme()
        if not isinstance(theme, Theme):
            warnings.warn("Theme should be a class loaded from gradio.themes")
            theme = DefaultTheme()
        self.theme: Theme = theme
        self.theme_css = theme._get_theme_css()
        self.stylesheets = theme._stylesheets
        theme_hasher = hashlib.sha256()
        theme_hasher.update(self.theme_css.encode("utf-8"))
        self.theme_hash = theme_hasher.hexdigest()

        self.encrypt = False
        self.mcp_server_obj: None | GradioMCPServer = None
        self.mcp_error: None | str = None
        self.share = False
        self.enable_queue = True
        self.max_threads = 40
        self.pending_streams = defaultdict(dict)
        self.pending_diff_streams = defaultdict(dict)
        self.show_error = True
        self.fill_height = fill_height
        self.fill_width = fill_width
        self.delete_cache = delete_cache
        self.extra_startup_events: list[Callable[..., Coroutine[Any, Any, Any]]] = []
        self.css = css or ""
        css_paths = utils.none_or_singleton_to_list(css_paths)
        for css_path in css_paths or []:
            with open(css_path, encoding="utf-8") as css_file:
                self.css += "\n" + css_file.read()
        self.js = js or ""
        self.head = head or ""
        head_paths = utils.none_or_singleton_to_list(head_paths)
        for head_path in head_paths or []:
            with open(head_path, encoding="utf-8") as head_file:
                self.head += "\n" + head_file.read()
        self.renderables: list[Renderable] = []
        self.state_holder: StateHolder
        self.custom_mount_path: str | None = None
        self.pwa = False
        self.mcp_server = False

        # For analytics_enabled and allow_flagging: (1) first check for
        # parameter, (2) check for env variable, (3) default to True/"manual"
        self.analytics_enabled = (
            analytics_enabled
            if analytics_enabled is not None
            else analytics.analytics_enabled()
        )
        if self.analytics_enabled:
            if not wasm_utils.IS_WASM:
                t = threading.Thread(target=analytics.version_check)
                t.start()
        else:
            os.environ["HF_HUB_DISABLE_TELEMETRY"] = "True"
        self.enable_monitoring: bool | None = None

        self.default_config = BlocksConfig(self)
        super().__init__(render=False, **kwargs)

        self.mode = mode
        self.is_running = False
        self.local_url = None
        self.share_url = None
        self.width = None
        self.height = None
        self.api_open = utils.get_space() is None

        self.space_id = utils.get_space()
        self.favicon_path = None
        self.auth = None
        self.dev_mode = bool(os.getenv("GRADIO_WATCH_DIRS", ""))
        self.app_id = random.getrandbits(64)
        self.upload_file_set = set()
        self.temp_file_sets = [self.upload_file_set]
        self.title = title
        self.show_api = not wasm_utils.IS_WASM

        # Only used when an Interface is loaded from a config
        self.predict = None
        self.input_components = None
        self.output_components = None
        self.__name__ = None  # type: ignore
        self.api_mode = None

        self.progress_tracking = None
        self.ssl_verify = True
        self.allowed_paths = []
        self.blocked_paths = []
        self.root_path = os.environ.get("GRADIO_ROOT_PATH", "")
        self.proxy_urls = set()

        self.pages: list[tuple[str, str]] = [("", "Home")]
        self.current_page = ""

        if self.analytics_enabled:
            is_custom_theme = not any(
                self.theme.to_dict() == built_in_theme.to_dict()
                for built_in_theme in BUILT_IN_THEMES.values()
            )
            data = {
                "mode": self.mode,
                "custom_css": self.css is not None,
                "theme": self.theme.name,
                "is_custom_theme": is_custom_theme,
                "version": get_package_version(),
            }
            analytics.initiated_analytics(data)

        self.queue()

    @property
    def blocks(self) -> dict[int, Component | Block]:
        return self.default_config.blocks

    @blocks.setter
    def blocks(self, value: dict[int, Component | Block]):
        self.default_config.blocks = value

    @property
    def fns(self) -> dict[int, BlockFunction]:
        return self.default_config.fns

    def get_component(self, id: int) -> Component | BlockContext:
        comp = self.blocks[id]
        if not isinstance(comp, (components.Component, BlockContext)):
            raise TypeError(f"Block with id {id} is not a Component or BlockContext")
        return comp

    @property
    def _is_running_in_reload_thread(self):
        if wasm_utils.IS_WASM:
            # Wasm (Pyodide) doesn't support threading,
            # so the return value is always False.
            return False

        from gradio.cli.commands.reload import reload_thread

        return getattr(reload_thread, "running_reload", False)

    @classmethod
    def from_config(
        cls,
        config: BlocksConfigDict,
        fns: list[Callable],
        proxy_url: str,
    ) -> Blocks:
        """
        Factory method that creates a Blocks from a config and list of functions. Used
        internally by the gradio.external.load() method.

        Parameters:
        config: a dictionary containing the configuration of the Blocks.
        fns: a list of functions that are used in the Blocks. Must be in the same order as the dependencies in the config.
        proxy_url: an external url to use as a root URL when serving files for components in the Blocks.
        """
        config = copy.deepcopy(config)
        components_config = config["components"]
        theme = config.get("theme", "default")
        original_mapping: dict[int, Block] = {}
        proxy_urls = {proxy_url}

        def get_block_instance(id: int) -> Block:
            for block_config in components_config:
                if block_config["id"] == id:
                    break
            else:
                raise ValueError(f"Cannot find block with id {id}")
            cls = component_or_layout_class(block_config["props"]["name"])

            # If a Gradio app B is loaded into a Gradio app A, and B itself loads a
            # Gradio app C, then the proxy_urls of the components in A need to be the
            # URL of C, not B. The else clause below handles this case.
            if block_config["props"].get("proxy_url") is None:
                block_config["props"]["proxy_url"] = f"{proxy_url}/"
            postprocessed_value = block_config["props"].pop("value", None)

            constructor_args = cls.recover_kwargs(block_config["props"])
            block = cls(**constructor_args)
            if postprocessed_value is not None:
                block.value = postprocessed_value  # type: ignore

            block_proxy_url = block_config["props"]["proxy_url"]
            block.proxy_url = block_proxy_url
            proxy_urls.add(block_proxy_url)
            if (
                _selectable := block_config["props"].pop("_selectable", None)
            ) is not None:
                block._selectable = _selectable  # type: ignore

            return block

        def iterate_over_children(children_list):
            for child_config in children_list:
                id = child_config["id"]
                block = get_block_instance(id)

                original_mapping[id] = block

                children = child_config.get("children")
                if children is not None:
                    if not isinstance(block, BlockContext):
                        raise ValueError(
                            f"Invalid config, Block with id {id} has children but is not a BlockContext."
                        )
                    with block:
                        iterate_over_children(children)

        derived_fields = ["types"]

        with Blocks(theme=theme) as blocks:
            # ID 0 should be the root Blocks component
            original_mapping[0] = root_block = Context.root_block or blocks

            if "layout" in config:
                iterate_over_children(config["layout"].get("children", []))

            first_dependency = None

            # add the event triggers
            if "dependencies" not in config:
                raise ValueError(
                    "This config is missing the 'dependencies' field and cannot be loaded."
                )
            for dependency, fn in zip(config["dependencies"], fns, strict=False):
                # We used to add a "fake_event" to the config to cache examples
                # without removing it. This was causing bugs in calling gr.load
                # We fixed the issue by removing "fake_event" from the config in examples.py
                # but we still need to skip these events when loading the config to support
                # older demos
                if "trigger" in dependency and dependency["trigger"] == "fake_event":
                    continue
                for field in derived_fields:
                    dependency.pop(field, None)

                # older versions had a separate trigger field, but now it is part of the
                # targets field
                _targets = dependency.pop("targets")
                trigger = dependency.pop("trigger", None)
                is_then_event = False

                # This assumes that you cannot combine multiple .then() events in a single
                # gr.on() event, which is true for now. If this changes, we will need to
                # update this code.
                if not isinstance(_targets[0], int) and _targets[0][1] in [
                    "then",
                    "success",
                ]:
                    if len(_targets) != 1:
                        raise ValueError(
                            "This logic assumes that .then() events are not combined with other events in a single gr.on() event"
                        )
                    is_then_event = True

                dependency.pop("backend_fn")
                dependency.pop("documentation", None)
                dependency["inputs"] = [
                    original_mapping[i] for i in dependency["inputs"]
                ]
                dependency["outputs"] = [
                    original_mapping[o] for o in dependency["outputs"]
                ]
                dependency.pop("status_tracker", None)
                dependency.pop("zerogpu", None)
                dependency.pop("id", None)
                dependency.pop("rendered_in", None)
                dependency.pop("render_id", None)
                dependency.pop("every", None)
                dependency["preprocess"] = False
                dependency["postprocess"] = False
                if is_then_event:
                    targets = [EventListenerMethod(None, "then")]
                    dependency["trigger_after"] = dependency.pop("trigger_after")
                    dependency["trigger_only_on_success"] = dependency.pop(
                        "trigger_only_on_success"
                    )
                    dependency["no_target"] = True
                else:
                    targets = [
                        EventListenerMethod(
                            t.__self__ if t.has_trigger else None,
                            t.event_name,  # type: ignore
                        )
                        for t in Blocks.get_event_targets(
                            original_mapping, _targets, trigger
                        )
                    ]
                dependency = root_block.default_config.set_event_trigger(
                    targets=targets, fn=fn, **dependency
                )[0]
                if first_dependency is None:
                    first_dependency = dependency

            # Allows some use of Interface-specific methods with loaded Spaces
            if first_dependency and get_blocks_context():
                blocks.predict = [fns[0]]
                blocks.input_components = first_dependency.inputs
                blocks.output_components = first_dependency.outputs
                blocks.__name__ = "Interface"
                blocks.api_mode = True
        blocks.proxy_urls = proxy_urls
        return blocks

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        num_backend_fns = len([d for d in self.fns.values() if d.fn])
        repr = f"Gradio Blocks instance: {num_backend_fns} backend functions"
        repr += f"\n{'-' * len(repr)}"
        for d, dependency in self.fns.items():
            if dependency.fn:
                repr += f"\nfn_index={d}"
                repr += "\n inputs:"
                for block in dependency.inputs:
                    block = self.blocks[block._id]
                    repr += f"\n |-{block}"
                repr += "\n outputs:"
                for block in dependency.outputs:
                    block = self.blocks[block._id]
                    repr += f"\n |-{block}"
        return repr

    @property
    def expects_oauth(self):
        """Return whether the app expects user to authenticate via OAuth."""
        return any(
            isinstance(block, components.LoginButton) for block in self.blocks.values()
        )

    def unload(self, fn: Callable[..., Any]) -> None:
        """This listener is triggered when the user closes or refreshes the tab, ending the user session.
        It is useful for cleaning up resources when the app is closed.
        Parameters:
            fn: Callable function to run to clear resources. The function should not take any arguments and the output is not used.
        Example:
            import gradio as gr
            with gr.Blocks() as demo:
                gr.Markdown("# When you close the tab, hello will be printed to the console")
                demo.unload(lambda: print("hello"))
            demo.launch()
        """
        self.default_config.set_event_trigger(
            targets=[EventListenerMethod(None, "unload")],
            fn=fn,
            inputs=None,
            outputs=None,
            preprocess=False,
            postprocess=False,
            show_progress="hidden",
            api_name=None,
            js=None,
            no_target=True,
            batch=False,
            max_batch_size=4,
            cancels=None,
            collects_event_data=None,
            trigger_after=None,
            trigger_only_on_success=False,
            trigger_mode="once",
            concurrency_limit="default",
            concurrency_id=None,
            show_api=False,
        )

    def render(self):
        root_context = get_blocks_context()
        if root_context is not None and Context.root_block is not None:
            if self._id in root_context.blocks:
                raise DuplicateBlockError(
                    f"A block with id: {self._id} has already been rendered in the current Blocks."
                )
            overlapping_ids = set(root_context.blocks).intersection(self.blocks)
            for id in overlapping_ids:
                # State components are allowed to be reused between Blocks
                if not isinstance(self.blocks[id], components.State):
                    raise DuplicateBlockError(
                        "At least one block in this Blocks has already been rendered."
                    )

            for block in self.blocks.values():
                block.page = Context.root_block.current_page
            root_context.blocks.update(self.blocks)
            dependency_offset = max(root_context.fns.keys(), default=-1) + 1
            existing_api_names = [
                dep.api_name
                for dep in root_context.fns.values()
                if isinstance(dep.api_name, str)
            ]
            for dependency in self.fns.values():
                dependency.page = Context.root_block.current_page
                dependency._id += dependency_offset
                # Any event -- e.g. Blocks.load() -- that is triggered by this Blocks
                # should now be triggered by the root Blocks instead.
                for target in dependency.targets:
                    if target[0] == self._id:
                        target = (Context.root_block._id, target[1])
                api_name = dependency.api_name
                if isinstance(api_name, str):
                    api_name_ = utils.append_unique_suffix(
                        api_name,
                        existing_api_names,
                    )
                    if api_name != api_name_:
                        dependency.api_name = api_name_
                dependency.cancels = [c + dependency_offset for c in dependency.cancels]
                if dependency.trigger_after is not None:
                    dependency.trigger_after += dependency_offset
                # Recreate the cancel function so that it has the latest
                # dependency fn indices. This is necessary to properly cancel
                # events in the backend
                if dependency.cancels:
                    updated_cancels = [
                        root_context.fns[i].get_config() for i in dependency.cancels
                    ]
                    dependency.cancels = get_cancelled_fn_indices(updated_cancels)
                root_context.fns[dependency._id] = dependency
            root_context.fn_id = max(root_context.fns.keys(), default=-1) + 1
            Context.root_block.temp_file_sets.extend(self.temp_file_sets)
            Context.root_block.proxy_urls.update(self.proxy_urls)
            Context.root_block.extra_startup_events.extend(self.extra_startup_events)

        render_context = get_render_context()
        if render_context is not None:
            render_context.children.extend(self.children)
        return self

    def is_callable(self, fn_index: int = 0) -> bool:
        """Checks if a particular Blocks function is callable (i.e. not stateful or a generator)."""
        block_fn = self.fns[fn_index]
        dependency = self.fns[fn_index]

        if inspect.isasyncgenfunction(block_fn.fn):
            return False
        if inspect.isgeneratorfunction(block_fn.fn):
            return False
        if any(block.stateful for block in dependency.inputs):
            return False
        return not any(block.stateful for block in dependency.outputs)

    def __call__(self, *inputs, fn_index: int = 0, api_name: str | None = None):
        """
        Allows Blocks objects to be called as functions. Supply the parameters to the
        function as positional arguments. To choose which function to call, use the
        fn_index parameter, which must be a keyword argument.

        Parameters:
        *inputs: the parameters to pass to the function
        fn_index: the index of the function to call (defaults to 0, which for Interfaces, is the default prediction function)
        api_name: The api_name of the dependency to call. Will take precedence over fn_index.
        """
        if api_name is not None:
            inferred_fn_index = next(
                (i for i, d in self.fns.items() if d.api_name == api_name),
                None,
            )
            if inferred_fn_index is None:
                raise InvalidApiNameError(
                    f"Cannot find a function with api_name {api_name}"
                )
            fn_index = inferred_fn_index
        if not (self.is_callable(fn_index)):
            raise ValueError(
                "This function is not callable because it is either stateful or is a generator. Please use the .launch() method instead to create an interactive user interface."
            )

        inputs = list(inputs)
        processed_inputs = self.serialize_data(fn_index, inputs)
        fn = self.fns[fn_index]
        if fn.batch:
            processed_inputs = [[inp] for inp in processed_inputs]

        outputs = client_utils.synchronize_async(
            self.process_api,
            block_fn=fn,
            inputs=processed_inputs,
            request=None,
            state={},
            explicit_call=True,
        )
        outputs = outputs["data"]

        if fn.batch:
            outputs = [out[0] for out in outputs]

        outputs = self.deserialize_data(fn_index, outputs)
        processed_outputs = utils.resolve_singleton(outputs)

        return processed_outputs

    async def call_function(
        self,
        block_fn: BlockFunction | int,
        processed_input: list[Any],
        iterator: AsyncIterator[Any] | None = None,
        requests: Request | list[Request] | None = None,
        event_id: str | None = None,
        event_data: EventData | None = None,
        in_event_listener: bool = False,
        state: SessionState | None = None,
    ):
        """
        Calls function with given index and preprocessed input, and measures process time.
        Parameters:
            fn_index: index of function to call
            processed_input: preprocessed input to pass to function
            iterator: iterator to use if function is a generator
            requests: requests to pass to function
            event_id: id of event in queue
            event_data: data associated with event trigger
        """
        if isinstance(block_fn, int):
            block_fn = self.fns[block_fn]
        if not block_fn.fn:
            raise IndexError("function has no backend method.")
        is_generating = False
        request = requests[0] if isinstance(requests, list) else requests
        start = time.time()

        fn = utils.get_function_with_locals(
            fn=block_fn.fn,
            blocks=self,
            event_id=event_id,
            in_event_listener=in_event_listener,
            request=request,
            state=state,
        )

        if iterator is None:  # If not a generator function that has already run
            if block_fn.inputs_as_dict:
                processed_input = [
                    dict(zip(block_fn.inputs, processed_input, strict=False))
                ]

            fn_to_analyze = (
                block_fn.renderable.fn if block_fn.renderable else block_fn.fn
            )
            processed_input, progress_index, _ = special_args(
                fn_to_analyze, processed_input, request, event_data
            )
            progress_tracker = (
                processed_input[progress_index] if progress_index is not None else None
            )

            if progress_tracker is not None and progress_index is not None:
                progress_tracker, fn = create_tracker(fn, progress_tracker.track_tqdm)
                processed_input[progress_index] = progress_tracker

            if inspect.iscoroutinefunction(fn):
                prediction = await fn(*processed_input)
            else:
                prediction = await anyio.to_thread.run_sync(  # type: ignore
                    fn, *processed_input, limiter=self.limiter
                )
        else:
            prediction = None

        if inspect.isgeneratorfunction(fn) or inspect.isasyncgenfunction(fn):
            try:
                if iterator is None:
                    iterator = cast(AsyncIterator[Any], prediction)
                if inspect.isgenerator(iterator):
                    iterator = utils.SyncToAsyncIterator(iterator, self.limiter)
                prediction = await utils.async_iteration(iterator)
                is_generating = True
            except StopAsyncIteration:
                n_outputs = len(block_fn.outputs)
                prediction = (
                    components._Keywords.FINISHED_ITERATING
                    if n_outputs == 1
                    else (components._Keywords.FINISHED_ITERATING,) * n_outputs
                )
                iterator = None

        duration = time.time() - start

        return {
            "prediction": prediction,
            "duration": duration,
            "is_generating": is_generating,
            "iterator": iterator,
        }

    def serialize_data(self, fn_index: int, inputs: list[Any]) -> list[Any]:
        dependency = self.fns[fn_index]
        processed_input = []

        def format_file(s):
            return FileData(path=s).model_dump()

        for i, block in enumerate(dependency.inputs):
            if not isinstance(block, components.Component):
                raise InvalidComponentError(
                    f"{block.__class__} Component not a valid input component."
                )
            api_info = block.api_info()
            if client_utils.value_is_file(api_info):
                serialized_input = client_utils.traverse(
                    inputs[i],
                    format_file,
                    lambda s: client_utils.is_filepath(s)
                    or client_utils.is_http_url_like(s),
                )
            else:
                serialized_input = inputs[i]
            processed_input.append(serialized_input)

        return processed_input

    def deserialize_data(self, fn_index: int, outputs: list[Any]) -> list[Any]:
        dependency = self.fns[fn_index]
        predictions = []

        for o, block in enumerate(dependency.outputs):
            if not isinstance(block, components.Component):
                raise InvalidComponentError(
                    f"{block.__class__} Component not a valid output component."
                )

            deserialized = client_utils.traverse(
                outputs[o], lambda s: s["path"], client_utils.is_file_obj
            )
            predictions.append(deserialized)

        return predictions

    def validate_inputs(self, block_fn: BlockFunction, inputs: list[Any]):
        dep_inputs = block_fn.inputs

        # This handles incorrect inputs when args are changed by a JS function
        # Only check not enough args case, ignore extra arguments (for now)
        # TODO: make this stricter?
        if len(inputs) < len(dep_inputs):
            name = (
                f" ({block_fn.name})"
                if block_fn.name and block_fn.name != "<lambda>"
                else ""
            )

            wanted_args = []
            received_args = []
            for block in dep_inputs:
                wanted_args.append(str(block))
            for inp in inputs:
                v = f'"{inp}"' if isinstance(inp, str) else str(inp)
                received_args.append(v)

            wanted = ", ".join(wanted_args)
            received = ", ".join(received_args)

            # JS func didn't pass enough arguments
            raise ValueError(
                f"""An event handler{name} didn't receive enough input values (needed: {len(dep_inputs)}, got: {len(inputs)}).
Check if the event handler calls a Javascript function, and make sure its return value is correct.
Wanted inputs:
    [{wanted}]
Received inputs:
    [{received}]"""
            )

    async def preprocess_data(
        self,
        block_fn: BlockFunction,
        inputs: list[Any],
        state: SessionState | None,
        explicit_call: bool = False,
    ):
        state = state or SessionState(self)

        self.validate_inputs(block_fn, inputs)

        processed_input = []
        for i, block in enumerate(block_fn.inputs):
            if not isinstance(block, components.Component):
                raise InvalidComponentError(
                    f"{block.__class__} Component not a valid input component."
                )
            if block.stateful:
                processed_input.append(state[block._id])
            else:
                if block._id in state:
                    block = state[block._id]
                inputs_cached = await processing_utils.async_move_files_to_cache(
                    inputs[i],
                    block,
                    check_in_upload_folder=not explicit_call,
                )
                if getattr(block, "data_model", None) and inputs_cached is not None:
                    data_model = cast(
                        Union[GradioModel, GradioRootModel], block.data_model
                    )
                    inputs_cached = data_model.model_validate(
                        inputs_cached, context={"validate_meta": True}
                    )
                if isinstance(inputs_cached, (GradioModel, GradioRootModel)):
                    inputs_serialized = inputs_cached.model_dump()
                else:
                    inputs_serialized = inputs_cached
                if block._id not in state:
                    state[block._id] = block
                state._update_value_in_config(block._id, inputs_serialized)
                if block_fn.preprocess:
                    processed_input.append(block.preprocess(inputs_cached))
                else:
                    processed_input.append(inputs_serialized)
        return processed_input

    def validate_outputs(self, block_fn: BlockFunction, predictions: Any | list[Any]):
        dep_outputs = block_fn.outputs

        if not isinstance(predictions, (list, tuple)):
            predictions = [predictions]

        if len(predictions) != len(dep_outputs):
            name = (
                f" ({block_fn.name})"
                if block_fn.name and block_fn.name != "<lambda>"
                else ""
            )

            wanted_args = []
            received_args = []
            for block in dep_outputs:
                wanted_args.append(str(block.get_block_class()))
            for pred in predictions:
                v = f'"{pred}"' if isinstance(pred, str) else str(pred)
                received_args.append(v)

            wanted = ", ".join(wanted_args)
            received = ", ".join(received_args)

            if len(predictions) < len(dep_outputs):
                raise ValueError(
                    f"""A  function{name} didn't return enough output values (needed: {len(dep_outputs)}, returned: {len(predictions)}).
    Output components:
        [{wanted}]
    Output values returned:
        [{received}]"""
                )
            else:
                if len(predictions) == 1 and predictions[0] is None:
                    # do not throw error if the function did not return anything
                    # https://github.com/gradio-app/gradio/issues/9742
                    return
                warnings.warn(
                    f"""A function{name} returned too many output values (needed: {len(dep_outputs)}, returned: {len(predictions)}). Ignoring extra values.
    Output components:
        [{wanted}]
    Output values returned:
        [{received}]"""
                )

    async def postprocess_data(
        self,
        block_fn: BlockFunction,
        predictions: list | dict,
        state: SessionState | None,
    ) -> list[Any]:
        state = state or SessionState(self)
        if (
            isinstance(predictions, dict)
            and predictions == skip()
            and len(block_fn.outputs) > 1
        ):
            # For developer convenience, if a function returns a single skip() with multiple outputs,
            # we will skip updating all outputs.
            predictions = [skip()] * len(block_fn.outputs)
        if isinstance(predictions, dict) and len(predictions) > 0:
            predictions = convert_component_dict_to_list(
                [block._id for block in block_fn.outputs], predictions
            )

        if len(block_fn.outputs) == 1 and not block_fn.batch:
            predictions = [
                predictions,
            ]

        self.validate_outputs(block_fn, predictions)  # type: ignore

        output = []
        for i, block in enumerate(block_fn.outputs):
            try:
                if predictions[i] is components._Keywords.FINISHED_ITERATING:
                    output.append(None)
                    continue
            except (IndexError, KeyError) as err:
                raise ValueError(
                    "Number of output components does not match number "
                    f"of values returned from from function {block_fn.name}"
                ) from err

            if block.stateful:
                if not utils.is_prop_update(predictions[i]):
                    state[block._id] = predictions[i]
                output.append(None)
            else:
                prediction_value = predictions[i]
                if utils.is_prop_update(
                    prediction_value
                ):  # if update is passed directly (deprecated), remove Nones
                    prediction_value = utils.delete_none(
                        prediction_value, skip_value=True
                    )

                if isinstance(prediction_value, Block):
                    prediction_value = prediction_value.constructor_args.copy()
                    prediction_value["__type__"] = "update"
                if utils.is_prop_update(prediction_value):
                    kwargs = state[block._id].constructor_args.copy()
                    kwargs.update(prediction_value)
                    kwargs.pop("value", None)
                    kwargs.pop("__type__")
                    kwargs["render"] = False

                    state[block._id] = block.__class__(**kwargs)
                    state._update_config(block._id)
                    prediction_value = postprocess_update_dict(
                        block=state[block._id],
                        update_dict=prediction_value,
                        postprocess=block_fn.postprocess,
                    )
                    if "value" in prediction_value:
                        state._update_value_in_config(
                            block._id, prediction_value.get("value")
                        )
                elif block_fn.postprocess:
                    if not isinstance(block, components.Component):
                        raise InvalidComponentError(
                            f"{block.__class__} Component not a valid output component."
                        )
                    if block._id in state:
                        block = state[block._id]
                    prediction_value = block.postprocess(prediction_value)
                    if isinstance(prediction_value, (GradioModel, GradioRootModel)):
                        prediction_value_serialized = prediction_value.model_dump()
                    else:
                        prediction_value_serialized = prediction_value
                    prediction_value_serialized = (
                        await processing_utils.async_move_files_to_cache(
                            prediction_value_serialized,
                            block,
                            postprocess=True,
                        )
                    )
                    if block._id not in state:
                        state[block._id] = block
                    state._update_value_in_config(
                        block._id, prediction_value_serialized
                    )

                outputs_cached = await processing_utils.async_move_files_to_cache(
                    prediction_value,
                    block,
                    postprocess=True,
                )
                output.append(outputs_cached)

        return output

    async def handle_streaming_outputs(
        self,
        block_fn: BlockFunction,
        data: list,
        session_hash: str | None,
        run: int | None,
        root_path: str | None = None,
        final: bool = False,
    ) -> list:
        if session_hash is None or run is None:
            return data
        if run not in self.pending_streams[session_hash]:
            self.pending_streams[session_hash][run] = {}
        stream_run: dict[int, MediaStream] = self.pending_streams[session_hash][run]

        for i, block in enumerate(block_fn.outputs):
            output_id = block._id
            if (
                isinstance(block, components.StreamingOutput)
                and block.streaming
                and not utils.is_prop_update(data[i])
            ):
                if final:
                    stream_run[output_id].end_stream()
                first_chunk = output_id not in stream_run
                binary_data, output_data = await block.stream_output(
                    data[i],
                    f"{session_hash}/{run}/{output_id}/playlist.m3u8",
                    first_chunk,
                )
                if first_chunk:
                    desired_output_format = None
                    if orig_name := output_data.get("orig_name"):
                        desired_output_format = Path(orig_name).suffix[1:]
                    stream_run[output_id] = MediaStream(
                        desired_output_format=desired_output_format
                    )
                    stream_run[output_id]

                await stream_run[output_id].add_segment(binary_data)
                output_data = await processing_utils.async_move_files_to_cache(
                    output_data,
                    block,
                    postprocess=True,
                )
                if root_path is not None:
                    output_data = processing_utils.add_root_url(
                        output_data, root_path, None
                    )
                data[i] = output_data

        return data

    def handle_streaming_diffs(
        self,
        block_fn: BlockFunction,
        data: list,
        session_hash: str | None,
        run: int | None,
        final: bool,
        simple_format: bool = False,
    ) -> list:
        if session_hash is None or run is None:
            return data
        first_run = run not in self.pending_diff_streams[session_hash]
        if first_run:
            self.pending_diff_streams[session_hash][run] = [None] * len(data)
        last_diffs = self.pending_diff_streams[session_hash][run]

        for i in range(len(block_fn.outputs)):
            if final:
                data[i] = last_diffs[i]
                continue

            if first_run:
                last_diffs[i] = data[i]
            else:
                prev_chunk = last_diffs[i]
                last_diffs[i] = data[i]
                if not simple_format:
                    data[i] = utils.diff(prev_chunk, data[i])

        if final:
            del self.pending_diff_streams[session_hash][run]

        return data

    async def process_api(
        self,
        block_fn: BlockFunction | int,
        inputs: list[Any],
        state: SessionState | None = None,
        request: Request | list[Request] | None = None,
        iterator: AsyncIterator | None = None,
        session_hash: str | None = None,
        event_id: str | None = None,
        event_data: EventData | None = None,
        in_event_listener: bool = True,
        simple_format: bool = False,
        explicit_call: bool = False,
        root_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Processes API calls from the frontend. First preprocesses the data,
        then runs the relevant function, then postprocesses the output.

        Parameters:
            fn_index: Index of function to run.
            inputs: input data received from the frontend
            state: data stored from stateful components for session (key is input block id)
            request: the gr.Request object containing information about the network request (e.g. IP address, headers, query parameters, username)
            iterators: the in-progress iterators for each generator function (key is function index)
            event_id: id of event that triggered this API call
            event_data: data associated with the event trigger itself
            in_event_listener: whether this API call is being made in response to an event listener
            explicit_call: whether this call is being made directly by calling the Blocks function, instead of through an event listener or API route
            root_path: if provided, the root path of the server. All file URLs will be prefixed with this path.

        Returns a dictionary with the following keys:
            - "data": the output data from the function
            - "is_generating": whether the function is generating output
            - "iterator": the iterator for the function
            - "duration": the duration of the function call
            - "average_duration": the average duration of the function call
            - "render_config": the render config for the function
        """
        if isinstance(block_fn, int):
            block_fn = self.fns[block_fn]
        batch = block_fn.batch
        state_ids_to_track, hashed_values = self.get_state_ids_to_track(block_fn, state)
        changed_state_ids = []
        LocalContext.blocks.set(self)

        if batch:
            max_batch_size = block_fn.max_batch_size
            batch_sizes = [len(inp) for inp in inputs]
            batch_size = batch_sizes[0]
            if inspect.isasyncgenfunction(block_fn.fn) or inspect.isgeneratorfunction(
                block_fn.fn
            ):
                raise ValueError("Gradio does not support generators in batch mode.")
            if not all(x == batch_size for x in batch_sizes):
                raise ValueError(
                    f"All inputs to a batch function must have the same length but instead have sizes: {batch_sizes}."
                )
            if batch_size > max_batch_size:
                raise ValueError(
                    f"Batch size ({batch_size}) exceeds the max_batch_size for this function ({max_batch_size})"
                )
            inputs = [
                await self.preprocess_data(block_fn, list(i), state, explicit_call)
                for i in zip(*inputs, strict=False)
            ]
            result = await self.call_function(
                block_fn,
                list(zip(*inputs, strict=False)),
                None,
                request,
                event_id,
                event_data,
                in_event_listener,
                state,
            )
            preds = result["prediction"]
            data = [
                await self.postprocess_data(block_fn, list(o), state)
                for o in zip(*preds, strict=False)
            ]
            if root_path is not None:
                data = processing_utils.add_root_url(data, root_path, None)  # type: ignore
            data = list(zip(*data, strict=False))
            is_generating, iterator = None, None
        else:
            old_iterator = iterator
            if old_iterator:
                inputs = []
            else:
                inputs = await self.preprocess_data(
                    block_fn, inputs, state, explicit_call
                )
            was_generating = old_iterator is not None
            result = await self.call_function(
                block_fn,
                inputs,
                old_iterator,
                request,
                event_id,
                event_data,
                in_event_listener,
                state,
            )
            data = await self.postprocess_data(block_fn, result["prediction"], state)
            if state:
                changed_state_ids = [
                    state_id
                    for hash_value, state_id in zip(
                        hashed_values, state_ids_to_track, strict=False
                    )
                    if hash_value != utils.deep_hash(state[state_id])
                ]

            if root_path is not None:
                data = processing_utils.add_root_url(data, root_path, None)
            is_generating, iterator = result["is_generating"], result["iterator"]
            if is_generating or was_generating:
                run = id(old_iterator) if was_generating else id(iterator)
                data = await self.handle_streaming_outputs(
                    block_fn,
                    data,
                    session_hash=session_hash,
                    run=run,
                    root_path=root_path,
                    final=not is_generating,
                )
                data = self.handle_streaming_diffs(
                    block_fn,
                    data,
                    session_hash=session_hash,
                    run=run,
                    final=not is_generating,
                    simple_format=simple_format,
                )

        block_fn.total_runtime += result["duration"]
        block_fn.total_runs += 1
        output = {
            "data": data,
            "is_generating": is_generating,
            "iterator": iterator,
            "duration": result["duration"],
            "average_duration": block_fn.total_runtime / block_fn.total_runs,
            "render_config": None,
            "changed_state_ids": changed_state_ids,
        }
        if block_fn.renderable and state:
            output["render_config"] = state.blocks_config.get_config(
                block_fn.renderable
            )
            output["render_config"]["render_id"] = block_fn.renderable._id
            if root_path is not None:
                output["render_config"] = processing_utils.add_root_url(
                    output["render_config"], root_path, None
                )

        return output

    def get_state_ids_to_track(
        self, block_fn: BlockFunction, state: SessionState | None
    ) -> tuple[list[int], list]:
        if state is None:
            return [], []
        state_ids_to_track = []
        hashed_values = []
        for block in block_fn.outputs:
            if block.stateful and any(
                (block._id, "change") in fn.targets
                for fn in state.blocks_config.fns.values()
            ):
                value = state[block._id]
                state_ids_to_track.append(block._id)
                hashed_values.append(utils.deep_hash(value))
        return state_ids_to_track, hashed_values

    def create_limiter(self):
        self.limiter = (
            None
            if self.max_threads == 40
            else CapacityLimiter(total_tokens=self.max_threads)
        )

    def get_config(self):
        return {"type": "column"}

    def get_config_file(self) -> BlocksConfigDict:
        config: BlocksConfigDict = {
            "version": VERSION,
            "api_prefix": API_PREFIX,
            "mode": self.mode,
            "app_id": self.app_id,
            "dev_mode": self.dev_mode,
            "analytics_enabled": self.analytics_enabled,
            "components": [],
            "css": self.css,
            "connect_heartbeat": False,
            "js": cast(str | Literal[True] | None, self.js),
            "head": self.head,
            "title": self.title or "Gradio",
            "space_id": self.space_id,
            "enable_queue": True,  # launch attributes
            "show_error": getattr(self, "show_error", False),
            "show_api": self.show_api,
            "is_colab": utils.colab_check(),
            "max_file_size": getattr(self, "max_file_size", None),
            "stylesheets": self.stylesheets,
            "theme": self.theme.name,
            "protocol": "sse_v3",
            "body_css": {
                "body_background_fill": self.theme._get_computed_value(
                    "body_background_fill"
                ),
                "body_text_color": self.theme._get_computed_value("body_text_color"),
                "body_background_fill_dark": self.theme._get_computed_value(
                    "body_background_fill_dark"
                ),
                "body_text_color_dark": self.theme._get_computed_value(
                    "body_text_color_dark"
                ),
            },
            "fill_height": self.fill_height,
            "fill_width": self.fill_width,
            "theme_hash": self.theme_hash,
            "pwa": self.pwa,
            "pages": self.pages,
            "page": {},
            "mcp_server": self.mcp_server,
            "i18n_translations": (
                getattr(self.i18n_instance, "translations_dict", None)
                if getattr(self, "i18n_instance", None) is not None
                else None
            ),
        }
        config.update(self.default_config.get_config())  # type: ignore
        config["connect_heartbeat"] = utils.connect_heartbeat(
            config, self.blocks.values()
        )
        return config

    def transpile_to_js(self, quiet: bool = False):
        fns_to_transpile = [
            fn.fn for fn in self.fns.values() if fn.fn and fn.js is True
        ]
        num_to_transpile = len(fns_to_transpile)
        if not quiet and num_to_transpile > 0:
            print("********************************************")
            print("* Trying to transpile functions from Python -> JS for performance\n")
        for index, fn in enumerate(fns_to_transpile):
            if not quiet:
                print(f"* ({index + 1}/{num_to_transpile}) {fn.__name__}: ", end="")
            if getattr(fn, "__js_implementation__", None) is None:  # type: ignore
                try:
                    fn.__js_implementation__ = transpile(fn, validate=True)  # type: ignore
                    if not quiet:
                        print("✅")
                except Exception as e:
                    if not quiet:
                        print("❌", e, end="\n\n")
            elif not quiet:
                print("✅")
        if not quiet and num_to_transpile > 0:
            print("********************************************\n")

    def __enter__(self):
        render_context = get_render_context()
        if render_context is None:
            Context.root_block = self
        self.parent = render_context
        set_render_context(self)
        self.exited = False
        return self

    def __exit__(self, exc_type: type[BaseException] | None = None, *args):
        if exc_type is not None:
            set_render_context(None)
            Context.root_block = None
            return
        super().fill_expected_parents()
        set_render_context(self.parent)
        # Configure the load events before root_block is reset
        self.default_config.attach_load_events()
        if self.parent is None:
            Context.root_block = None
        else:
            self.parent.children.extend(self.children)
        self.config = self.get_config_file()
        self.app = App.create_app(self)
        self.progress_tracking = any(
            block_fn.tracks_progress for block_fn in self.fns.values()
        )
        self.page = ""
        self.exited = True

    def clear(self):
        """Resets the layout of the Blocks object."""
        self.default_config.blocks = {}
        self.default_config.fns = {}
        self.children = []
        return self

    @document()
    def queue(
        self,
        status_update_rate: float | Literal["auto"] = "auto",
        api_open: bool | None = None,
        max_size: int | None = None,
        *,
        default_concurrency_limit: int | None | Literal["not_set"] = "not_set",
    ):
        """
        By enabling the queue you can control when users know their position in the queue, and set a limit on maximum number of events allowed.
        Parameters:
            status_update_rate: If "auto", Queue will send status estimations to all clients whenever a job is finished. Otherwise Queue will send status at regular intervals set by this parameter as the number of seconds.
            api_open: If True, the REST routes of the backend will be open, allowing requests made directly to those endpoints to skip the queue.
            max_size: The maximum number of events the queue will store at any given moment. If the queue is full, new events will not be added and a user will receive a message saying that the queue is full. If None, the queue size will be unlimited.
            default_concurrency_limit: The default value of `concurrency_limit` to use for event listeners that don't specify a value. Can be set by environment variable GRADIO_DEFAULT_CONCURRENCY_LIMIT. Defaults to 1 if not set otherwise.
        Example: (Blocks)
            with gr.Blocks() as demo:
                button = gr.Button(label="Generate Image")
                button.click(fn=image_generator, inputs=gr.Textbox(), outputs=gr.Image())
            demo.queue(max_size=10)
            demo.launch()
        Example: (Interface)
            demo = gr.Interface(image_generator, gr.Textbox(), gr.Image())
            demo.queue(max_size=20)
            demo.launch()
        """
        if api_open is not None:
            self.api_open = api_open
        if utils.is_zero_gpu_space():
            max_size = 1 if max_size is None else max_size
        self._queue = queueing.Queue(
            live_updates=status_update_rate == "auto",
            concurrency_count=self.max_threads,
            update_intervals=status_update_rate if status_update_rate != "auto" else 1,
            max_size=max_size,
            blocks=self,
            default_concurrency_limit=default_concurrency_limit,
        )
        self.app = App.create_app(self)
        return self

    def validate_queue_settings(self):
        for dep in self.fns.values():
            for i in dep.cancels:
                if not self.fns[i].queue:
                    raise ValueError(
                        "Queue needs to be enabled! "
                        "You may get this error by either 1) passing a function that uses the yield keyword "
                        "into an interface without enabling the queue or 2) defining an event that cancels "
                        "another event without enabling the queue. Both can be solved by calling .queue() "
                        "before .launch()"
                    )
            if dep.batch and dep.queue is False:
                raise ValueError("In order to use batching, the queue must be enabled.")

    def launch(
        self,
        inline: bool | None = None,
        inbrowser: bool = False,
        share: bool | None = None,
        debug: bool = False,
        max_threads: int = 40,
        auth: (
            Callable[[str, str], bool] | tuple[str, str] | list[tuple[str, str]] | None
        ) = None,
        auth_message: str | None = None,
        prevent_thread_lock: bool = False,
        show_error: bool = False,
        server_name: str | None = None,
        server_port: int | None = None,
        *,
        height: int = 500,
        width: int | str = "100%",
        favicon_path: str | Path | None = None,
        ssl_keyfile: str | None = None,
        ssl_certfile: str | None = None,
        ssl_keyfile_password: str | None = None,
        ssl_verify: bool = True,
        quiet: bool = False,
        show_api: bool = not wasm_utils.IS_WASM,
        allowed_paths: list[str] | None = None,
        blocked_paths: list[str] | None = None,
        root_path: str | None = None,
        app_kwargs: dict[str, Any] | None = None,
        state_session_capacity: int = 10000,
        share_server_address: str | None = None,
        share_server_protocol: Literal["http", "https"] | None = None,
        share_server_tls_certificate: str | None = None,
        auth_dependency: Callable[[fastapi.Request], str | None] | None = None,
        max_file_size: str | int | None = None,
        enable_monitoring: bool | None = None,
        strict_cors: bool = True,
        node_server_name: str | None = None,
        node_port: int | None = None,
        ssr_mode: bool | None = None,
        pwa: bool | None = None,
        mcp_server: bool | None = None,
        _frontend: bool = True,
        i18n: I18n | None = None,
    ) -> tuple[App, str, str]:
        """
        Launches a simple web server that serves the demo. Can also be used to create a
        public link used by anyone to access the demo from their browser by setting share=True.
        Parameters:
            inline: whether to display in the gradio app inline in an iframe. Defaults to True in python notebooks; False otherwise.
            inbrowser: whether to automatically launch the gradio app in a new tab on the default browser.
            share: whether to create a publicly shareable link for the gradio app. Creates an SSH tunnel to make your UI accessible from anywhere. If not provided, it is set to False by default every time, except when running in Google Colab. When localhost is not accessible (e.g. Google Colab), setting share=False is not supported. Can be set by environment variable GRADIO_SHARE=True.
            debug: if True, blocks the main thread from running. If running in Google Colab, this is needed to print the errors in the cell output.
            auth: If provided, username and password (or list of username-password tuples) required to access app. Can also provide function that takes username and password and returns True if valid login.
            auth_message: If provided, HTML message provided on login page.
            prevent_thread_lock: By default, the gradio app blocks the main thread while the server is running. If set to True, the gradio app will not block and the gradio server will terminate as soon as the script finishes.
            show_error: If True, any errors in the gradio app will be displayed in an alert modal and printed in the browser console log. They will also be displayed in the alert modal of downstream apps that gr.load() this app.
            server_port: will start gradio app on this port (if available). Can be set by environment variable GRADIO_SERVER_PORT. If None, will search for an available port starting at 7860.
            server_name: to make app accessible on local network, set this to "0.0.0.0". Can be set by environment variable GRADIO_SERVER_NAME. If None, will use "127.0.0.1".
            max_threads: the maximum number of total threads that the Gradio app can generate in parallel. The default is inherited from the starlette library (currently 40).
            width: The width in pixels of the iframe element containing the gradio app (used if inline=True)
            height: The height in pixels of the iframe element containing the gradio app (used if inline=True)
            favicon_path: If a path to a file (.png, .gif, or .ico) is provided, it will be used as the favicon for the web page.
            ssl_keyfile: If a path to a file is provided, will use this as the private key file to create a local server running on https.
            ssl_certfile: If a path to a file is provided, will use this as the signed certificate for https. Needs to be provided if ssl_keyfile is provided.
            ssl_keyfile_password: If a password is provided, will use this with the ssl certificate for https.
            ssl_verify: If False, skips certificate validation which allows self-signed certificates to be used.
            quiet: If True, suppresses most print statements.
            show_api: If True, shows the api docs in the footer of the app. Default True.
            allowed_paths: List of complete filepaths or parent directories that gradio is allowed to serve. Must be absolute paths. Warning: if you provide directories, any files in these directories or their subdirectories are accessible to all users of your app. Can be set by comma separated environment variable GRADIO_ALLOWED_PATHS. These files are generally assumed to be secure and will be displayed in the browser when possible.
            blocked_paths: List of complete filepaths or parent directories that gradio is not allowed to serve (i.e. users of your app are not allowed to access). Must be absolute paths. Warning: takes precedence over `allowed_paths` and all other directories exposed by Gradio by default. Can be set by comma separated environment variable GRADIO_BLOCKED_PATHS.
            root_path: The root path (or "mount point") of the application, if it's not served from the root ("/") of the domain. Often used when the application is behind a reverse proxy that forwards requests to the application. For example, if the application is served at "https://example.com/myapp", the `root_path` should be set to "/myapp". A full URL beginning with http:// or https:// can be provided, which will be used as the root path in its entirety. Can be set by environment variable GRADIO_ROOT_PATH. Defaults to "".
            app_kwargs: Additional keyword arguments to pass to the underlying FastAPI app as a dictionary of parameter keys and argument values. For example, `{"docs_url": "/docs"}`
            state_session_capacity: The maximum number of sessions whose information to store in memory. If the number of sessions exceeds this number, the oldest sessions will be removed. Reduce capacity to reduce memory usage when using gradio.State or returning updated components from functions. Defaults to 10000.
            share_server_address: Use this to specify a custom FRP server and port for sharing Gradio apps (only applies if share=True). If not provided, will use the default FRP server at https://gradio.live. See https://github.com/huggingface/frp for more information.
            share_server_protocol: Use this to specify the protocol to use for the share links. Defaults to "https", unless a custom share_server_address is provided, in which case it defaults to "http". If you are using a custom share_server_address and want to use https, you must set this to "https".
            share_server_tls_certificate: The path to a TLS certificate file to use when connecting to a custom share server. This parameter is not used with the default FRP server at https://gradio.live. Otherwise, you must provide a valid TLS certificate file (e.g. a "cert.pem") relative to the current working directory, or the connection will not use TLS encryption, which is insecure.
            auth_dependency: A function that takes a FastAPI request and returns a string user ID or None. If the function returns None for a specific request, that user is not authorized to access the app (they will see a 401 Unauthorized response). To be used with external authentication systems like OAuth. Cannot be used with `auth`.
            max_file_size: The maximum file size in bytes that can be uploaded. Can be a string of the form "<value><unit>", where value is any positive integer and unit is one of "b", "kb", "mb", "gb", "tb". If None, no limit is set.
            enable_monitoring: Enables traffic monitoring of the app through the /monitoring endpoint. By default is None, which enables this endpoint. If explicitly True, will also print the monitoring URL to the console. If False, will disable monitoring altogether.
            strict_cors: If True, prevents external domains from making requests to a Gradio server running on localhost. If False, allows requests to localhost that originate from localhost but also, crucially, from "null". This parameter should normally be True to prevent CSRF attacks but may need to be False when embedding a *locally-running Gradio app* using web components.
            ssr_mode: If True, the Gradio app will be rendered using server-side rendering mode, which is typically more performant and provides better SEO, but this requires Node 20+ to be installed on the system. If False, the app will be rendered using client-side rendering mode. If None, will use GRADIO_SSR_MODE environment variable or default to False.
            pwa: If True, the Gradio app will be set up as an installable PWA (Progressive Web App). If set to None (default behavior), then the PWA feature will be enabled if this Gradio app is launched on Spaces, but not otherwise.
            i18n: An I18n instance containing custom translations, which are used to translate strings in our components (e.g. the labels of components or Markdown strings). This feature can only be used to translate static text in the frontend, not values in the backend.
            mcp_server: If True, the Gradio app will be set up as an MCP server and documented functions will be added as MCP tools. If None (default behavior), then the GRADIO_MCP_SERVER environment variable will be used to determine if the MCP server should be enabled (which is "True" on Hugging Face Spaces).
        Returns:
            app: FastAPI app object that is running the demo
            local_url: Locally accessible link to the demo
            share_url: Publicly accessible link to the demo (if share=True, otherwise None)
        Example: (Blocks)
            import gradio as gr
            def reverse(text):
                return text[::-1]
            with gr.Blocks() as demo:
                button = gr.Button(value="Reverse")
                button.click(reverse, gr.Textbox(), gr.Textbox())
            demo.launch(share=True, auth=("username", "password"))
        Example:  (Interface)
            import gradio as gr
            def reverse(text):
                return text[::-1]
            demo = gr.Interface(reverse, "text", "text")
            demo.launch(share=True, auth=("username", "password"))
        """
        from gradio.routes import App

        if self._is_running_in_reload_thread:
            # We have already launched the demo
            return None, None, None  # type: ignore

        if not self.exited:
            self.__exit__()

        if auth is not None and auth_dependency is not None:
            raise ValueError(
                "You cannot provide both `auth` and `auth_dependency` in launch(). Please choose one."
            )
        if (
            auth
            and not callable(auth)
            and not isinstance(auth[0], tuple)
            and not isinstance(auth[0], list)
        ):
            self.auth = [auth]
        else:
            self.auth = auth

        if self.auth and not callable(self.auth):
            if any(not authenticable[0] for authenticable in self.auth):
                warnings.warn(
                    "You have provided an empty username in `auth`. Please provide a valid username."
                )
            if any(not authenticable[1] for authenticable in self.auth):
                warnings.warn(
                    "You have provided an empty password in `auth`. Please provide a valid password."
                )

        self.auth_message = auth_message
        self.show_error = show_error
        self.height = height
        self.width = width
        self.favicon_path = favicon_path
        self.ssl_verify = ssl_verify
        self.state_session_capacity = state_session_capacity
        if root_path is None:
            self.root_path = os.environ.get("GRADIO_ROOT_PATH", "")
        else:
            self.root_path = root_path
        self.show_api = show_api

        if allowed_paths:
            self.allowed_paths = allowed_paths
        else:
            allowed_paths_env = os.environ.get("GRADIO_ALLOWED_PATHS", "")
            if len(allowed_paths_env) > 0:
                self.allowed_paths = [
                    item.strip() for item in allowed_paths_env.split(",")
                ]
            else:
                self.allowed_paths = []

        if blocked_paths:
            self.blocked_paths = blocked_paths
        else:
            blocked_paths_env = os.environ.get("GRADIO_BLOCKED_PATHS", "")
            if len(blocked_paths_env) > 0:
                self.blocked_paths = [
                    item.strip() for item in blocked_paths_env.split(",")
                ]
            else:
                self.blocked_paths = []

        if not isinstance(self.allowed_paths, list):
            raise ValueError("`allowed_paths` must be a list of directories.")
        if not isinstance(self.blocked_paths, list):
            raise ValueError("`blocked_paths` must be a list of directories.")

        self.validate_queue_settings()
        self.max_file_size = utils._parse_file_size(max_file_size)

        if self.dev_mode:
            for block in self.blocks.values():
                if block.key is None:
                    block.key = f"__{block._id}__"

        self.pwa = utils.get_space() is not None if pwa is None else pwa
        self.max_threads = max_threads
        self._queue.max_thread_count = max_threads
        self.transpile_to_js(quiet=quiet)

        self.ssr_mode = (
            False
            if wasm_utils.IS_WASM
            else (
                ssr_mode
                if ssr_mode is not None
                else os.getenv("GRADIO_SSR_MODE", "False").lower() == "true"
            )
        )
        if self.ssr_mode:
            self.node_path = os.environ.get(
                "GRADIO_NODE_PATH", "" if wasm_utils.IS_WASM else get_node_path()
            )
            self.node_server_name, self.node_process, self.node_port = (
                start_node_server(
                    server_name=node_server_name,
                    server_port=node_port,
                    node_path=self.node_path,
                )
            )
        else:
            self.node_server_name = self.node_port = self.node_process = None

        self.i18n_instance = i18n

        if app_kwargs is None:
            app_kwargs = {}

        self.server_app = self.app = App.create_app(
            self,
            auth_dependency=auth_dependency,
            app_kwargs=app_kwargs,
            strict_cors=strict_cors,
            ssr_mode=self.ssr_mode,
            mcp_server=mcp_server,
        )
        if self.mcp_server and not quiet:
            print(self.mcp_error)

        self.config = self.get_config_file()

        if self.is_running:
            if not isinstance(self.local_url, str):
                raise ValueError(f"Invalid local_url: {self.local_url}")
            if not (quiet):
                print(
                    "Rerunning server... use `close()` to stop if you need to change `launch()` parameters.\n----"
                )
        else:
            if wasm_utils.IS_WASM:
                server_name = "xxx"
                server_port = 99999
                local_url = ""
                server = None
                # In the Wasm environment, we only need the app object
                # which the frontend app will directly communicate with through the Worker API,
                # and we don't need to start a server.
                wasm_utils.register_app(self.app)
            else:
                from gradio import http_server

                (
                    server_name,
                    server_port,
                    local_url,
                    server,
                ) = http_server.start_server(
                    app=self.app,
                    server_name=server_name,
                    server_port=server_port,
                    ssl_keyfile=ssl_keyfile,
                    ssl_certfile=ssl_certfile,
                    ssl_keyfile_password=ssl_keyfile_password,
                )
            self.server_name = server_name
            self.local_url = local_url
            self.local_api_url = f"{self.local_url.rstrip('/')}{API_PREFIX}/"
            self.server_port = server_port
            self.server = server
            self.is_running = True
            self.is_colab = utils.colab_check()
            self.is_hosted_notebook = utils.is_hosted_notebook()
            self.share_server_address = share_server_address
            self.share_server_protocol = share_server_protocol or (
                "http" if share_server_address is not None else "https"
            )
            self.share_server_tls_certificate = share_server_tls_certificate
            self.has_launched = True

            self.protocol = (
                "https"
                if self.local_url.startswith("https") or self.is_colab
                else "http"
            )
            if not wasm_utils.IS_WASM and not self.is_colab and not quiet:
                s = (
                    "* Running on local URL:  {}://{}:{}, with SSR ⚡ (experimental, to disable set `ssr_mode=False` in `launch()`)"
                    if self.ssr_mode
                    else "* Running on local URL:  {}://{}:{}"
                )
                print(s.format(self.protocol, self.server_name, self.server_port))

            self._queue.set_server_app(self.server_app)

            if not wasm_utils.IS_WASM:
                # Cannot run async functions in background other than app's scope.
                # Workaround by triggering the app endpoint
                resp = httpx.get(
                    f"{self.local_api_url}startup-events",
                    verify=ssl_verify,
                    timeout=None,
                )
                if not resp.is_success:
                    raise Exception(
                        f"Couldn't start the app because '{resp.url}' failed (code {resp.status_code}). Check your network or proxy settings to ensure localhost is accessible."
                    )
            else:
                # NOTE: One benefit of the code above dispatching `startup_events()` via a self HTTP request is
                # that `self._queue.start()` is called in another thread which is managed by the HTTP server, `uvicorn`
                # so all the asyncio tasks created by the queue runs in an event loop in that thread and
                # will be cancelled just by stopping the server.
                # In contrast, in the Wasm env, we can't do that because `threading` is not supported and all async tasks will run in the same event loop, `pyodide.webloop.WebLoop` in the main thread.
                # So we need to manually cancel them. See `self.close()`..
                self.run_startup_events()
                # In the normal mode, self.run_extra_startup_events() is awaited like https://github.com/gradio-app/gradio/blob/2afcad80abd489111e47cf586a2a8221cc3dc9b6/gradio/routes.py#L1442.
                # But in the Wasm env, we need to call the start up events here as described above, so we can't await it as here is not in an async function.
                # So we use create_task() instead. This is a best-effort fallback in the Wasm env but it doesn't guarantee that all the tasks are completed before they are needed.
                asyncio.create_task(self.run_extra_startup_events())

        if share is None:
            if self.is_colab or self.is_hosted_notebook:
                if not quiet:
                    print(
                        "It looks like you are running Gradio on a hosted Jupyter notebook, which requires `share=True`. Automatically setting `share=True` (you can turn this off by setting `share=False` in `launch()` explicitly).\n"
                    )
                self.share = True
            else:
                self.share = False
                share_env = os.getenv("GRADIO_SHARE")
                if share_env is not None and share_env.lower() == "true":
                    self.share = True
        else:
            self.share = share

        if enable_monitoring:
            print(
                f"Monitoring URL: {self.local_url}monitoring/{self.app.analytics_key}"
            )
        self.enable_monitoring = enable_monitoring in [True, None]

        # If running in a colab or not able to access localhost,
        # a shareable link must be created.
        if (
            _frontend
            and not wasm_utils.IS_WASM
            and not networking.url_ok(self.local_url)
            and not self.share
        ):
            raise ValueError(
                "When localhost is not accessible, a shareable link must be created. Please set share=True or check your proxy settings to allow access to localhost."
            )

        if self.is_colab and not quiet:
            if debug:
                print(
                    "Colab notebook detected. This cell will run indefinitely so that you can see errors and logs. To turn off, set debug=False in launch()."
                )
            else:
                print(
                    "Colab notebook detected. To show errors in colab notebook, set debug=True in launch()"
                )
            if not self.share:
                print(
                    "Note: opening Chrome Inspector may crash demo inside Colab notebooks."
                )

        if self.share:
            if self.space_id:
                warnings.warn(
                    "Setting share=True is not supported on Hugging Face Spaces"
                )
                self.share = False
            if wasm_utils.IS_WASM:
                warnings.warn(
                    "Setting share=True is not supported in the Wasm environment"
                )
                self.share = False

        if self.share:
            try:
                if self.share_url is None:
                    share_url = networking.setup_tunnel(
                        local_host=self.server_name,
                        local_port=self.server_port,
                        share_token=self.share_token,
                        share_server_address=self.share_server_address,
                        share_server_tls_certificate=self.share_server_tls_certificate,
                    )
                    parsed_url = urlparse(share_url)
                    self.share_url = urlunparse(
                        (self.share_server_protocol,) + parsed_url[1:]
                    )
                print(f"* Running on public URL: {self.share_url}")
                if not (quiet):
                    print(
                        "\nThis share link expires in 1 week. For free permanent hosting and GPU upgrades, run `gradio deploy` from the terminal in the working directory to deploy to Hugging Face Spaces (https://huggingface.co/spaces)"
                    )
            except Exception as e:
                if self.analytics_enabled:
                    analytics.error_analytics("Not able to set up tunnel")
                self.share_url = None
                self.share = False
                if isinstance(e, ChecksumMismatchError):
                    print(
                        f"\nCould not create share link. Checksum mismatch for file: {BINARY_PATH}."
                    )
                elif Path(BINARY_PATH).exists():
                    print(
                        "\nCould not create share link. Please check your internet connection or our status page: https://status.gradio.app."
                    )
                else:
                    print(
                        f"\nCould not create share link. Missing file: {BINARY_PATH}. \n\nPlease check your internet connection. This can happen if your antivirus software blocks the download of this file. You can install manually by following these steps: \n\n1. Download this file: {BINARY_URL}\n2. Rename the downloaded file to: {BINARY_FILENAME}\n3. Move the file to this location: {BINARY_FOLDER}"
                    )
        else:
            if not quiet and not wasm_utils.IS_WASM:
                print("* To create a public link, set `share=True` in `launch()`.")
            self.share_url = None

        mcp_subpath = API_PREFIX + "/mcp"
        if self.mcp_server:
            print(
                f"\n🔨 MCP server (using SSE) running at: {self.share_url or self.local_url.rstrip('/')}/{mcp_subpath.lstrip('/')}/sse"
            )

        if inbrowser and not wasm_utils.IS_WASM:
            link = self.share_url if self.share and self.share_url else self.local_url
            webbrowser.open(link)

        # Check if running in a Python notebook in which case, display inline
        if inline is None:
            inline = utils.ipython_check()
        if inline:
            try:
                from IPython.display import HTML, Javascript, display  # type: ignore

                if self.share and self.share_url:
                    while not networking.url_ok(self.share_url):
                        time.sleep(0.25)
                    artifact = HTML(
                        f'<div><iframe src="{self.share_url}" width="{self.width}" height="{self.height}" allow="autoplay; camera; microphone; clipboard-read; clipboard-write;" frameborder="0" allowfullscreen></iframe></div>'
                    )

                elif self.is_colab:
                    # modified from /usr/local/lib/python3.7/dist-packages/google/colab/output/_util.py within Colab environment
                    code = """(async (port, path, width, height, cache, element) => {
                        if (!google.colab.kernel.accessAllowed && !cache) {
                            return;
                        }
                        element.appendChild(document.createTextNode(''));
                        const url = await google.colab.kernel.proxyPort(port, {cache});

                        const external_link = document.createElement('div');
                        external_link.innerHTML = `
                            <div style="font-family: monospace; margin-bottom: 0.5rem">
                                Running on <a href=${new URL(path, url).toString()} target="_blank">
                                    https://localhost:${port}${path}
                                </a>
                            </div>
                        `;
                        element.appendChild(external_link);

                        const iframe = document.createElement('iframe');
                        iframe.src = new URL(path, url).toString();
                        iframe.height = height;
                        iframe.allow = "autoplay; camera; microphone; clipboard-read; clipboard-write;"
                        iframe.width = width;
                        iframe.style.border = 0;
                        element.appendChild(iframe);
                    })""" + "({port}, {path}, {width}, {height}, {cache}, window.element)".format(
                        port=json.dumps(self.server_port),
                        path=json.dumps("/"),
                        width=json.dumps(self.width),
                        height=json.dumps(self.height),
                        cache=json.dumps(False),
                    )

                    artifact = Javascript(code)
                else:
                    artifact = HTML(
                        f'<div><iframe src="{self.local_url}" width="{self.width}" height="{self.height}" allow="autoplay; camera; microphone; clipboard-read; clipboard-write;" frameborder="0" allowfullscreen></iframe></div>'
                    )
                self.artifact = artifact
                display(artifact)
            except ImportError:
                pass

        if getattr(self, "analytics_enabled", False):
            data = {
                "launch_method": "browser" if inbrowser else "inline",
                "is_google_colab": self.is_colab,
                "is_sharing_on": self.share,
                "is_space": self.space_id is not None,
                "mode": self.mode,
            }
            analytics.launched_analytics(self, data)

        is_in_interactive_mode = bool(getattr(sys, "ps1", sys.flags.interactive))

        # Block main thread if debug==True
        if (
            debug
            or int(os.getenv("GRADIO_DEBUG", "0")) == 1
            and not wasm_utils.IS_WASM
            or (
                # Block main thread if running in a script to stop script from exiting
                not prevent_thread_lock
                and not is_in_interactive_mode
                # In the Wasm env, we don't have to block the main thread because the server won't be shut down after the execution finishes.
                # Moreover, we MUST NOT do it because there is only one thread in the Wasm env and blocking it will stop the subsequent code from running.
                and not wasm_utils.IS_WASM
            )
        ):
            self.block_thread()

        return TupleNoPrint((self.server_app, self.local_url, self.share_url))  # type: ignore

    def integrate(
        self,
        comet_ml=None,
        wandb: ModuleType | None = None,
        mlflow: ModuleType | None = None,
    ) -> None:
        """
        A catch-all method for integrating with other libraries. This method should be run after launch()
        Parameters:
            comet_ml: If a comet_ml Experiment object is provided, will integrate with the experiment and appear on Comet dashboard
            wandb: If the wandb module is provided, will integrate with it and appear on WandB dashboard
            mlflow: If the mlflow module  is provided, will integrate with the experiment and appear on ML Flow dashboard
        """
        analytics_integration = ""
        if comet_ml is not None:
            analytics_integration = "CometML"
            comet_ml.log_other("Created from", "Gradio")
            if self.share_url is not None:
                comet_ml.log_text(f"gradio: {self.share_url}")
                comet_ml.end()
            elif self.local_url:
                comet_ml.log_text(f"gradio: {self.local_url}")
                comet_ml.end()
            else:
                raise ValueError("Please run `launch()` first.")
        if wandb is not None:
            analytics_integration = "WandB"
            if self.share_url is not None:
                wandb.log(
                    {
                        "Gradio panel": wandb.Html(
                            '<iframe src="'
                            + self.share_url
                            + '" width="'
                            + str(self.width)
                            + '" height="'
                            + str(self.height)
                            + '" frameBorder="0"></iframe>'
                        )
                    }
                )
            else:
                print(
                    "The WandB integration requires you to `launch(share=True)` first."
                )
        if mlflow is not None:
            analytics_integration = "MLFlow"
            if self.share_url is not None:
                mlflow.log_param("Gradio Interface Share Link", self.share_url)
            else:
                mlflow.log_param("Gradio Interface Local Link", self.local_url)
        if self.analytics_enabled and analytics_integration:
            data = {"integration": analytics_integration}
            analytics.integration_analytics(data)

    def close(self, verbose: bool = True) -> None:
        """
        Closes the Interface that was launched and frees the port.
        """
        try:
            if wasm_utils.IS_WASM:
                # NOTE:
                # Normally, queue-related async tasks whose async tasks are started at the `/queue/data` endpoint function)
                # are running in an event loop in the server thread,
                # so they will be cancelled by `self.server.close()` below.
                # However, in the Wasm env, we don't have the `server` and
                # all async tasks are running in the same event loop, `pyodide.webloop.WebLoop` in the main thread,
                # so we have to cancel them explicitly so that these tasks won't run after a new app is launched.
                self._queue._cancel_asyncio_tasks()
                self.server_app._cancel_asyncio_tasks()
            self._queue.close()
            # set this before closing server to shut down heartbeats
            self.is_running = False
            self.app.stop_event.set()
            if self.server:
                self.server.close()
            # So that the startup events (starting the queue)
            # happen the next time the app is launched
            self.app.startup_events_triggered = False
            if verbose:
                print(f"Closing server running on port: {self.server_port}")
        except (AttributeError, OSError):  # can't close if not running
            pass

    def block_thread(
        self,
    ) -> None:
        """Block main thread until interrupted by user."""
        try:
            while True:
                time.sleep(0.1)
        except (KeyboardInterrupt, OSError):
            print("Keyboard interruption in main thread... closing server.")
            if self.server:
                self.server.close()
            for tunnel in CURRENT_TUNNELS:
                tunnel.kill()

    def run_startup_events(self):
        """Events that should be run when the app containing this block starts up."""
        self._queue.start()
        # So that processing can resume in case the queue was stopped
        self._queue.stopped = False
        self.is_running = True
        self.create_limiter()

    async def run_extra_startup_events(self):
        for startup_event in self.extra_startup_events:
            await startup_event()

    def get_api_info(self, all_endpoints: bool = False) -> APIInfo:
        """
        Gets the information needed to generate the API docs from a Blocks.
        Parameters:
            all_endpoints: If True, returns information about all endpoints, including those with show_api=False.
        """
        config = self.config
        api_info: APIInfo = {"named_endpoints": {}, "unnamed_endpoints": {}}

        for fn in self.fns.values():
            if not fn.fn or fn.api_name is False:
                continue
            if not all_endpoints and not fn.show_api:
                continue

            dependency_info: APIEndpointInfo = {
                "parameters": [],
                "returns": [],
                "show_api": fn.show_api,
            }
            fn_info = utils.get_function_params(fn.fn)  # type: ignore
            description, _, _ = utils.get_function_description(fn.fn)
            if description:
                dependency_info["description"] = description
            skip_endpoint = False

            inputs = fn.inputs
            for index, input_block in enumerate(inputs):
                for component in config["components"]:
                    if component["id"] == input_block._id:
                        break
                else:
                    skip_endpoint = True  # if component not found, skip endpoint
                    break
                type = component["props"]["name"]
                if self.blocks[component["id"]].skip_api:
                    continue
                label = component["props"].get("label", f"parameter_{input_block._id}")
                comp = self.get_component(component["id"])
                if not isinstance(comp, components.Component):
                    raise TypeError(f"{comp!r} is not a Component")
                info = component.get("api_info_as_input", component.get("api_info"))
                example = comp.example_inputs()
                python_type = client_utils.json_schema_to_python_type(info)

                # Since the clients use "api_name" and "fn_index" to designate the endpoint and
                # "result_callbacks" to specify the callbacks, we need to make sure that no parameters
                # have those names. Hence the final checks.
                if (
                    fn.fn
                    and index < len(fn_info)
                    and fn_info[index][0]
                    not in ["api_name", "fn_index", "result_callbacks"]
                ):
                    parameter_name = fn_info[index][0]
                else:
                    parameter_name = f"param_{index}"

                # How default values are set for the client: if a component has an initial value, then that parameter
                # is optional in the client and the initial value from the config is used as default in the client.
                # If the component does not have an initial value, but if the corresponding argument in the predict function has
                # a default value of None, then that parameter is also optional in the client and the None is used as default in the client.
                if component["props"].get("value") is not None:
                    parameter_has_default = True
                    parameter_default = component["props"]["value"]
                elif (
                    fn.fn
                    and index < len(fn_info)
                    and fn_info[index][1]
                    and fn_info[index][2] is None
                ):
                    parameter_has_default = True
                    parameter_default = None
                else:
                    parameter_has_default = False
                    parameter_default = None

                dependency_info["parameters"].append(
                    {
                        "label": label,
                        "parameter_name": parameter_name,
                        "parameter_has_default": parameter_has_default,
                        "parameter_default": parameter_default,
                        "type": info,
                        "python_type": {
                            "type": python_type,
                            "description": info.get("additional_description", ""),
                        },
                        "component": type.capitalize(),
                        "example_input": example,
                    }
                )

            outputs = fn.outputs
            for o in outputs:
                for component in config["components"]:
                    if component["id"] == o._id:
                        break
                else:
                    skip_endpoint = True  # if component not found, skip endpoint
                    break
                type = component["props"]["name"]
                if self.blocks[component["id"]].skip_api:
                    continue
                label = component["props"].get("label", f"value_{o._id}")
                comp = self.get_component(component["id"])
                if not isinstance(comp, components.Component):
                    raise TypeError(f"{comp!r} is not a Component")
                info = component.get("api_info_as_output", component["api_info"])
                example = comp.example_inputs()
                python_type = client_utils.json_schema_to_python_type(info)
                dependency_info["returns"].append(
                    {
                        "label": label,
                        "type": info,
                        "python_type": {
                            "type": python_type,
                            "description": info.get("description", ""),
                        },
                        "component": type.capitalize(),
                    }
                )

            if not skip_endpoint:
                api_info["named_endpoints"][f"/{fn.api_name}"] = dependency_info

        return api_info

    @staticmethod
    def get_event_targets(
        original_mapping: dict[int, Block], _targets: list, trigger: str
    ) -> list:
        target_events = []
        for target in _targets:
            # If target is just an integer (old format), use it directly with the trigger
            # Otherwise target is a tuple and we use its components
            target_id = target if isinstance(target, int) else target[0]
            event_name = trigger if isinstance(target, int) else target[1]
            block = original_mapping.get(target_id)
            # Blocks events are a special case because they are not stored in the blocks list in the config
            if block is None:
                if event_name in [
                    event.event_name if isinstance(event, EventListener) else event
                    for event in BLOCKS_EVENTS
                ]:
                    block = Context.root_block
                else:
                    raise ValueError(
                        f"Cannot find Block with id: {target_id} but is present as a target in the config"
                    )
            event = getattr(block, event_name)
            target_events.append(event)
        return target_events

    @document()
    def route(self, name: str, path: str | None = None) -> Blocks:
        """
        Adds a new page to the Blocks app.
        Parameters:
            name: The name of the page as it appears in the nav bar.
            path: The URL suffix appended after your Gradio app's root URL to access this page (e.g. if path="/test", the page may be accessible e.g. at http://localhost:7860/test). If not provided, the path is generated from the name by converting to lowercase and replacing spaces with hyphens. Any leading or trailing forward slashes are stripped.
        Example:
            with gr.Blocks() as demo:
                name = gr.Textbox(label="Name")
                ...
            with demo.route("Test", "/test"):
                num = gr.Number()
                ...
        """
        if get_blocks_context():
            raise ValueError(
                "You cannot create a route while inside a Blocks() context. Call route() outside the Blocks() context (unindent this line)."
            )

        if path:
            path = path.strip("/")
            valid_path_regex = re.compile(r"^[a-zA-Z0-9-._~!$&'()*+,;=:@\[\]]+$")
            if not valid_path_regex.match(path):
                raise ValueError(
                    f"Path '{path}' contains invalid characters. Paths can only contain alphanumeric characters and the following special characters: -._~!$&'()*+,;=:@[]"
                )
        if path in INTERNAL_ROUTES:
            raise ValueError(f"Route with path '{path}' already exists")
        if path is None:
            path = name.lower().replace(" ", "-")
            path = "".join(
                [letter for letter in path if letter.isalnum() or letter == "-"]
            )
        while path in INTERNAL_ROUTES or path in [page[0] for page in self.pages]:
            path = "_" + path
        self.pages.append((path, name))
        self.current_page = path
        return self


=== File: gradio/chat_interface.py ===
"""
This file defines a useful high-level abstraction to build Gradio chatbots: ChatInterface.
"""

from __future__ import annotations

import builtins
import copy
import dataclasses
import inspect
import os
import warnings
from collections.abc import AsyncGenerator, Callable, Generator, Sequence
from functools import wraps
from pathlib import Path
from typing import Any, Literal, Union, cast

import anyio
from gradio_client.documentation import document

from gradio import utils
from gradio.blocks import Blocks
from gradio.components import (
    JSON,
    BrowserState,
    Button,
    Chatbot,
    Component,
    Dataset,
    Markdown,
    MultimodalTextbox,
    State,
    Textbox,
    get_component_instance,
)
from gradio.components.chatbot import (
    ChatMessage,
    ExampleMessage,
    Message,
    MessageDict,
    TupleFormat,
)
from gradio.components.multimodal_textbox import MultimodalPostprocess, MultimodalValue
from gradio.context import get_blocks_context
from gradio.events import Dependency, EditData, SelectData
from gradio.flagging import ChatCSVLogger
from gradio.helpers import create_examples as Examples  # noqa: N812
from gradio.helpers import special_args, update
from gradio.i18n import I18nData
from gradio.layouts import Accordion, Column, Group, Row
from gradio.themes import ThemeClass as Theme


@document()
class ChatInterface(Blocks):
    """
    ChatInterface is Gradio's high-level abstraction for creating chatbot UIs, and allows you to create
    a web-based demo around a chatbot model in a few lines of code. Only one parameter is required: fn, which
    takes a function that governs the response of the chatbot based on the user input and chat history. Additional
    parameters can be used to control the appearance and behavior of the demo.

    Example:
        import gradio as gr

        def echo(message, history):
            return message

        demo = gr.ChatInterface(fn=echo, type="messages", examples=[{"text": "hello", "text": "hola", "text": "merhaba"}], title="Echo Bot")
        demo.launch()
    Demos: chatinterface_random_response, chatinterface_streaming_echo, chatinterface_artifacts
    Guides: creating-a-chatbot-fast, sharing-your-app
    """

    def __init__(
        self,
        fn: Callable,
        *,
        multimodal: bool = False,
        type: Literal["messages", "tuples"] | None = None,
        chatbot: Chatbot | None = None,
        textbox: Textbox | MultimodalTextbox | None = None,
        additional_inputs: str | Component | list[str | Component] | None = None,
        additional_inputs_accordion: str | Accordion | None = None,
        additional_outputs: Component | list[Component] | None = None,
        editable: bool = False,
        examples: list[str] | list[MultimodalValue] | list[list] | None = None,
        example_labels: list[str] | None = None,
        example_icons: list[str] | None = None,
        run_examples_on_click: bool = True,
        cache_examples: bool | None = None,
        cache_mode: Literal["eager", "lazy"] | None = None,
        title: str | I18nData | None = None,
        description: str | None = None,
        theme: Theme | str | None = None,
        flagging_mode: Literal["never", "manual"] | None = None,
        flagging_options: list[str] | tuple[str, ...] | None = ("Like", "Dislike"),
        flagging_dir: str = ".gradio/flagged",
        css: str | None = None,
        css_paths: str | Path | Sequence[str | Path] | None = None,
        js: str | Literal[True] | None = None,
        head: str | None = None,
        head_paths: str | Path | Sequence[str | Path] | None = None,
        analytics_enabled: bool | None = None,
        autofocus: bool = True,
        autoscroll: bool = True,
        submit_btn: str | bool | None = True,
        stop_btn: str | bool | None = True,
        concurrency_limit: int | None | Literal["default"] = "default",
        delete_cache: tuple[int, int] | None = None,
        show_progress: Literal["full", "minimal", "hidden"] = "minimal",
        fill_height: bool = True,
        fill_width: bool = False,
        api_name: str | Literal[False] = "chat",
        save_history: bool = False,
    ):
        """
        Parameters:
            fn: the function to wrap the chat interface around. Normally (assuming `type` is set to "messages"), the function should accept two parameters: a `str` representing the input message and `list` of openai-style dictionaries: {"role": "user" | "assistant", "content": `str` | {"path": `str`} | `gr.Component`} representing the chat history. The function should return/yield a `str` (for a simple message), a supported Gradio component (e.g. gr.Image to return an image), a `dict` (for a complete openai-style message response), or a `list` of such messages.
            multimodal: if True, the chat interface will use a `gr.MultimodalTextbox` component for the input, which allows for the uploading of multimedia files. If False, the chat interface will use a gr.Textbox component for the input. If this is True, the first argument of `fn` should accept not a `str` message but a `dict` message with keys "text" and "files"
            type: The format of the messages passed into the chat history parameter of `fn`. If "messages", passes the history as a list of dictionaries with openai-style "role" and "content" keys. The "content" key's value should be one of the following - (1) strings in valid Markdown (2) a dictionary with a "path" key and value corresponding to the file to display or (3) an instance of a Gradio component: at the moment gr.Image, gr.Plot, gr.Video, gr.Gallery, gr.Audio, and gr.HTML are supported. The "role" key should be one of 'user' or 'assistant'. Any other roles will not be displayed in the output. If this parameter is 'tuples' (deprecated), passes the chat history as a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message.
            chatbot: an instance of the gr.Chatbot component to use for the chat interface, if you would like to customize the chatbot properties. If not provided, a default gr.Chatbot component will be created.
            textbox: an instance of the gr.Textbox or gr.MultimodalTextbox component to use for the chat interface, if you would like to customize the textbox properties. If not provided, a default gr.Textbox or gr.MultimodalTextbox component will be created.
            editable: if True, users can edit past messages to regenerate responses.
            additional_inputs: an instance or list of instances of gradio components (or their string shortcuts) to use as additional inputs to the chatbot. If the components are not already rendered in a surrounding Blocks, then the components will be displayed under the chatbot, in an accordion. The values of these components will be passed into `fn` as arguments in order after the chat history.
            additional_inputs_accordion: if a string is provided, this is the label of the `gr.Accordion` to use to contain additional inputs. A `gr.Accordion` object can be provided as well to configure other properties of the container holding the additional inputs. Defaults to a `gr.Accordion(label="Additional Inputs", open=False)`. This parameter is only used if `additional_inputs` is provided.
            additional_outputs: an instance or list of instances of gradio components to use as additional outputs from the chat function. These must be components that are already defined in the same Blocks scope. If provided, the chat function should return additional values for these components. See $demo/chatinterface_artifacts.
            examples: sample inputs for the function; if provided, appear within the chatbot and can be clicked to populate the chatbot input. Should be a list of strings representing text-only examples, or a list of dictionaries (with keys `text` and `files`) representing multimodal examples. If `additional_inputs` are provided, the examples must be a list of lists, where the first element of each inner list is the string or dictionary example message and the remaining elements are the example values for the additional inputs -- in this case, the examples will appear under the chatbot.
            example_labels: labels for the examples, to be displayed instead of the examples themselves. If provided, should be a list of strings with the same length as the examples list. Only applies when examples are displayed within the chatbot (i.e. when `additional_inputs` is not provided).
            example_icons: icons for the examples, to be displayed above the examples. If provided, should be a list of string URLs or local paths with the same length as the examples list. Only applies when examples are displayed within the chatbot (i.e. when `additional_inputs` is not provided).
            cache_examples: if True, caches examples in the server for fast runtime in examples. The default option in HuggingFace Spaces is True. The default option elsewhere is False.  Note that examples are cached separately from Gradio's queue() so certain features, such as gr.Progress(), gr.Info(), gr.Warning(), etc. will not be displayed in Gradio's UI for cached examples.
            cache_mode: if "eager", all examples are cached at app launch. If "lazy", examples are cached for all users after the first use by any user of the app. If None, will use the GRADIO_CACHE_MODE environment variable if defined, or default to "eager".
            run_examples_on_click: if True, clicking on an example will run the example through the chatbot fn and the response will be displayed in the chatbot. If False, clicking on an example will only populate the chatbot input with the example message. Has no effect if `cache_examples` is True
            title: a title for the interface; if provided, appears above chatbot in large font. Also used as the tab title when opened in a browser window.
            description: a description for the interface; if provided, appears above the chatbot and beneath the title in regular font. Accepts Markdown and HTML content.
            theme: a Theme object or a string representing a theme. If a string, will look for a built-in theme with that name (e.g. "soft" or "default"), or will attempt to load a theme from the Hugging Face Hub (e.g. "gradio/monochrome"). If None, will use the Default theme.
            flagging_mode: one of "never", "manual". If "never", users will not see a button to flag an input and output. If "manual", users will see a button to flag.
            flagging_options: a list of strings representing the options that users can choose from when flagging a message. Defaults to ["Like", "Dislike"]. These two case-sensitive strings will render as "thumbs up" and "thumbs down" icon respectively next to each bot message, but any other strings appear under a separate flag icon.
            flagging_dir: path to the the directory where flagged data is stored. If the directory does not exist, it will be created.
            css: Custom css as a code string. This css will be included in the demo webpage.
            css_paths: Custom css as a pathlib.Path to a css file or a list of such paths. This css files will be read, concatenated, and included in the demo webpage. If the `css` parameter is also set, the css from `css` will be included first.
            js: Custom js as a code string. The custom js should be in the form of a single js function. This function will automatically be executed when the page loads. For more flexibility, use the head parameter to insert js inside <script> tags.
            head: Custom html code to insert into the head of the demo webpage. This can be used to add custom meta tags, multiple scripts, stylesheets, etc. to the page.
            head_paths: Custom html code as a pathlib.Path to a html file or a list of such paths. This html files will be read, concatenated, and included in the head of the demo webpage. If the `head` parameter is also set, the html from `head` will be included first.
            analytics_enabled: whether to allow basic telemetry. If None, will use GRADIO_ANALYTICS_ENABLED environment variable if defined, or default to True.
            autofocus: if True, autofocuses to the textbox when the page loads.
            autoscroll: If True, will automatically scroll to the bottom of the chatbot when a new message appears, unless the user scrolls up. If False, will not scroll to the bottom of the chatbot automatically.
            submit_btn: If True, will show a submit button with a submit icon within the textbox. If a string, will use that string as the submit button text in place of the icon. If False, will not show a submit button.
            stop_btn: If True, will show a button with a stop icon during generator executions, to stop generating. If a string, will use that string as the submit button text in place of the stop icon. If False, will not show a stop button.
            concurrency_limit: if set, this is the maximum number of chatbot submissions that can be running simultaneously. Can be set to None to mean no limit (any number of chatbot submissions can be running simultaneously). Set to "default" to use the default concurrency limit (defined by the `default_concurrency_limit` parameter in `.queue()`, which is 1 by default).
            delete_cache: a tuple corresponding [frequency, age] both expressed in number of seconds. Every `frequency` seconds, the temporary files created by this Blocks instance will be deleted if more than `age` seconds have passed since the file was created. For example, setting this to (86400, 86400) will delete temporary files every day. The cache will be deleted entirely when the server restarts. If None, no cache deletion will occur.
            show_progress: how to show the progress animation while event is running: "full" shows a spinner which covers the output component area as well as a runtime display in the upper right corner, "minimal" only shows the runtime display, "hidden" shows no progress animation at all
            fill_height: if True, the chat interface will expand to the height of window.
            fill_width: Whether to horizontally expand to fill container fully. If False, centers and constrains app to a maximum width.
            api_name: defines how the chat endpoint appears in the API docs. Can be a string or False. If set to a string, the chat endpoint will be exposed in the API docs with the given name. If False, the chat endpoint will not be exposed in the API docs and downstream apps (including those that `gr.load` this app) will not be able to call this chat endpoint.
            save_history: if True, will save the chat history to the browser's local storage and display previous conversations in a side panel.
        """
        super().__init__(
            analytics_enabled=analytics_enabled,
            mode="chat_interface",
            title=title or "Gradio",
            theme=theme,
            css=css,
            css_paths=css_paths,
            js=js,
            head=head,
            head_paths=head_paths,
            fill_height=fill_height,
            fill_width=fill_width,
            delete_cache=delete_cache,
        )
        self.api_name: str | Literal[False] = api_name
        self.type = type
        self.multimodal = multimodal
        self.concurrency_limit = concurrency_limit
        if isinstance(fn, ChatInterface):
            self.fn = fn.fn
        else:
            self.fn = fn
        self.is_async = inspect.iscoroutinefunction(
            self.fn
        ) or inspect.isasyncgenfunction(self.fn)
        self.is_generator = inspect.isgeneratorfunction(
            self.fn
        ) or inspect.isasyncgenfunction(self.fn)
        self.provided_chatbot = chatbot is not None
        self.examples = examples
        self.examples_messages = self._setup_example_messages(
            examples, example_labels, example_icons
        )
        self.run_examples_on_click = run_examples_on_click
        self.cache_examples = cache_examples
        self.cache_mode = cache_mode
        self.editable = editable
        self.fill_height = fill_height
        self.autoscroll = autoscroll
        self.autofocus = autofocus
        self.title = title
        self.description = description
        self.show_progress = show_progress
        if save_history and not type == "messages":
            raise ValueError("save_history is only supported for type='messages'")
        self.save_history = save_history
        self.additional_inputs = [
            get_component_instance(i)
            for i in utils.none_or_singleton_to_list(additional_inputs)
        ]
        self.additional_outputs = utils.none_or_singleton_to_list(additional_outputs)
        if additional_inputs_accordion is None:
            self.additional_inputs_accordion_params = {
                "label": "Additional Inputs",
                "open": False,
            }
        elif isinstance(additional_inputs_accordion, str):
            self.additional_inputs_accordion_params = {
                "label": additional_inputs_accordion
            }
        elif isinstance(additional_inputs_accordion, Accordion):
            self.additional_inputs_accordion_params = (
                additional_inputs_accordion.recover_kwargs(
                    additional_inputs_accordion.get_config()
                )
            )
        else:
            raise ValueError(
                f"The `additional_inputs_accordion` parameter must be a string or gr.Accordion, not {builtins.type(additional_inputs_accordion)}"
            )
        self._additional_inputs_in_examples = False
        if self.additional_inputs and self.examples is not None:
            for example in self.examples:
                if not isinstance(example, list):
                    raise ValueError(
                        "Examples must be a list of lists when additional inputs are provided."
                    )
                for idx, example_for_input in enumerate(example):
                    if example_for_input is not None and idx > 0:
                        self._additional_inputs_in_examples = True
                        break
                if self._additional_inputs_in_examples:
                    break

        if flagging_mode is None:
            flagging_mode = os.getenv("GRADIO_CHAT_FLAGGING_MODE", "never")  # type: ignore
        if flagging_mode in ["manual", "never"]:
            self.flagging_mode = flagging_mode
        else:
            raise ValueError(
                "Invalid value for `flagging_mode` parameter."
                "Must be: 'manual' or 'never'."
            )
        self.flagging_options = flagging_options
        self.flagging_dir = flagging_dir
        if isinstance(textbox, (Textbox, MultimodalTextbox)):
            textbox.unrender()
        if isinstance(chatbot, Chatbot):
            chatbot.unrender()

        with self:
            self.saved_conversations = BrowserState(
                [], storage_key=f"_saved_conversations_{self._id}"
            )
            self.conversation_id = State(None)
            self.saved_input = State()  # Stores the most recent user message
            self.null_component = State()  # Used to discard unneeded values

            with Column():
                self._render_header()
                if self.save_history:
                    with Row(scale=1):
                        self._render_history_area()
                        with Column(scale=6):
                            self._render_chatbot_area(
                                chatbot, textbox, submit_btn, stop_btn
                            )
                            self._render_footer()
                else:
                    self._render_chatbot_area(chatbot, textbox, submit_btn, stop_btn)
                    self._render_footer()

            self._setup_events()

    def _render_header(self):
        if self.title:
            Markdown(
                f"<h1 style='text-align: center; margin-bottom: 1rem'>{self.title}</h1>"
            )
        if self.description:
            Markdown(self.description)

    def _render_history_area(self):
        with Column(scale=1, min_width=100):
            self.new_chat_button = Button(
                "New chat",
                variant="primary",
                size="md",
                icon=utils.get_icon_path("plus.svg"),
                # scale=0,
            )
            self.chat_history_dataset = Dataset(
                components=[Textbox(visible=False)],
                show_label=False,
                layout="table",
                type="index",
            )

    def _render_chatbot_area(
        self,
        chatbot: Chatbot | None,
        textbox: Textbox | MultimodalTextbox | None,
        submit_btn: str | bool | None,
        stop_btn: str | bool | None,
    ):
        if chatbot:
            if self.type:
                if self.type != chatbot.type:
                    warnings.warn(
                        "The type of the gr.Chatbot does not match the type of the gr.ChatInterface."
                        f"The type of the gr.ChatInterface, '{self.type}', will be used."
                    )
                    chatbot.type = cast(Literal["messages", "tuples"], self.type)
                    chatbot._setup_data_model()
            else:
                warnings.warn(
                    f"The gr.ChatInterface was not provided with a type, so the type of the gr.Chatbot, '{chatbot.type}', will be used."
                )
                self.type = chatbot.type
            self.chatbot = cast(Chatbot, get_component_instance(chatbot, render=True))
            if self.chatbot.examples and self.examples_messages:
                warnings.warn(
                    "The ChatInterface already has examples set. The examples provided in the chatbot will be ignored."
                )
            self.chatbot.examples = (
                self.examples_messages
                if not self._additional_inputs_in_examples
                else None
            )
            self.chatbot._setup_examples()
        else:
            self.type = self.type or "tuples"
            self.chatbot = Chatbot(
                label="Chatbot",
                scale=1,
                height=400 if self.fill_height else None,
                type=cast(Literal["messages", "tuples"], self.type),
                autoscroll=self.autoscroll,
                examples=self.examples_messages
                if not self._additional_inputs_in_examples
                else None,
            )
        with Group():
            with Row():
                if textbox:
                    textbox.show_label = False
                    textbox_ = get_component_instance(textbox, render=True)
                    if not isinstance(textbox_, (Textbox, MultimodalTextbox)):
                        raise TypeError(
                            f"Expected a gr.Textbox or gr.MultimodalTextbox component, but got {builtins.type(textbox_)}"
                        )
                    self.textbox = textbox_
                else:
                    textbox_component = (
                        MultimodalTextbox if self.multimodal else Textbox
                    )
                    self.textbox = textbox_component(
                        show_label=False,
                        label="Message",
                        placeholder="Type a message...",
                        scale=7,
                        autofocus=self.autofocus,
                        submit_btn=submit_btn,
                        stop_btn=stop_btn,
                    )

        # Hide the stop button at the beginning, and show it with the given value during the generator execution.
        self.original_stop_btn = self.textbox.stop_btn
        self.textbox.stop_btn = False
        self.fake_api_btn = Button("Fake API", visible=False)
        self.api_response = JSON(
            label="Response", visible=False
        )  # Used to store the response from the API call

        # Used internally to store the chatbot value when it differs from the value displayed in the chatbot UI.
        # For example, when a user submits a message, the chatbot UI is immediately updated with the user message,
        # but the chatbot_state value is not updated until the submit_fn is called.
        self.chatbot_state = State(self.chatbot.value if self.chatbot.value else [])

        # Provided so that developers can update the chatbot value from other events outside of `gr.ChatInterface`.
        self.chatbot_value = State(self.chatbot.value if self.chatbot.value else [])

    def _render_footer(self):
        if self.examples:
            self.examples_handler = Examples(
                examples=self.examples,
                inputs=[self.textbox] + self.additional_inputs,
                outputs=self.chatbot,
                fn=self._examples_stream_fn if self.is_generator else self._examples_fn,
                cache_examples=self.cache_examples,
                cache_mode=cast(Literal["eager", "lazy"], self.cache_mode),
                visible=self._additional_inputs_in_examples,
                preprocess=self._additional_inputs_in_examples,
            )

        any_unrendered_inputs = any(
            not inp.is_rendered for inp in self.additional_inputs
        )
        if self.additional_inputs and any_unrendered_inputs:
            with Accordion(**self.additional_inputs_accordion_params):  # type: ignore
                for input_component in self.additional_inputs:
                    if not input_component.is_rendered:
                        input_component.render()

    def _setup_example_messages(
        self,
        examples: list[str] | list[MultimodalValue] | list[list] | None,
        example_labels: list[str] | None = None,
        example_icons: list[str] | None = None,
    ) -> list[ExampleMessage]:
        examples_messages = []
        if examples:
            for index, example in enumerate(examples):
                if isinstance(example, list):
                    example = example[0]
                example_message: ExampleMessage = {}
                if isinstance(example, str):
                    example_message["text"] = example
                elif isinstance(example, dict):
                    example_message["text"] = example.get("text", "")
                    example_message["files"] = example.get("files", [])
                if example_labels:
                    example_message["display_text"] = example_labels[index]
                if self.multimodal:
                    example_files = example_message.get("files")
                    if not example_files:
                        if example_icons:
                            example_message["icon"] = example_icons[index]
                        else:
                            example_message["icon"] = {
                                "path": "",
                                "url": None,
                                "orig_name": None,
                                "mime_type": "text",  # for internal use, not a valid mime type
                                "meta": {"_type": "gradio.FileData"},
                            }
                elif example_icons:
                    example_message["icon"] = example_icons[index]
                examples_messages.append(example_message)
        return examples_messages

    def _generate_chat_title(self, conversation: list[MessageDict]) -> str:
        """
        Generate a title for a conversation by taking the first user message that is a string
        and truncating it to 40 characters. If files are present, add a 📎 to the title.
        """
        title = ""
        for message in conversation:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    title += message["content"]
                    break
                else:
                    title += "📎 "
        if len(title) > 40:
            title = title[:40] + "..."
        return title or "Conversation"

    @staticmethod
    def serialize_components(conversation: list[MessageDict]) -> list[MessageDict]:
        def inner(obj: Any) -> Any:
            if isinstance(obj, list):
                return [inner(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: inner(v) for k, v in obj.items()}
            elif isinstance(obj, Component):
                return obj.value
            return obj

        return inner(conversation)

    def _save_conversation(
        self,
        index: int | None,
        conversation: list[MessageDict],
        saved_conversations: list[list[MessageDict]],
    ):
        if self.save_history:
            serialized_conversation = self.serialize_components(conversation)
            if index is not None:
                saved_conversations[index] = serialized_conversation
            else:
                saved_conversations = saved_conversations or []
                saved_conversations.insert(0, serialized_conversation)
                index = 0
        return index, saved_conversations

    def _delete_conversation(
        self,
        index: int | None,
        saved_conversations: list[list[MessageDict]],
    ):
        if index is not None:
            saved_conversations.pop(index)
        return None, saved_conversations

    def _load_chat_history(self, conversations):
        return Dataset(
            samples=[
                [self._generate_chat_title(conv)]
                for conv in conversations or []
                if conv
            ]
        )

    def _load_conversation(
        self,
        index: int,
        conversations: list[list[MessageDict]],
    ):
        return (
            index,
            Chatbot(
                value=conversations[index],  # type: ignore
                feedback_value=[],
                type="messages",
            ),
        )

    def _api_wrapper(self, fn, submit_fn):
        """Wrap the submit_fn in a way that preserves the signature of the original function.
        That way, the API page shows the same parameters as the original function.
        """
        # Need two separate functions here because a `return`
        # statement can't be placed in an async generator function.
        # using different names because otherwise type checking complains
        if self.is_generator:

            @wraps(fn)
            async def _wrapper(*args, **kwargs):
                async for chunk in submit_fn(*args, **kwargs):
                    yield chunk

            return _wrapper
        else:

            @wraps(fn)
            async def __wrapper(*args, **kwargs):
                return await submit_fn(*args, **kwargs)

            return __wrapper

    def _setup_events(self) -> None:
        from gradio import on

        submit_fn = self._stream_fn if self.is_generator else self._submit_fn

        submit_wrapped = self._api_wrapper(self.fn, submit_fn)
        # To not conflict with the api_name
        submit_wrapped.__name__ = "_submit_fn"
        api_fn = self._api_wrapper(self.fn, submit_fn)

        synchronize_chat_state_kwargs = {
            "fn": lambda x: (x, x),
            "inputs": [self.chatbot],
            "outputs": [self.chatbot_state, self.chatbot_value],
            "show_api": False,
            "queue": False,
        }
        submit_fn_kwargs = {
            "fn": submit_wrapped,
            "inputs": [self.saved_input, self.chatbot_state] + self.additional_inputs,
            "outputs": [self.null_component, self.chatbot] + self.additional_outputs,
            "show_api": False,
            "concurrency_limit": cast(
                Union[int, Literal["default"], None], self.concurrency_limit
            ),
            "show_progress": cast(
                Literal["full", "minimal", "hidden"], self.show_progress
            ),
        }
        save_fn_kwargs = {
            "fn": self._save_conversation,
            "inputs": [
                self.conversation_id,
                self.chatbot_state,
                self.saved_conversations,
            ],
            "outputs": [self.conversation_id, self.saved_conversations],
            "show_api": False,
            "queue": False,
        }

        submit_event = (
            self.textbox.submit(
                self._clear_and_save_textbox,
                [self.textbox],
                [self.textbox, self.saved_input],
                show_api=False,
                queue=False,
            )
            .then(  # The reason we do this outside of the submit_fn is that we want to update the chatbot UI with the user message immediately, before the submit_fn is called
                self._append_message_to_history,
                [self.saved_input, self.chatbot],
                [self.chatbot],
                show_api=False,
                queue=False,
            )
            .then(**submit_fn_kwargs)
        )
        submit_event.then(**synchronize_chat_state_kwargs).then(
            lambda: update(value=None, interactive=True),
            None,
            self.textbox,
            show_api=False,
        ).then(**save_fn_kwargs)

        # Creates the "/chat" API endpoint
        self.fake_api_btn.click(
            api_fn,
            [self.textbox, self.chatbot_state] + self.additional_inputs,
            [self.api_response, self.chatbot_state] + self.additional_outputs,
            api_name=self.api_name,
            concurrency_limit=cast(
                Union[int, Literal["default"], None], self.concurrency_limit
            ),
            postprocess=False,
        )

        example_select_event = None
        if (
            isinstance(self.chatbot, Chatbot)
            and self.examples
            and not self._additional_inputs_in_examples
        ):
            if self.cache_examples or self.run_examples_on_click:
                example_select_event = self.chatbot.example_select(
                    self.example_clicked,
                    None,
                    [self.chatbot, self.saved_input],
                    show_api=False,
                )
                if not self.cache_examples:
                    example_select_event = example_select_event.then(**submit_fn_kwargs)
                example_select_event.then(**synchronize_chat_state_kwargs)
            else:
                example_select_event = self.chatbot.example_select(
                    self.example_populated,
                    None,
                    [self.textbox],
                    show_api=False,
                )

        retry_event = (
            self.chatbot.retry(
                self._pop_last_user_message,
                [self.chatbot_state],
                [self.chatbot_state, self.saved_input],
                show_api=False,
                queue=False,
            )
            .then(
                self._append_message_to_history,
                [self.saved_input, self.chatbot_state],
                [self.chatbot],
                show_api=False,
                queue=False,
            )
            .then(
                lambda: update(interactive=False, placeholder=""),
                outputs=[self.textbox],
                show_api=False,
            )
            .then(**submit_fn_kwargs)
        )
        retry_event.then(**synchronize_chat_state_kwargs).then(
            lambda: update(interactive=True),
            outputs=[self.textbox],
            show_api=False,
        ).then(**save_fn_kwargs)

        events_to_cancel = [submit_event, retry_event]
        if example_select_event is not None:
            events_to_cancel.append(example_select_event)

        self._setup_stop_events(
            event_triggers=[
                self.textbox.submit,
                self.chatbot.retry,
                self.chatbot.example_select,
            ],
            events_to_cancel=events_to_cancel,
        )

        self.chatbot.undo(
            self._pop_last_user_message,
            [self.chatbot],
            [self.chatbot, self.textbox],
            show_api=False,
            queue=False,
        ).then(**synchronize_chat_state_kwargs).then(**save_fn_kwargs)

        self.chatbot.option_select(
            self.option_clicked,
            [self.chatbot],
            [self.chatbot, self.saved_input],
            show_api=False,
        ).then(**submit_fn_kwargs).then(**synchronize_chat_state_kwargs).then(
            **save_fn_kwargs
        )

        self.chatbot.clear(**synchronize_chat_state_kwargs).then(
            self._delete_conversation,
            [self.conversation_id, self.saved_conversations],
            [self.conversation_id, self.saved_conversations],
            show_api=False,
            queue=False,
        )

        if self.editable:
            self.chatbot.edit(
                self._edit_message,
                [self.chatbot],
                [self.chatbot, self.chatbot_state, self.saved_input],
                show_api=False,
            ).success(**submit_fn_kwargs).success(**synchronize_chat_state_kwargs).then(
                **save_fn_kwargs
            )

        if self.save_history:
            self.new_chat_button.click(
                lambda: (None, []),
                None,
                [self.conversation_id, self.chatbot],
                show_api=False,
                queue=False,
            ).then(
                lambda x: x,
                [self.chatbot],
                [self.chatbot_state],
                show_api=False,
                queue=False,
            )

            on(
                triggers=[self.load, self.saved_conversations.change],
                fn=self._load_chat_history,
                inputs=[self.saved_conversations],
                outputs=[self.chat_history_dataset],
                show_api=False,
                queue=False,
            )

            self.chat_history_dataset.click(
                lambda: [],
                None,
                [self.chatbot],
                show_api=False,
                queue=False,
                show_progress="hidden",
            ).then(
                self._load_conversation,
                [self.chat_history_dataset, self.saved_conversations],
                [self.conversation_id, self.chatbot],
                show_api=False,
                queue=False,
                show_progress="hidden",
            ).then(**synchronize_chat_state_kwargs)

        if self.flagging_mode != "never":
            flagging_callback = ChatCSVLogger()
            flagging_callback.setup(self.flagging_dir)
            self.chatbot.feedback_options = self.flagging_options
            self.chatbot.like(flagging_callback.flag, self.chatbot)

        self.chatbot_value.change(
            lambda x: x,
            [self.chatbot_value],
            [self.chatbot],
            show_api=False,
        ).then(**synchronize_chat_state_kwargs)

    def _setup_stop_events(
        self, event_triggers: list[Callable], events_to_cancel: list[Dependency]
    ) -> None:
        textbox_component = MultimodalTextbox if self.multimodal else Textbox
        original_submit_btn = self.textbox.submit_btn
        for event_trigger in event_triggers:
            event_trigger(
                utils.async_lambda(
                    lambda: textbox_component(
                        submit_btn=False,
                        stop_btn=self.original_stop_btn,
                    )
                ),
                None,
                [self.textbox],
                show_api=False,
                queue=False,
            )
        for event_to_cancel in events_to_cancel:
            event_to_cancel.then(
                utils.async_lambda(
                    lambda: textbox_component(
                        submit_btn=original_submit_btn, stop_btn=False
                    )
                ),
                None,
                [self.textbox],
                show_api=False,
                queue=False,
            )
        self.textbox.stop(
            None,
            None,
            None,
            cancels=events_to_cancel,  # type: ignore
            show_api=False,
        )

    def _clear_and_save_textbox(
        self,
        message: str | MultimodalPostprocess,
    ) -> tuple[
        Textbox | MultimodalTextbox,
        str | MultimodalPostprocess,
    ]:
        return (
            type(self.textbox)("", interactive=False, placeholder=""),
            message,
        )

    @staticmethod
    def _messages_to_tuples(history_messages: list[MessageDict]) -> TupleFormat:
        history_tuples = []
        for message in history_messages:
            if message["role"] == "user":
                history_tuples.append((message["content"], None))
            elif history_tuples and history_tuples[-1][1] is None:
                history_tuples[-1] = (history_tuples[-1][0], message["content"])
            else:
                history_tuples.append((None, message["content"]))
        return history_tuples

    @staticmethod
    def _tuples_to_messages(history_tuples: TupleFormat) -> list[MessageDict]:
        history_messages = []
        for message_tuple in history_tuples:
            if message_tuple[0]:
                history_messages.append({"role": "user", "content": message_tuple[0]})
            if message_tuple[1]:
                history_messages.append(
                    {"role": "assistant", "content": message_tuple[1]}
                )
        return history_messages

    def _append_message_to_history(
        self,
        message: MessageDict | Message | str | Component | MultimodalPostprocess | list,
        history: list[MessageDict] | TupleFormat,
        role: Literal["user", "assistant"] = "user",
    ) -> list[MessageDict] | TupleFormat:
        message_dicts = self._message_as_message_dict(message, role)
        if self.type == "tuples":
            history = self._tuples_to_messages(history)  # type: ignore
        else:
            history = copy.deepcopy(history)
        history.extend(message_dicts)  # type: ignore
        if self.type == "tuples":
            history = self._messages_to_tuples(history)  # type: ignore
        return history

    def _message_as_message_dict(
        self,
        message: MessageDict | Message | str | Component | MultimodalPostprocess | list,
        role: Literal["user", "assistant"],
    ) -> list[MessageDict]:
        """
        Converts a user message, example message, or response from the chat function to a
        list of MessageDict objects that can be appended to the chat history.
        """
        message_dicts = []
        if not isinstance(message, list):
            message = [message]
        for msg in message:
            if isinstance(msg, Message):
                message_dicts.append(msg.model_dump())
            elif isinstance(msg, ChatMessage):
                msg.role = role
                message_dicts.append(
                    dataclasses.asdict(msg, dict_factory=utils.dict_factory)
                )
            elif isinstance(msg, (str, Component)):
                message_dicts.append({"role": role, "content": msg})
            elif (
                isinstance(msg, dict) and "content" in msg
            ):  # in MessageDict format already
                msg["role"] = role
                message_dicts.append(msg)
            else:  # in MultimodalPostprocess format
                for x in msg.get("files", []):
                    if isinstance(x, dict):
                        x = x.get("path")
                    message_dicts.append({"role": role, "content": (x,)})
                if msg["text"] is None or not isinstance(msg["text"], str):
                    pass
                else:
                    message_dicts.append({"role": role, "content": msg["text"]})
        return message_dicts

    async def _submit_fn(
        self,
        message: str | MultimodalPostprocess,
        history: TupleFormat | list[MessageDict],
        *args,
    ) -> tuple:
        inputs = [message, history] + list(args)
        if self.is_async:
            response = await self.fn(*inputs)
        else:
            response = await anyio.to_thread.run_sync(
                self.fn, *inputs, limiter=self.limiter
            )
        if self.additional_outputs:
            response, *additional_outputs = response
        else:
            additional_outputs = None
        history = self._append_message_to_history(message, history, "user")
        history = self._append_message_to_history(response, history, "assistant")
        if additional_outputs:
            return response, history, *additional_outputs
        return response, history

    async def _stream_fn(
        self,
        message: str | MultimodalPostprocess,
        history: TupleFormat | list[MessageDict],
        *args,
    ) -> AsyncGenerator[
        tuple,
        None,
    ]:
        inputs = [message, history] + list(args)
        if self.is_async:
            generator = self.fn(*inputs)
        else:
            generator = await anyio.to_thread.run_sync(
                self.fn, *inputs, limiter=self.limiter
            )
            generator = utils.SyncToAsyncIterator(generator, self.limiter)

        history = self._append_message_to_history(message, history, "user")
        additional_outputs = None
        try:
            first_response = await utils.async_iteration(generator)
            if self.additional_outputs:
                first_response, *additional_outputs = first_response
            history_ = self._append_message_to_history(
                first_response, history, "assistant"
            )
            if not additional_outputs:
                yield first_response, history_
            else:
                yield first_response, history_, *additional_outputs
        except StopIteration:
            yield None, history
        async for response in generator:
            if self.additional_outputs:
                response, *additional_outputs = response
            history_ = self._append_message_to_history(response, history, "assistant")
            if not additional_outputs:
                yield response, history_
            else:
                yield response, history_, *additional_outputs

    def option_clicked(
        self, history: list[MessageDict], option: SelectData
    ) -> tuple[TupleFormat | list[MessageDict], str | MultimodalPostprocess]:
        """
        When an option is clicked, the chat history is appended with the option value.
        The saved input value is also set to option value. Note that event can only
        be called if self.type is "messages" since options are only available for this
        chatbot type.
        """
        history.append({"role": "user", "content": option.value})
        return history, option.value

    def _flatten_example_files(self, example: SelectData):
        """
        Returns an example with the files flattened to just the file path.
        Also ensures that the `files` key is always present in the example.
        """
        example.value["files"] = [f["path"] for f in example.value.get("files", [])]
        return example

    def example_populated(self, example: SelectData):
        if self.multimodal:
            example = self._flatten_example_files(example)
            return example.value
        else:
            return example.value["text"]

    def _edit_message(
        self, history: list[MessageDict] | TupleFormat, edit_data: EditData
    ) -> tuple[
        list[MessageDict] | TupleFormat,
        list[MessageDict] | TupleFormat,
        str | MultimodalPostprocess,
    ]:
        if isinstance(edit_data.index, (list, tuple)):
            history = history[: edit_data.index[0]]
        else:
            history = history[: edit_data.index]
        return history, history, edit_data.value

    def example_clicked(
        self, example: SelectData
    ) -> Generator[
        tuple[TupleFormat | list[MessageDict], str | MultimodalPostprocess], None, None
    ]:
        """
        When an example is clicked, the chat history (and saved input) is initially set only
        to the example message. Then, if example caching is enabled, the cached response is loaded
        and added to the chat history as well.
        """
        history = self._append_message_to_history(example.value, [], "user")
        example = self._flatten_example_files(example)
        message = example.value if self.multimodal else example.value["text"]
        yield history, message
        if self.cache_examples:
            history = self.examples_handler.load_from_cache(example.index)[0].root
            yield history, message

    def _process_example(
        self, message: ExampleMessage | str, response: MessageDict | str | None
    ):
        result = []
        if self.multimodal:
            message = cast(ExampleMessage, message)
            if self.type == "tuples":
                for file in message.get("files", []):
                    result.append([file, None])
                if "text" in message:
                    result.append([message["text"], None])
                result[-1][1] = response
            else:
                for file in message.get("files", []):
                    if isinstance(file, dict):
                        file = file.get("path")
                    result.append({"role": "user", "content": (file,)})
                if "text" in message:
                    result.append({"role": "user", "content": message["text"]})
                result.append({"role": "assistant", "content": response})
        else:
            message = cast(str, message)
            if self.type == "tuples":
                result = [[message, response]]
            else:
                result = [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response},
                ]
        return result

    async def _examples_fn(
        self, message: ExampleMessage | str, *args
    ) -> TupleFormat | list[MessageDict]:
        inputs, _, _ = special_args(self.fn, inputs=[message, [], *args], request=None)
        if self.is_async:
            response = await self.fn(*inputs)
        else:
            response = await anyio.to_thread.run_sync(
                self.fn, *inputs, limiter=self.limiter
            )
        return self._process_example(message, response)  # type: ignore

    async def _examples_stream_fn(
        self,
        message: str,
        *args,
    ) -> AsyncGenerator:
        inputs, _, _ = special_args(self.fn, inputs=[message, [], *args], request=None)

        if self.is_async:
            generator = self.fn(*inputs)
        else:
            generator = await anyio.to_thread.run_sync(
                self.fn, *inputs, limiter=self.limiter
            )
            generator = utils.SyncToAsyncIterator(generator, self.limiter)
        async for response in generator:
            yield self._process_example(message, response)

    def _pop_last_user_message(
        self,
        history: list[MessageDict] | TupleFormat,
    ) -> tuple[list[MessageDict] | TupleFormat, str | MultimodalPostprocess]:
        """
        Removes the message (or set of messages) that the user last sent from the chat history and returns them.
        If self.multimodal is True, returns a MultimodalPostprocess (dict) object with text and files.
        If self.multimodal is False, returns just the message text as a string.
        """
        if not history:
            return history, "" if not self.multimodal else {"text": "", "files": []}

        if self.type == "tuples":
            history = self._tuples_to_messages(history)  # type: ignore
        i = len(history) - 1
        while i >= 0 and history[i]["role"] == "assistant":  # type: ignore
            i -= 1
        while i >= 0 and history[i]["role"] == "user":  # type: ignore
            i -= 1
        last_messages = history[i + 1 :]
        last_user_message = ""
        files = []
        for msg in last_messages:
            assert isinstance(msg, dict)  # noqa: S101
            if msg["role"] == "user":
                content = msg["content"]
                if isinstance(content, tuple):
                    files.append(content[0])
                else:
                    last_user_message = content
        return_message = (
            {"text": last_user_message, "files": files}
            if self.multimodal
            else last_user_message
        )
        history_ = history[: i + 1]
        if self.type == "tuples":
            history_ = self._messages_to_tuples(history_)  # type: ignore
        return history_, return_message  # type: ignore

    def render(self) -> ChatInterface:
        # If this is being rendered inside another Blocks, and the height is not explicitly set, set it to 400 instead of 200.
        if get_blocks_context() and not self.provided_chatbot:
            self.chatbot.height = 400
            super().render()
        return self


=== File: gradio/interface.py ===
"""
This file defines two useful high-level abstractions to build Gradio apps: Interface and TabbedInterface.
"""

from __future__ import annotations

import inspect
import json
import os
import warnings
import weakref
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio import Examples, utils, wasm_utils
from gradio.blocks import Blocks
from gradio.components import (
    Button,
    ClearButton,
    Component,
    DeepLinkButton,
    DuplicateButton,
    Markdown,
    State,
    get_component_instance,
)
from gradio.data_classes import InterfaceTypes
from gradio.events import Dependency, Events, on
from gradio.exceptions import RenderError
from gradio.flagging import CSVLogger, FlaggingCallback, FlagMethod
from gradio.i18n import I18nData
from gradio.layouts import Accordion, Column, Row, Tab, Tabs
from gradio.pipelines import load_from_js_pipeline, load_from_pipeline
from gradio.themes import ThemeClass as Theme

if TYPE_CHECKING:  # Only import for type checking (is False at runtime).
    from diffusers import DiffusionPipeline  # type: ignore
    from transformers.pipelines.base import Pipeline


@document("launch", "load", "from_pipeline", "integrate", "queue")
class Interface(Blocks):
    """
    Interface is Gradio's main high-level class, and allows you to create a web-based GUI / demo
    around a machine learning model (or any Python function) in a few lines of code.
    You must specify three parameters: (1) the function to create a GUI for (2) the desired input components and
    (3) the desired output components. Additional parameters can be used to control the appearance
    and behavior of the demo.

    Example:
        import gradio as gr

        def image_classifier(inp):
            return {'cat': 0.3, 'dog': 0.7}

        demo = gr.Interface(fn=image_classifier, inputs="image", outputs="label")
        demo.launch()
    Demos: hello_world, hello_world_2, hello_world_3
    Guides: quickstart, key-features, sharing-your-app, interface-state, reactive-interfaces, advanced-interface-features, setting-up-a-gradio-demo-for-maximum-performance
    """

    # stores references to all currently existing Interface instances
    instances: weakref.WeakSet = weakref.WeakSet()

    @classmethod
    def get_instances(cls) -> list[Interface]:
        """
        :return: list of all current instances.
        """
        return list(Interface.instances)

    @classmethod
    def from_pipeline(
        cls, pipeline: Pipeline | DiffusionPipeline, **kwargs
    ) -> Interface:
        """
        Class method that constructs an Interface from a Hugging Face transformers.Pipeline or diffusers.DiffusionPipeline object.
        The input and output components are automatically determined from the pipeline.
        Parameters:
            pipeline: the pipeline object to use.
        Returns:
            a Gradio Interface object from the given Pipeline
        Example:
            import gradio as gr
            from transformers import pipeline
            pipe = pipeline("image-classification")
            gr.Interface.from_pipeline(pipe).launch()
        """
        if wasm_utils.IS_WASM:
            interface_info = load_from_js_pipeline(pipeline)
        else:
            interface_info = load_from_pipeline(pipeline)
        kwargs = dict(interface_info, **kwargs)
        interface = cls(**kwargs)
        return interface

    def __init__(
        self,
        fn: Callable,
        inputs: str | Component | Sequence[str | Component] | None,
        outputs: str | Component | Sequence[str | Component] | None,
        examples: list[Any] | list[list[Any]] | str | None = None,
        *,
        cache_examples: bool | None = None,
        cache_mode: Literal["eager", "lazy"] | None = None,
        examples_per_page: int = 10,
        example_labels: list[str] | None = None,
        preload_example: int | Literal[False] = False,
        live: bool = False,
        title: str | I18nData | None = None,
        description: str | None = None,
        article: str | None = None,
        theme: Theme | str | None = None,
        flagging_mode: Literal["never"]
        | Literal["auto"]
        | Literal["manual"]
        | None = None,
        flagging_options: list[str] | list[tuple[str, str]] | None = None,
        flagging_dir: str = ".gradio/flagged",
        flagging_callback: FlaggingCallback | None = None,
        analytics_enabled: bool | None = None,
        batch: bool = False,
        max_batch_size: int = 4,
        api_name: str | Literal[False] | None = "predict",
        _api_mode: bool = False,
        allow_duplication: bool = False,
        concurrency_limit: int | None | Literal["default"] = "default",
        css: str | None = None,
        css_paths: str | Path | Sequence[str | Path] | None = None,
        js: str | Literal[True] | None = None,
        head: str | None = None,
        head_paths: str | Path | Sequence[str | Path] | None = None,
        additional_inputs: str | Component | Sequence[str | Component] | None = None,
        additional_inputs_accordion: str | Accordion | None = None,
        submit_btn: str | Button = "Submit",
        stop_btn: str | Button = "Stop",
        clear_btn: str | Button | None = "Clear",
        delete_cache: tuple[int, int] | None = None,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        fill_width: bool = False,
        allow_flagging: Literal["never"]
        | Literal["auto"]
        | Literal["manual"]
        | None = None,
        time_limit: int | None = 30,
        stream_every: float = 0.5,
        deep_link: str | DeepLinkButton | bool | None = None,
        **kwargs,
    ):
        """
        Parameters:
            fn: the function to wrap an interface around. Often a machine learning model's prediction function. Each parameter of the function corresponds to one input component, and the function should return a single value or a tuple of values, with each element in the tuple corresponding to one output component.
            inputs: a single Gradio component, or list of Gradio components. Components can either be passed as instantiated objects, or referred to by their string shortcuts. The number of input components should match the number of parameters in fn. If set to None, then only the output components will be displayed.
            outputs: a single Gradio component, or list of Gradio components. Components can either be passed as instantiated objects, or referred to by their string shortcuts. The number of output components should match the number of values returned by fn. If set to None, then only the input components will be displayed.
            examples: sample inputs for the function; if provided, appear below the UI components and can be clicked to populate the interface. Should be nested list, in which the outer list consists of samples and each inner list consists of an input corresponding to each input component. A string path to a directory of examples can also be provided, but it should be within the directory with the python file running the gradio app. If there are multiple input components and a directory is provided, a log.csv file must be present in the directory to link corresponding inputs.
            cache_examples: If True, caches examples in the server for fast runtime in examples. If "lazy", then examples are cached (for all users of the app) after their first use (by any user of the app). If None, will use the GRADIO_CACHE_EXAMPLES environment variable, which should be either "true" or "false". In HuggingFace Spaces, this parameter defaults to True (as long as `fn` and `outputs` are also provided).  Note that examples are cached separately from Gradio's queue() so certain features, such as gr.Progress(), gr.Info(), gr.Warning(), etc. will not be displayed in Gradio's UI for cached examples.
            cache_mode: if "lazy", examples are cached after their first use. If "eager", all examples are cached at app launch. If None, will use the GRADIO_CACHE_MODE environment variable if defined, or default to "eager". In HuggingFace Spaces, this parameter defaults to "eager" except for ZeroGPU Spaces, in which case it defaults to "lazy".
            examples_per_page: if examples are provided, how many to display per page.
            preload_example: If an integer is provided (and examples are being cached), the example at that index in the examples list will be preloaded when the Gradio app is first loaded. If False, no example will be preloaded.
            live: whether the interface should automatically rerun if any of the inputs change.
            title: a title for the interface; if provided, appears above the input and output components in large font. Also used as the tab title when opened in a browser window.
            description: a description for the interface; if provided, appears above the input and output components and beneath the title in regular font. Accepts Markdown and HTML content.
            article: an expanded article explaining the interface; if provided, appears below the input and output components in regular font. Accepts Markdown and HTML content. If it is an HTTP(S) link to a downloadable remote file, the content of this file is displayed.
            theme: a Theme object or a string representing a theme. If a string, will look for a built-in theme with that name (e.g. "soft" or "default"), or will attempt to load a theme from the Hugging Face Hub (e.g. "gradio/monochrome"). If None, will use the Default theme.
            flagging_mode: one of "never", "auto", or "manual". If "never" or "auto", users will not see a button to flag an input and output. If "manual", users will see a button to flag. If "auto", every input the user submits will be automatically flagged, along with the generated output. If "manual", both the input and outputs are flagged when the user clicks flag button. This parameter can be set with environmental variable GRADIO_FLAGGING_MODE; otherwise defaults to "manual".
            flagging_options: if provided, allows user to select from the list of options when flagging. Only applies if flagging_mode is "manual". Can either be a list of tuples of the form (label, value), where label is the string that will be displayed on the button and value is the string that will be stored in the flagging CSV; or it can be a list of strings ["X", "Y"], in which case the values will be the list of strings and the labels will ["Flag as X", "Flag as Y"], etc.
            flagging_dir: path to the the directory where flagged data is stored. If the directory does not exist, it will be created.
            flagging_callback: either None or an instance of a subclass of FlaggingCallback which will be called when a sample is flagged. If set to None, an instance of gradio.flagging.CSVLogger will be created and logs will be saved to a local CSV file in flagging_dir. Default to None.
            analytics_enabled: whether to allow basic telemetry. If None, will use GRADIO_ANALYTICS_ENABLED environment variable if defined, or default to True.
            batch: if True, then the function should process a batch of inputs, meaning that it should accept a list of input values for each parameter. The lists should be of equal length (and be up to length `max_batch_size`). The function is then *required* to return a tuple of lists (even if there is only 1 output component), with each list in the tuple corresponding to one output component.
            max_batch_size: the maximum number of inputs to batch together if this is called from the queue (only relevant if batch=True)
            api_name: defines how the prediction endpoint appears in the API docs. Can be a string, None, or False. If set to a string, the endpoint will be exposed in the API docs with the given name. If None, the name of the prediction function will be used as the API endpoint. If False, the endpoint will not be exposed in the API docs and downstream apps (including those that `gr.load` this app) will not be able to use this prediction endpoint.
            allow_duplication: if True, then will show a 'Duplicate Spaces' button on Hugging Face Spaces.
            concurrency_limit: if set, this is the maximum number of this event that can be running simultaneously. Can be set to None to mean no concurrency_limit (any number of this event can be running simultaneously). Set to "default" to use the default concurrency limit (defined by the `default_concurrency_limit` parameter in `.queue()`, which itself is 1 by default).
            css: Custom css as a code string. This css will be included in the demo webpage.
            css_paths: Custom css as a pathlib.Path to a css file or a list of such paths. This css files will be read, concatenated, and included in the demo webpage. If the `css` parameter is also set, the css from `css` will be included first.
            js: Custom js as a code string. The custom js should be in the form of a single js function. This function will automatically be executed when the page loads. For more flexibility, use the head parameter to insert js inside <script> tags.
            head: Custom html code to insert into the head of the demo webpage. This can be used to add custom meta tags, multiple scripts, stylesheets, etc. to the page.
            head_paths: Custom html code as a pathlib.Path to a html file or a list of such paths. This html files will be read, concatenated, and included in the head of the demo webpage. If the `head` parameter is also set, the html from `head` will be included first.
            additional_inputs: a single Gradio component, or list of Gradio components. Components can either be passed as instantiated objects, or referred to by their string shortcuts. These components will be rendered in an accordion below the main input components. By default, no additional input components will be displayed.
            additional_inputs_accordion: if a string is provided, this is the label of the `gr.Accordion` to use to contain additional inputs. A `gr.Accordion` object can be provided as well to configure other properties of the container holding the additional inputs. Defaults to a `gr.Accordion(label="Additional Inputs", open=False)`. This parameter is only used if `additional_inputs` is provided.
            submit_btn: the button to use for submitting inputs. Defaults to a `gr.Button("Submit", variant="primary")`. This parameter does not apply if the Interface is output-only, in which case the submit button always displays "Generate". Can be set to a string (which becomes the button label) or a `gr.Button` object (which allows for more customization).
            stop_btn: the button to use for stopping the interface. Defaults to a `gr.Button("Stop", variant="stop", visible=False)`. Can be set to a string (which becomes the button label) or a `gr.Button` object (which allows for more customization).
            clear_btn: the button to use for clearing the inputs. Defaults to a `gr.Button("Clear", variant="secondary")`. Can be set to a string (which becomes the button label) or a `gr.Button` object (which allows for more customization). Can be set to None, which hides the button.
            delete_cache: a tuple corresponding [frequency, age] both expressed in number of seconds. Every `frequency` seconds, the temporary files created by this Blocks instance will be deleted if more than `age` seconds have passed since the file was created. For example, setting this to (86400, 86400) will delete temporary files every day. The cache will be deleted entirely when the server restarts. If None, no cache deletion will occur.
            show_progress: how to show the progress animation while event is running: "full" shows a spinner which covers the output component area as well as a runtime display in the upper right corner, "minimal" only shows the runtime display, "hidden" shows no progress animation at all
            example_labels: a list of labels for each example. If provided, the length of this list should be the same as the number of examples, and these labels will be used in the UI instead of rendering the example values.
            fill_width: whether to horizontally expand to fill container fully. If False, centers and constrains app to a maximum width.
            time_limit: The time limit for the stream to run. Default is 30 seconds. Parameter only used for streaming images or audio if the interface is live and the input components are set to "streaming=True".
            stream_every: The latency (in seconds) at which stream chunks are sent to the backend. Defaults to 0.5 seconds. Parameter only used for streaming images or audio if the interface is live and the input components are set to "streaming=True".
            deep_link: a string or `gr.DeepLinkButton` object that creates a unique URL you can use to share your app and all components **as they currently are** with others. Automatically enabled on Hugging Face Spaces unless explicitly set to False.
        """
        super().__init__(
            analytics_enabled=analytics_enabled,
            mode="interface",
            title=title or "Gradio",
            theme=theme,
            css=css,
            css_paths=css_paths,
            js=js,
            head=head,
            head_paths=head_paths,
            delete_cache=delete_cache,
            fill_width=fill_width,
            **kwargs,
        )
        if isinstance(deep_link, str):
            deep_link = DeepLinkButton(value=deep_link, render=False, interactive=False)
        elif deep_link is True:
            deep_link = DeepLinkButton(render=False, interactive=False)
        if utils.get_space() and deep_link is None:
            deep_link = DeepLinkButton(render=False, interactive=False)
        if wasm_utils.IS_WASM or deep_link is False:
            deep_link = None
        self.deep_link = deep_link
        self.time_limit = time_limit
        self.stream_every = stream_every
        self.api_name: str | Literal[False] | None = api_name
        self.interface_type = InterfaceTypes.STANDARD
        if (inputs is None or inputs == []) and (outputs is None or outputs == []):
            raise ValueError("Must provide at least one of `inputs` or `outputs`")
        elif outputs is None or outputs == []:
            outputs = []
            self.interface_type = InterfaceTypes.INPUT_ONLY
        elif inputs is None or inputs == []:
            inputs = []
            self.interface_type = InterfaceTypes.OUTPUT_ONLY
        if additional_inputs is None:
            self.additional_input_components = []
        else:
            if not isinstance(additional_inputs, Sequence):
                additional_inputs = [additional_inputs]
            self.additional_input_components = [
                get_component_instance(i, unrender=True) for i in additional_inputs
            ]

        if not isinstance(inputs, (Sequence, Component)):
            raise TypeError(
                f"inputs must be a string, list, or Component, not {inputs}"
            )
        if not isinstance(outputs, (Sequence, Component)):
            raise TypeError(
                f"outputs must be a string, list, or Component, not {outputs}"
            )

        if isinstance(inputs, (str, Component)):
            inputs = [inputs]
        if isinstance(outputs, (str, Component)):
            outputs = [outputs]

        self.cache_examples = cache_examples
        self.cache_mode: Literal["eager", "lazy"] | None = cache_mode
        self.preload_example = preload_example

        self.main_input_components = [
            get_component_instance(i, unrender=True) for i in inputs
        ]
        self.input_components = (
            self.main_input_components + self.additional_input_components
        )
        self.output_components = [
            get_component_instance(o, unrender=True)
            for o in outputs  # type: ignore
        ]

        state_input_indexes = [
            idx
            for idx, i in enumerate(self.input_components)
            if i == "state" or isinstance(i, State)
        ]
        state_output_indexes = [
            idx
            for idx, o in enumerate(self.output_components)
            if o == "state" or isinstance(o, State)
        ]

        if len(state_input_indexes) == 0 and len(state_output_indexes) == 0:
            pass
        elif len(state_input_indexes) != 1 or len(state_output_indexes) != 1:
            raise ValueError(
                "If using 'state', there must be exactly one state input and one state output."
            )
        else:
            state_input_index = state_input_indexes[0]
            state_output_index = state_output_indexes[0]
            if self.input_components[state_input_index] == "state":
                default = utils.get_default_args(fn)[state_input_index]
                state_variable = State(value=default)
            else:
                state_variable = self.input_components[state_input_index]

            self.input_components[state_input_index] = state_variable
            self.output_components[state_output_index] = state_variable

            if cache_examples:
                warnings.warn(
                    "Cache examples cannot be used with state inputs and outputs."
                    "Setting cache_examples to False."
                )
            self.cache_examples = False

        if additional_inputs_accordion is None:
            self.additional_inputs_accordion_params = {
                "label": "Additional Inputs",
                "open": False,
            }
        elif isinstance(additional_inputs_accordion, str):
            self.additional_inputs_accordion_params = {
                "label": additional_inputs_accordion
            }
        elif isinstance(additional_inputs_accordion, Accordion):
            self.additional_inputs_accordion_params = (
                additional_inputs_accordion.recover_kwargs(
                    additional_inputs_accordion.get_config()
                )
            )
        else:
            raise ValueError(
                f"The `additional_inputs_accordion` parameter must be a string or gr.Accordion, not {type(additional_inputs_accordion)}"
            )

        for component in self.input_components + self.output_components:
            if not (isinstance(component, Component)):
                raise ValueError(
                    f"{component} is not a valid input/output component for Interface."
                )

        if len(self.input_components) == len(self.output_components):
            same_components = [
                i is o
                for i, o in zip(
                    self.input_components, self.output_components, strict=False
                )
            ]
            if all(same_components):
                self.interface_type = InterfaceTypes.UNIFIED

        if self.interface_type in [
            InterfaceTypes.STANDARD,
            InterfaceTypes.OUTPUT_ONLY,
        ]:
            for o in self.output_components:
                if not isinstance(o, Component):
                    raise TypeError(
                        f"Output component must be a Component, not {type(o)}"
                    )
                if o.interactive is None:
                    # Unless explicitly otherwise specified, force output components to
                    # be non-interactive
                    o.interactive = False

        self.api_mode = _api_mode
        self.fn = fn
        self.fn_durations = [0, 0]
        self.__name__ = getattr(fn, "__name__", "fn")
        self.live = live
        self.title = title

        self.simple_description = utils.remove_html_tags(description)
        self.description = description
        if article is not None:
            article = utils.download_if_url(article)
        self.article = article

        self.examples = examples
        self.examples_per_page = examples_per_page
        self.example_labels = example_labels

        if isinstance(submit_btn, Button):
            self.submit_btn_parms = submit_btn.recover_kwargs(submit_btn.get_config())
        elif isinstance(submit_btn, str):
            self.submit_btn_parms = {
                "value": submit_btn,
                "variant": "primary",
            }
        else:
            raise ValueError(
                f"The submit_btn parameter must be a gr.Button or string, not {type(submit_btn)}"
            )

        if isinstance(stop_btn, Button):
            self.stop_btn_parms = stop_btn.recover_kwargs(stop_btn.get_config())
        elif isinstance(stop_btn, str):
            self.stop_btn_parms = {
                "value": stop_btn,
                "variant": "stop",
                "visible": False,
            }
        else:
            raise ValueError(
                f"The stop_btn parameter must be a gr.Button or string, not {type(stop_btn)}"
            )

        if clear_btn is None:
            self.clear_btn_params = {
                "visible": False,
                "variant": "secondary",
            }
        elif isinstance(clear_btn, Button):
            self.clear_btn_params = clear_btn.recover_kwargs(clear_btn.get_config())
        elif isinstance(clear_btn, str):
            self.clear_btn_params = {
                "value": clear_btn,
                "variant": "secondary",
            }
        else:
            raise ValueError(
                f"The clear_btn parameter must be a gr.Button, a string, or None, not {type(clear_btn)}"
            )

        self.simple_server = None

        # For flagging_mode: (1) first check for `flagging_mode` parameter (or its alias `allow_flagging`),
        # (2) check for env variable, (3) default to "manual"
        if allow_flagging is not None:
            warnings.warn(
                "The `allow_flagging` parameter in `Interface` is deprecated."
                "Use `flagging_mode` instead."
            )
            flagging_mode = allow_flagging
        if flagging_mode is None:
            self.flagging_mode = os.getenv("GRADIO_FLAGGING_MODE", "manual")
        elif flagging_mode in ["manual", "never", "auto"]:
            self.flagging_mode = flagging_mode
        else:
            raise ValueError(
                "Invalid value for `flagging_mode` parameter."
                "Must be: 'auto', 'manual', or 'never'."
            )

        if flagging_options is None:
            self.flagging_options = [("Flag", None)]
        elif not (isinstance(flagging_options, list)):
            raise ValueError(
                "flagging_options must be a list of strings or list of (string, string) tuples."
            )
        elif all(isinstance(x, str) for x in flagging_options):
            self.flagging_options = [(f"Flag as {x}", x) for x in flagging_options]
        elif all(isinstance(x, tuple) for x in flagging_options):
            self.flagging_options = flagging_options
        else:
            raise ValueError(
                "flagging_options must be a list of strings or list of (string, string) tuples."
            )

        if flagging_callback is None:
            flagging_callback = CSVLogger()

        self.flagging_callback = flagging_callback
        self.flagging_dir = flagging_dir
        self.show_progress: Literal["full", "hidden", "minimal"] = show_progress

        self.batch = batch
        self.max_batch_size = max_batch_size
        self.allow_duplication = allow_duplication
        self.concurrency_limit: int | None | Literal["default"] = concurrency_limit

        self.share = None
        self.share_url = None
        self.local_url = None

        self.favicon_path = None
        self.i18n_instance = None
        Interface.instances.add(self)

        param_types = utils.get_type_hints(self.fn)
        # param_names = inspect.getfullargspec(self.fn)[0]
        param_names = []
        try:
            param_names = inspect.getfullargspec(self.fn)[0]
            if len(param_names) > 0 and inspect.ismethod(self.fn):
                param_names = param_names[1:]
            for param_name in param_names.copy():
                if utils.is_special_typed_parameter(param_name, param_types):
                    param_names.remove(param_name)
        except (TypeError, ValueError):
            param_names = utils.default_input_labels()
        for component, param_name in zip(
            self.input_components, param_names, strict=False
        ):
            if not isinstance(component, Component):
                raise TypeError(
                    f"Input component must be a Component, not {type(component)}"
                )
            if component.label is None:
                component.label = param_name
        for i, component in enumerate(self.output_components):
            if not isinstance(component, Component):
                raise TypeError(
                    f"Output component must be a Component, not {type(component)}"
                )
            if component.label is None:
                if len(self.output_components) == 1:
                    component.label = "output"
                else:
                    component.label = f"output {i}"

        if self.flagging_mode != "never":
            if self.interface_type == InterfaceTypes.UNIFIED:
                self.flagging_callback.setup(self.input_components, self.flagging_dir)  # type: ignore
            elif self.interface_type == InterfaceTypes.INPUT_ONLY:
                pass
            else:
                self.flagging_callback.setup(
                    self.input_components + self.output_components,
                    self.flagging_dir,  # type: ignore
                )

        # Render the Gradio UI
        with self:
            if self.deep_link:
                self.deep_link.activate()
            self.render_title_description()

            _submit_btn, _clear_btn, _stop_btn, flag_btns, duplicate_btn = (
                None,
                None,
                None,
                None,
                None,
            )  # type: ignore
            input_component_column = None

            with Row():
                if self.interface_type in [
                    InterfaceTypes.STANDARD,
                    InterfaceTypes.INPUT_ONLY,
                    InterfaceTypes.UNIFIED,
                ]:
                    (
                        _submit_btn,
                        _clear_btn,
                        _stop_btn,
                        flag_btns,
                        input_component_column,
                    ) = self.render_input_column()  # type: ignore
                if self.interface_type in [
                    InterfaceTypes.STANDARD,
                    InterfaceTypes.OUTPUT_ONLY,
                ]:
                    (
                        _submit_btn_out,
                        _clear_btn_2_out,
                        duplicate_btn,
                        _stop_btn_2_out,
                        flag_btns_out,
                    ) = self.render_output_column(_submit_btn)
                    _submit_btn = _submit_btn or _submit_btn_out
                    _clear_btn = _clear_btn or _clear_btn_2_out
                    _stop_btn = _stop_btn or _stop_btn_2_out
                    flag_btns = flag_btns or flag_btns_out

            if _clear_btn is None:
                raise RenderError("Clear button not rendered")

            _submit_event = self.attach_submit_events(_submit_btn, _stop_btn)
            self.attach_clear_events(_clear_btn, input_component_column)
            if duplicate_btn is not None:
                duplicate_btn.activate()

            self.attach_flagging_events(flag_btns, _clear_btn, _submit_event)
            if _submit_event and self.deep_link:
                _submit_event.then(
                    lambda: DeepLinkButton(interactive=True),
                    inputs=None,
                    outputs=[self.deep_link],
                    js=True,
                    show_api=False,
                )
            self.render_examples()
            self.render_article()

        self.config = self.get_config_file()

    def render_title_description(self) -> None:
        if self.title:
            Markdown(
                f"<h1 style='text-align: center; margin-bottom: 1rem'>{self.title}</h1>"
            )
        if self.description:
            Markdown(self.description)

    def render_flag_btns(self) -> list[Button]:
        return [Button(label) for label, _ in self.flagging_options]

    def render_input_column(
        self,
    ) -> tuple[
        Button | None,
        ClearButton | None,
        Button | None,
        list[Button] | None,
        Column,
    ]:
        _submit_btn, _clear_btn, _stop_btn, flag_btns = None, None, None, None

        with Column():
            input_component_column = Column()
            with input_component_column:
                for component in self.main_input_components:
                    component.render()
                if self.additional_input_components:
                    with Accordion(**self.additional_inputs_accordion_params):  # type: ignore
                        for component in self.additional_input_components:
                            component.render()
            with Row():
                if self.interface_type in [
                    InterfaceTypes.STANDARD,
                    InterfaceTypes.INPUT_ONLY,
                ]:
                    _clear_btn = ClearButton(**self.clear_btn_params)  # type: ignore
                    if not self.live:
                        if (
                            self.deep_link
                            and self.interface_type == InterfaceTypes.INPUT_ONLY
                        ):
                            self.deep_link.render()
                        _submit_btn = Button(**self.submit_btn_parms)  # type: ignore
                        # Stopping jobs only works if the queue is enabled
                        # We don't know if the queue is enabled when the interface
                        # is created. We use whether a generator function is provided
                        # as a proxy of whether the queue will be enabled.
                        # Using a generator function without the queue will raise an error.
                        if inspect.isgeneratorfunction(
                            self.fn
                        ) or inspect.isasyncgenfunction(self.fn):
                            _stop_btn = Button(**self.stop_btn_parms)
                elif self.interface_type == InterfaceTypes.UNIFIED:
                    _clear_btn = ClearButton(**self.clear_btn_params)  # type: ignore
                    _submit_btn = Button(**self.submit_btn_parms)  # type: ignore
                    if self.deep_link:
                        self.deep_link.render()
                    if (
                        inspect.isgeneratorfunction(self.fn)
                        or inspect.isasyncgenfunction(self.fn)
                    ) and not self.live:
                        _stop_btn = Button(**self.stop_btn_parms)
                    if self.flagging_mode == "manual":
                        flag_btns = self.render_flag_btns()
                    elif self.flagging_mode == "auto":
                        flag_btns = [_submit_btn]
        return (
            _submit_btn,
            _clear_btn,
            _stop_btn,
            flag_btns,
            input_component_column,
        )

    def render_output_column(
        self,
        _submit_btn_in: Button | None,
    ) -> tuple[
        Button | None,
        ClearButton | None,
        DuplicateButton | None,
        Button | None,
        list | None,
    ]:
        _submit_btn = _submit_btn_in
        _clear_btn, duplicate_btn, flag_btns, _stop_btn = (
            None,
            None,
            None,
            None,
        )

        with Column():
            for component in self.output_components:
                if not (isinstance(component, State)):
                    component.render()
            with Row():
                if self.deep_link:
                    self.deep_link.render()
                if self.interface_type == InterfaceTypes.OUTPUT_ONLY:
                    _clear_btn = ClearButton(**self.clear_btn_params)  # type: ignore
                    _submit_btn = Button("Generate", variant="primary")
                    if (
                        inspect.isgeneratorfunction(self.fn)
                        or inspect.isasyncgenfunction(self.fn)
                    ) and not self.live:
                        # Stopping jobs only works if the queue is enabled
                        # We don't know if the queue is enabled when the interface
                        # is created. We use whether a generator function is provided
                        # as a proxy of whether the queue will be enabled.
                        # Using a generator function without the queue will raise an error.
                        _stop_btn = Button(**self.stop_btn_parms)
                if self.flagging_mode == "manual":
                    flag_btns = self.render_flag_btns()
                elif self.flagging_mode == "auto":
                    if _submit_btn is None:
                        raise RenderError("Submit button not rendered")
                    flag_btns = [_submit_btn]

                if self.allow_duplication:
                    duplicate_btn = DuplicateButton(scale=1, size="lg", _activate=False)

        return (
            _submit_btn,
            _clear_btn,
            duplicate_btn,
            _stop_btn,
            flag_btns,
        )

    def render_article(self):
        if self.article:
            Markdown(self.article)

    def attach_submit_events(
        self, _submit_btn: Button | None, _stop_btn: Button | None
    ) -> Dependency:
        if self.live:
            if self.interface_type == InterfaceTypes.OUTPUT_ONLY:
                if _submit_btn is None:
                    raise RenderError("Submit button not rendered")
                super().load(self.fn, None, self.output_components)
                # For output-only interfaces, the user probably still want a "generate"
                # button even if the Interface is live
                return _submit_btn.click(
                    self.fn,
                    None,
                    self.output_components,
                    api_name=self.api_name,
                    preprocess=not (self.api_mode),
                    postprocess=not (self.api_mode),
                    batch=self.batch,
                    max_batch_size=self.max_batch_size,
                )
            else:
                events: list[Callable] = []
                streaming_event = False
                for component in self.input_components:
                    if component.has_event("stream") and component.streaming:  # type: ignore
                        events.append(component.stream)  # type: ignore
                        streaming_event = True
                    elif component.has_event("change"):
                        events.append(component.change)  # type: ignore
                return on(
                    events,
                    self.fn,
                    self.input_components,
                    self.output_components,
                    api_name=self.api_name,
                    preprocess=not (self.api_mode),
                    postprocess=not (self.api_mode),
                    show_progress="hidden" if streaming_event else self.show_progress,
                    trigger_mode="always_last" if not streaming_event else "multiple",
                    time_limit=self.time_limit,
                    stream_every=self.stream_every,
                )
        else:
            if _submit_btn is None:
                raise RenderError("Submit button not rendered")
            fn = self.fn
            extra_output = []

            triggers = [_submit_btn.click] + [
                component.submit  # type: ignore
                for component in self.input_components
                if component.has_event(Events.submit)
            ]

            for component in self.input_components:
                if getattr(component, "streaming", None):
                    warnings.warn(
                        "Streaming components are only supported in live interfaces."
                    )

            if _stop_btn:
                extra_output = [_submit_btn, _stop_btn]

                async def cleanup():
                    return [Button(visible=True), Button(visible=False)]

                predict_event = on(
                    triggers,
                    utils.async_lambda(
                        lambda: (
                            Button(visible=False),
                            Button(visible=True),
                        )
                    ),
                    inputs=None,
                    outputs=[_submit_btn, _stop_btn],
                    queue=False,
                    show_api=False,
                ).then(
                    self.fn,
                    self.input_components,
                    self.output_components,
                    api_name=self.api_name,
                    scroll_to_output=True,
                    preprocess=not (self.api_mode),
                    postprocess=not (self.api_mode),
                    batch=self.batch,
                    max_batch_size=self.max_batch_size,
                    concurrency_limit=self.concurrency_limit,
                    show_progress=self.show_progress,
                )

                final_event = predict_event.then(
                    cleanup,
                    inputs=None,
                    outputs=extra_output,  # type: ignore
                    queue=False,
                    show_api=False,
                )

                _stop_btn.click(
                    cleanup,
                    inputs=None,
                    outputs=[_submit_btn, _stop_btn],
                    cancels=predict_event,
                    queue=False,
                    show_api=False,
                )
                return final_event
            else:
                return on(
                    triggers,
                    fn,
                    self.input_components,
                    self.output_components,
                    api_name=self.api_name,
                    scroll_to_output=True,
                    preprocess=not (self.api_mode),
                    postprocess=not (self.api_mode),
                    batch=self.batch,
                    max_batch_size=self.max_batch_size,
                    concurrency_limit=self.concurrency_limit,
                    show_progress=self.show_progress,
                )

    def attach_clear_events(
        self,
        _clear_btn: ClearButton,
        input_component_column: Column | None,
    ):
        _clear_btn.add(self.input_components + self.output_components)
        _clear_btn.click(
            None,
            [],
            ([input_component_column] if input_component_column else []),  # type: ignore
            js=f"""() => {
                json.dumps(
                    [{"variant": None, "visible": True, "__type__": "update"}]
                    if self.interface_type
                    in [
                        InterfaceTypes.STANDARD,
                        InterfaceTypes.INPUT_ONLY,
                        InterfaceTypes.UNIFIED,
                    ]
                    else []
                )
            }
            """,
        )

    def attach_flagging_events(
        self,
        flag_btns: list[Button] | None,
        _clear_btn: ClearButton,
        _submit_event: Dependency,
    ):
        if not (
            flag_btns
            and self.interface_type
            in (
                InterfaceTypes.STANDARD,
                InterfaceTypes.OUTPUT_ONLY,
                InterfaceTypes.UNIFIED,
            )
        ):
            return

        if self.flagging_mode == "auto":
            flag_method = FlagMethod(
                self.flagging_callback, "", None, visual_feedback=False
            )
            _submit_event.success(
                flag_method,
                inputs=self.input_components + self.output_components,
                outputs=None,
                preprocess=False,
                queue=False,
                show_api=False,
            )
            return

        if self.interface_type == InterfaceTypes.UNIFIED:
            flag_components = self.input_components
        else:
            flag_components = self.input_components + self.output_components

        for flag_btn, (label, value) in zip(
            flag_btns, self.flagging_options, strict=False
        ):
            if value is not None and not isinstance(value, str):
                raise TypeError(
                    f"Flagging option value must be a string, not {value!r}"
                )
            flag_method = FlagMethod(self.flagging_callback, label, value)
            flag_btn.click(
                utils.async_lambda(
                    lambda: Button(value="Saving...", interactive=False)
                ),
                None,
                flag_btn,
                queue=False,
                show_api=False,
            )
            flag_btn.click(
                flag_method,
                inputs=flag_components,
                outputs=flag_btn,
                preprocess=False,
                queue=False,
                show_api=False,
            )
            _clear_btn.click(
                utils.async_lambda(flag_method.reset),
                None,
                flag_btn,
                queue=False,
                show_api=False,
            )

    def render_examples(self):
        if self.examples:
            non_state_inputs = [
                c for c in self.input_components if not isinstance(c, State)
            ]
            non_state_outputs = [
                c for c in self.output_components if not isinstance(c, State)
            ]
            self.examples_handler = Examples(
                examples=self.examples,
                inputs=non_state_inputs,
                outputs=non_state_outputs,
                fn=self.fn,
                cache_examples=self.cache_examples,
                cache_mode=self.cache_mode,
                examples_per_page=self.examples_per_page,
                _api_mode=self.api_mode,
                batch=self.batch,
                example_labels=self.example_labels,
                preload=self.preload_example,
            )
            if self.deep_link and self.examples_handler.cache_event:
                self.examples_handler.cache_event.then(
                    lambda: DeepLinkButton(interactive=True),
                    inputs=None,
                    outputs=[self.deep_link],
                    js=True,
                    show_api=False,
                )

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        repr = f"Gradio Interface for: {self.__name__}"
        repr += f"\n{'-' * len(repr)}"
        repr += "\ninputs:"
        for component in self.input_components:
            repr += f"\n|-{component}"
        repr += "\noutputs:"
        for component in self.output_components:
            repr += f"\n|-{component}"
        return repr


@document()
class TabbedInterface(Blocks):
    """
    A TabbedInterface is created by providing a list of Interfaces or Blocks, each of which gets
    rendered in a separate tab. Only the components from the Interface/Blocks will be rendered in the tab.
    Certain high-level attributes of the Blocks (e.g. custom `css`, `js`, and `head` attributes) will not be loaded.

    Demos: tabbed_interface_lite
    """

    def __init__(
        self,
        interface_list: Sequence[Blocks],
        tab_names: list[str] | None = None,
        title: str | None = None,
        theme: Theme | str | None = None,
        analytics_enabled: bool | None = None,
        css: str | None = None,
        js: str | Literal[True] | None = None,
        head: str | None = None,
    ):
        """
        Parameters:
            interface_list: A list of Interfaces (or Blocks) to be rendered in the tabs.
            tab_names: A list of tab names. If None, the tab names will be "Tab 1", "Tab 2", etc.
            title: The tab title to display when this demo is opened in a browser window.
            theme: A Theme object or a string representing a theme. If a string, will look for a built-in theme with that name (e.g. "soft" or "default"), or will attempt to load a theme from the Hugging Face Hub (e.g. "gradio/monochrome"). If None, will use the Default theme.
            analytics_enabled: Whether to allow basic telemetry. If None, will use GRADIO_ANALYTICS_ENABLED environment variable or default to True.
            css: Custom css as a string or path to a css file. This css will be included in the demo webpage.
            js: Custom js as a string or path to a js file. The custom js should in the form of a single js function. This function will automatically be executed when the page loads. For more flexibility, use the head parameter to insert js inside <script> tags.
            head: Custom html to insert into the head of the demo webpage. This can be used to add custom meta tags, multiple scripts, stylesheets, etc. to the page.
        Returns:
            a Gradio Tabbed Interface for the given interfaces
        """
        super().__init__(
            title=title or "Gradio",
            theme=theme,
            analytics_enabled=analytics_enabled,
            mode="tabbed_interface",
            css=css,
            js=js,
            head=head,
            fill_height=True,
        )
        if tab_names is None:
            tab_names = [f"Tab {i}" for i in range(len(interface_list))]
        with self:
            if title:
                Markdown(
                    f"<h1 style='text-align: center; margin-bottom: 1rem'>{title}</h1>"
                )
            with Tabs():
                for interface, tab_name in zip(interface_list, tab_names, strict=False):
                    with Tab(
                        label=tab_name,
                        scale=1 if interface.fill_height else None,
                    ):
                        interface.render()


def close_all(verbose: bool = True) -> None:
    for io in Interface.get_instances():
        io.close(verbose)


=== File: gradio/layouts/accordion.py ===
from __future__ import annotations

from typing import TYPE_CHECKING

from gradio_client.documentation import document

from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    pass


@document()
class Accordion(BlockContext, metaclass=ComponentMeta):
    """
    Accordion is a layout element which can be toggled to show/hide the contained content.
    Example:
        with gr.Accordion("See Details"):
            gr.Markdown("lorem ipsum")
    """

    EVENTS = [Events.expand, Events.collapse]

    def __init__(
        self,
        label: str | I18nData | None = None,
        *,
        open: bool = True,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            label: name of accordion section.
            open: if True, accordion is open by default.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.label = label
        self.open = open
        BlockContext.__init__(
            self,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )


=== File: gradio/layouts/column.py ===
from __future__ import annotations

import warnings
from typing import Literal

from gradio_client.documentation import document

from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta


@document()
class Column(BlockContext, metaclass=ComponentMeta):
    """
    Column is a layout element within Blocks that renders all children vertically. The widths of columns can be set through the `scale` and `min_width` parameters.
    If a certain scale results in a column narrower than min_width, the min_width parameter will win.
    Example:
        with gr.Blocks() as demo:
            with gr.Row():
                with gr.Column(scale=1):
                    text1 = gr.Textbox()
                    text2 = gr.Textbox()
                with gr.Column(scale=4):
                    btn1 = gr.Button("Button 1")
                    btn2 = gr.Button("Button 2")
    Guides: controlling-layout
    """

    EVENTS = []

    def __init__(
        self,
        *,
        scale: int = 1,
        min_width: int = 320,
        variant: Literal["default", "panel", "compact"] = "default",
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        show_progress: bool = False,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            scale: relative width compared to adjacent Columns. For example, if Column A has scale=2, and Column B has scale=1, A will be twice as wide as B.
            min_width: minimum pixel width of Column, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in a column narrower than min_width, the min_width parameter will be respected first.
            variant: column type, 'default' (no background), 'panel' (gray background color and rounded corners), or 'compact' (rounded corners and no internal gap).
            visible: If False, column will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            show_progress: If True, shows progress animation when being updated.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        if scale != round(scale):
            warnings.warn(
                f"'scale' value should be an integer. Using {scale} will cause issues."
            )

        self.scale = scale
        self.min_width = min_width
        self.variant = variant
        if variant == "compact":
            self.allow_expected_parents = False
        self.show_progress = show_progress
        BlockContext.__init__(
            self,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )


=== File: gradio/layouts/form.py ===
from __future__ import annotations

from typing import TYPE_CHECKING

from gradio.blocks import BlockContext, Blocks
from gradio.component_meta import ComponentMeta
from gradio.layouts.column import Column
from gradio.layouts.row import Row

if TYPE_CHECKING:
    from gradio.blocks import Block


class Form(BlockContext, metaclass=ComponentMeta):
    EVENTS = []

    def __init__(
        self,
        *,
        scale: int = 0,
        min_width: int = 0,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            scale: relative width compared to adjacent Columns. For example, if Column A has scale=2, and Column B has scale=1, A will be twice as wide as B.
            min_width: minimum pixel width of Column, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in a column narrower than min_width, the min_width parameter will be respected first.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.scale = scale
        self.min_width = min_width
        BlockContext.__init__(
            self,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )

    def add_child(self, child: Block):
        if isinstance(self.parent, Row):
            scale = getattr(child, "scale", None)
            self.scale += 1 if scale is None else scale
            self.min_width += getattr(child, "min_width", 0) or 0
        elif (
            isinstance(self.parent, Column)
            and isinstance(self.parent.parent, Row)
            and self.parent.parent.equal_height
        ):
            scale = getattr(child, "scale", None)
            self.scale += 1 if scale is None else scale
        elif isinstance(self.parent, Blocks) and self.parent.fill_height:
            scale = getattr(child, "scale", None)
            self.scale += 0 if scale is None else scale
        BlockContext.add_child(self, child)


=== File: gradio/layouts/group.py ===
from __future__ import annotations

from gradio_client.documentation import document

from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta


@document()
class Group(BlockContext, metaclass=ComponentMeta):
    """
    Group is a layout element within Blocks which groups together children so that
    they do not have any padding or margin between them.
    Example:
        with gr.Group():
            gr.Textbox(label="First")
            gr.Textbox(label="Last")
    """

    EVENTS = []

    def __init__(
        self,
        *,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            visible: If False, group will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        BlockContext.__init__(
            self,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )


=== File: gradio/layouts/row.py ===
from __future__ import annotations

import warnings
from typing import Literal

from gradio_client.documentation import document

from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta


@document()
class Row(BlockContext, metaclass=ComponentMeta):
    """
    Row is a layout element within Blocks that renders all children horizontally.
    Example:
        with gr.Blocks() as demo:
            with gr.Row():
                gr.Image("lion.jpg", scale=2)
                gr.Image("tiger.jpg", scale=1)
        demo.launch()
    Guides: controlling-layout
    """

    EVENTS = []

    def __init__(
        self,
        *,
        variant: Literal["default", "panel", "compact"] = "default",
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        scale: int | None = None,
        render: bool = True,
        height: int | str | None = None,
        max_height: int | str | None = None,
        min_height: int | str | None = None,
        equal_height: bool = False,
        show_progress: bool = False,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            variant: row type, 'default' (no background), 'panel' (gray background color and rounded corners), or 'compact' (rounded corners and no internal gap).
            visible: If False, row will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            scale: relative height compared to adjacent elements. 1 or greater indicates the Row will expand in height, and any child columns will also expand to fill the height.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            height: The height of the row, specified in pixels if a number is passed, or in CSS units if a string is passed. If content exceeds the height, the row will scroll vertically. If not set, the row will expand to fit the content.
            max_height: The maximum height of the row, specified in pixels if a number is passed, or in CSS units if a string is passed. If content exceeds the height, the row will scroll vertically. If content is shorter than the height, the row will shrink to fit the content. Will not have any effect if `height` is set and is smaller than `max_height`.
            min_height: The minimum height of the row, specified in pixels if a number is passed, or in CSS units if a string is passed. If content exceeds the height, the row will expand to fit the content. Will not have any effect if `height` is set and is larger than `min_height`.
            equal_height: If True, makes every child element have equal height
            show_progress: If True, shows progress animation when being updated.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.variant = variant
        self.equal_height = equal_height
        if variant == "compact":
            self.allow_expected_parents = False
        self.show_progress = show_progress
        self.height = height
        self.max_height = max_height
        self.min_height = min_height
        if scale and scale != round(scale):
            warnings.warn(
                f"'scale' value should be an integer. Using {scale} will cause issues."
            )

        self.scale = scale

        BlockContext.__init__(
            self,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )

    @staticmethod
    def update(
        visible: bool | None = None,
    ):
        return {
            "visible": visible,
            "__type__": "update",
        }


=== File: gradio/layouts/sidebar.py ===
from __future__ import annotations

from typing import Literal

from gradio_client.documentation import document

from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta
from gradio.events import Events
from gradio.i18n import I18nData


@document()
class Sidebar(BlockContext, metaclass=ComponentMeta):
    """
    Sidebar is a collapsible panel that renders child components on the left side of the screen within a Blocks layout.
    Example:
        with gr.Blocks() as demo:
            with gr.Sidebar():
                gr.Textbox()
                gr.Button()
    Guides: controlling-layout
    """

    EVENTS = [Events.expand, Events.collapse]

    def __init__(
        self,
        label: str | I18nData | None = None,
        *,
        open: bool = True,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        width: int | str = 320,
        position: Literal["left", "right"] = "left",
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            label: name of the sidebar. Not displayed to the user.
            open: if True, sidebar is open by default.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            width: The width of the sidebar, specified in pixels if a number is passed, or in CSS units if a string is passed.
            position: The position of the sidebar in the layout, either "left" or "right". Defaults to "left".
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.label = label
        self.open = open
        self.width = width
        self.position = position
        BlockContext.__init__(
            self,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )


=== File: gradio/layouts/tabs.py ===
from __future__ import annotations

from gradio_client.documentation import document

from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta
from gradio.events import Events
from gradio.i18n import I18nData


class Tabs(BlockContext, metaclass=ComponentMeta):
    """
    Tabs is a layout element within Blocks that can contain multiple "Tab" Components.
    """

    EVENTS = [Events.change, Events.select]

    def __init__(
        self,
        *,
        selected: int | str | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            selected: The currently selected tab. Must correspond to an id passed to the one of the child TabItems. Defaults to the first TabItem.
            visible: If False, Tabs will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        BlockContext.__init__(
            self,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )
        self.selected = selected


@document()
class Tab(BlockContext, metaclass=ComponentMeta):
    """
    Tab (or its alias TabItem) is a layout element. Components defined within the Tab will be visible when this tab is selected tab.
    Example:
        with gr.Blocks() as demo:
            with gr.Tab("Lion"):
                gr.Image("lion.jpg")
                gr.Button("New Lion")
            with gr.Tab("Tiger"):
                gr.Image("tiger.jpg")
                gr.Button("New Tiger")
    Guides: controlling-layout
    """

    EVENTS = [Events.select]

    def __init__(
        self,
        label: str | I18nData | None = None,
        visible: bool = True,
        interactive: bool = True,
        *,
        id: int | str | None = None,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        scale: int | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            label: The visual label for the tab
            id: An optional identifier for the tab, required if you wish to control the selected tab from a predict function.
            elem_id: An optional string that is assigned as the id of the <div> containing the contents of the Tab layout. The same string followed by "-button" is attached to the Tab button. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            scale: relative size compared to adjacent elements. 1 or greater indicates the Tab will expand in size.
            visible: If False, Tab will be hidden.
            interactive: If False, Tab will not be clickable.
        """
        BlockContext.__init__(
            self,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )
        self.label = label
        self.id = id
        self.visible = visible
        self.scale = scale
        self.interactive = interactive

    def get_expected_parent(self) -> type[Tabs]:
        return Tabs

    def get_block_name(self):
        return "tabitem"


TabItem = Tab

