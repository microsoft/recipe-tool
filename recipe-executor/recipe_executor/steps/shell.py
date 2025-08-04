# Shell execution step for recipe-executor
import asyncio
import logging
import os
from typing import Any, Dict, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.utils.templates import render_template


class ShellConfig(StepConfig):
    """
    Configuration for ShellStep.

    Fields:
        command: The shell command to execute (supports template variables)
        working_dir: Optional working directory for command execution
        env: Optional environment variables to set
        capture_output: Whether to capture stdout/stderr (default: True)
        output_key: Optional key to store the command output in context
        error_key: Optional key to store error output in context
        timeout: Optional timeout in seconds for command execution
    """

    command: str
    working_dir: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    capture_output: bool = True
    output_key: Optional[str] = None
    error_key: Optional[str] = None
    timeout: Optional[float] = None


class ShellStep(BaseStep[ShellConfig]):
    """
    Step that executes shell commands.
    """

    def __init__(
        self,
        logger: logging.Logger,
        config: Dict[str, Any],
    ) -> None:
        config_model = ShellConfig.model_validate(config)
        super().__init__(logger, config_model)

    async def execute(self, context: ContextProtocol) -> None:
        """Execute the shell command."""
        # Render the command with template variables
        command = render_template(self.config.command, context)
        self.logger.info(f"Executing shell command: {command}")

        # Render working directory if provided
        working_dir = None
        if self.config.working_dir:
            working_dir = render_template(self.config.working_dir, context)
            working_dir = os.path.expanduser(working_dir)
            self.logger.debug(f"Working directory: {working_dir}")

        # Prepare environment variables
        env = os.environ.copy()
        if self.config.env:
            for key, value in self.config.env.items():
                env[key] = render_template(value, context)

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if self.config.capture_output else None,
                stderr=asyncio.subprocess.PIPE if self.config.capture_output else None,
                cwd=working_dir,
                env=env,
            )

            # Wait for completion with optional timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.config.timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(f"Command timed out after {self.config.timeout} seconds")

            # Decode output if captured
            if self.config.capture_output:
                stdout_text = stdout.decode("utf-8", errors="replace") if stdout else ""
                stderr_text = stderr.decode("utf-8", errors="replace") if stderr else ""

                # Log output
                if stdout_text:
                    self.logger.debug(f"Command stdout: {stdout_text}")
                if stderr_text:
                    self.logger.debug(f"Command stderr: {stderr_text}")

                # Store output in context if requested
                if self.config.output_key and stdout_text:
                    context[self.config.output_key] = stdout_text.strip()
                if self.config.error_key and stderr_text:
                    context[self.config.error_key] = stderr_text.strip()

            # Check return code
            if process.returncode != 0:
                error_msg = f"Command failed with exit code {process.returncode}"
                if self.config.capture_output and stderr_text:
                    error_msg += f": {stderr_text}"
                raise RuntimeError(error_msg)

            self.logger.info("Shell command completed successfully")

        except Exception as e:
            self.logger.error(f"Shell command failed: {e}")
            raise


# Register the step
STEP_REGISTRY["shell"] = ShellStep
