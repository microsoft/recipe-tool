import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template

__all__ = ["LoopStep", "LoopStepConfig"]


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.
    """

    items: Union[str, List[Any], Dict[Any, Any]]
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    """
    LoopStep: iterate over a collection, execute substeps for each item.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        # Validate configuration via Pydantic
        validated = LoopStepConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        # Delay import to avoid circular dependency
        from recipe_executor.executor import Executor  # type: ignore

        # Resolve the items definition
        items_def = self.config.items
        if isinstance(items_def, str):
            rendered = render_template(items_def, context)
            items_obj: Any = _resolve_path(rendered, context)
        else:
            items_obj = items_def

        # Validate existence and type of items
        if items_obj is None:
            raise ValueError(f"LoopStep: Items '{items_def}' not found in context.")
        if not isinstance(items_obj, (list, dict)):
            raise ValueError(f"LoopStep: Items must be a list or dict, got {type(items_obj).__name__}.")

        # Flatten items into list of (key, value)
        if isinstance(items_obj, list):
            items_list: List[Tuple[Any, Any]] = [(_idx, _val) for _idx, _val in enumerate(items_obj)]
        else:
            items_list = list(items_obj.items())

        total = len(items_list)
        max_c = self.config.max_concurrency
        self.logger.info(f"LoopStep: Processing {total} items with max_concurrency={max_c}.")

        # Handle empty collection
        if total == 0:
            empty: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
            context[self.config.result_key] = empty
            self.logger.info("LoopStep: No items to process.")
            return

        # Prepare result and error placeholders
        results: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
        errors: Union[List[Dict[str, Any]], Dict[Any, Dict[str, Any]]] = [] if isinstance(items_obj, list) else {}

        # Concurrency control: None => unlimited, else semaphore
        semaphore: Optional[asyncio.Semaphore]
        if max_c == 0:
            semaphore = None
        else:
            semaphore = asyncio.Semaphore(max_c) if max_c > 0 else None

        # Executor for running sub-steps
        step_executor: ExecutorProtocol = Executor(self.logger)
        recipe_body: Dict[str, Any] = {"steps": self.config.substeps}

        fail_fast_triggered = False
        completed = 0
        tasks: List[asyncio.Task[Tuple[Any, Any, Optional[str]]]] = []

        async def process_one(key: Any, val: Any) -> Tuple[Any, Any, Optional[str]]:
            # Clone context for isolation
            item_ctx = context.clone()
            # Set current item and metadata
            item_ctx[self.config.item_key] = val
            if isinstance(items_obj, list):
                item_ctx["__index"] = key
            else:
                item_ctx["__key"] = key
            try:
                self.logger.debug(f"LoopStep: Starting item {key}.")
                await step_executor.execute(recipe_body, item_ctx)
                # Extract result: prefer updated item_key or fallback to original
                out = item_ctx.get(self.config.item_key, val)
                self.logger.debug(f"LoopStep: Finished item {key}.")
                return key, out, None
            except Exception as e:
                msg = str(e)
                self.logger.error(f"LoopStep: Error on item {key}: {msg}")
                return key, None, msg

        async def sequential() -> None:
            nonlocal fail_fast_triggered, completed
            for k, v in items_list:
                if fail_fast_triggered:
                    break
                idx, out, err = await process_one(k, v)
                if err:
                    # Record error
                    if isinstance(errors, list):
                        errors.append({"index": idx, "error": err})
                    else:
                        errors[idx] = {"error": err}
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break
                else:
                    # Record success
                    if isinstance(results, list):
                        results.append(out)
                    else:
                        results[idx] = out
                    completed += 1

        async def parallel() -> None:
            nonlocal fail_fast_triggered, completed

            async def worker(k: Any, v: Any) -> Tuple[Any, Any, Optional[str]]:
                if semaphore:
                    async with semaphore:
                        return await process_one(k, v)
                return await process_one(k, v)

            # Schedule tasks with optional delay for staggering
            for idx, (k, v) in enumerate(items_list):
                if fail_fast_triggered:
                    break
                tasks.append(asyncio.create_task(worker(k, v)))
                if self.config.delay and idx < total - 1:
                    await asyncio.sleep(self.config.delay)

            # Collect task results as they complete
            for task in asyncio.as_completed(tasks):  # type: ignore
                if fail_fast_triggered:
                    break
                try:
                    k, out, err = await task  # type: ignore
                    if err:
                        if isinstance(errors, list):
                            errors.append({"index": k, "error": err})
                        else:
                            errors[k] = {"error": err}
                        if self.config.fail_fast:
                            fail_fast_triggered = True
                            continue
                    else:
                        if isinstance(results, list):
                            results.append(out)
                        else:
                            results[k] = out
                        completed += 1
                except Exception as e:
                    self.logger.error(f"LoopStep: Unexpected error: {e}")
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break

        # Choose execution mode
        if max_c == 1:
            await sequential()
        else:
            await parallel()

        # Store results and errors in parent context
        context[self.config.result_key] = results
        if errors:
            context[f"{self.config.result_key}__errors"] = errors

        error_count = len(errors) if isinstance(errors, (list, dict)) else 0
        self.logger.info(f"LoopStep: Completed {completed}/{total} items. Errors: {error_count}.")


def _resolve_path(path: str, context: ContextProtocol) -> Any:
    """
    Resolve a dot-notated path against the context or nested dicts.
    """
    current: Any = context
    for part in path.split("."):
        if isinstance(current, ContextProtocol):
            current = current.get(part, None)
        elif isinstance(current, dict):
            current = current.get(part, None)
        else:
            return None
        if current is None:
            return None
    return current
