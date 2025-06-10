import asyncio
import logging
from typing import Any, Dict, List, Optional, Set

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.protocols import ContextProtocol, StepProtocol


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step definitions, each a dict with 'type' and 'config'.
        max_concurrency: Maximum number of substeps to run concurrently. 0 means unlimited.
        delay: Optional delay (in seconds) between launching each substep.
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """Step to execute multiple sub-steps in parallel."""

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        substeps: List[Dict[str, Any]] = self.config.substeps or []
        total: int = len(substeps)
        max_conc: int = self.config.max_concurrency
        delay: float = self.config.delay

        self.logger.info(f"Starting ParallelStep: {total} substeps, max_concurrency={max_conc}, delay={delay}")

        if total == 0:
            self.logger.info("ParallelStep has no substeps to execute. Skipping.")
            return

        # Determine concurrency limit
        concurrency: int = max_conc if max_conc > 0 else total
        semaphore: asyncio.Semaphore = asyncio.Semaphore(concurrency)

        # Holder for first failure
        failure: Dict[str, Optional[Any]] = {"exc": None, "idx": None}
        tasks: List[asyncio.Task] = []

        async def run_substep(idx: int, spec: Dict[str, Any]) -> None:
            sub_logger = self.logger.getChild(f"substep_{idx}")
            try:
                sub_logger.debug(f"Cloning context and preparing substep {idx} ({spec.get('type')})")
                sub_context = context.clone()

                step_type = spec.get("type")
                step_cfg = spec.get("config", {})
                if not step_type or step_type not in STEP_REGISTRY:
                    raise RuntimeError(f"Unknown or missing step type '{step_type}' for substep {idx}")
                StepClass = STEP_REGISTRY[step_type]
                step_instance: StepProtocol = StepClass(sub_logger, step_cfg)

                sub_logger.info(f"Launching substep {idx} of type '{step_type}'")
                await step_instance.execute(sub_context)
                sub_logger.info(f"Substep {idx} completed successfully")

            except Exception as exc:
                # Record first exception
                if failure["exc"] is None:
                    failure["exc"] = exc
                    failure["idx"] = idx
                sub_logger.error(f"Substep {idx} failed: {exc}", exc_info=True)
                raise

            finally:
                semaphore.release()

        # Launch substeps with concurrency control and optional delay
        for idx, spec in enumerate(substeps):
            if failure["exc"]:
                self.logger.debug(f"Fail-fast: aborting launch of remaining substeps at index {idx}")
                break

            await semaphore.acquire()
            if delay > 0:
                await asyncio.sleep(delay)

            task = asyncio.create_task(run_substep(idx, spec))
            tasks.append(task)

        if not tasks:
            self.logger.info("No substeps were launched. Nothing to wait for.")
            return

        # Wait for first exception or all to finish
        done: Set[asyncio.Task] = set()
        pending: Set[asyncio.Task] = set()
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        except Exception:
            # Should not happen; tasks errors handled below
            pass

        if failure["exc"]:
            failed_idx: Optional[int] = failure.get("idx")
            self.logger.error(f"A substep failed at index {failed_idx}; cancelling remaining tasks")
            for p in pending:
                p.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            raise RuntimeError(f"ParallelStep aborted due to failure in substep {failed_idx}") from failure["exc"]

        # All succeeded; ensure finalization
        await asyncio.gather(*done)
        success_count: int = len(done)
        self.logger.info(f"Completed ParallelStep: {success_count}/{total} substeps succeeded")
