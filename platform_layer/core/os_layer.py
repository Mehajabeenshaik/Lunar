"""OS System Layer - Direct OS interactions and resource management."""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SystemResource:
    """System resource information."""
    cpu_count: int
    memory_mb: int
    disk_free_mb: int
    python_version: str
    os_platform: str


@dataclass
class ProcessResult:
    """Result from process execution."""
    exit_code: int
    stdout: str
    stderr: str
    command: str


class OSLayer:
    """Direct OS interactions layer."""

    @staticmethod
    def get_system_info() -> SystemResource:
        """Get system resource information."""
        import psutil
        
        return SystemResource(
            cpu_count=psutil.cpu_count(),
            memory_mb=int(psutil.virtual_memory().total / (1024 ** 2)),
            disk_free_mb=int(psutil.disk_usage('/').free / (1024 ** 2)),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            os_platform=sys.platform,
        )

    @staticmethod
    def run_command(
        cmd: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300,
    ) -> ProcessResult:
        """Run OS command and capture output."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env={**os.environ, **(env or {})},
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return ProcessResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=" ".join(cmd),
            )
        except subprocess.TimeoutExpired as e:
            return ProcessResult(
                exit_code=124,
                stdout="",
                stderr=f"Command timeout after {timeout}s: {e}",
                command=" ".join(cmd),
            )
        except Exception as e:
            return ProcessResult(
                exit_code=1,
                stdout="",
                stderr=f"Command failed: {e}",
                command=" ".join(cmd),
            )

    @staticmethod
    def create_directory(path: str, exist_ok: bool = True) -> bool:
        """Create directory."""
        try:
            Path(path).mkdir(parents=True, exist_ok=exist_ok)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False

    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """Copy file."""
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Failed to copy {src} to {dst}: {e}")
            return False

    @staticmethod
    def copy_tree(src: str, dst: str) -> bool:
        """Copy directory tree."""
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            return True
        except Exception as e:
            logger.error(f"Failed to copy tree {src} to {dst}: {e}")
            return False

    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(path)

    @staticmethod
    def read_file(path: str) -> Optional[str]:
        """Read file contents."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {path}: {e}")
            return None

    @staticmethod
    def write_file(path: str, content: str) -> bool:
        """Write file contents."""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
            return False

    @staticmethod
    def list_files(path: str, pattern: str = "*") -> List[str]:
        """List files matching pattern."""
        try:
            return [str(p) for p in Path(path).glob(pattern)]
        except Exception as e:
            logger.error(f"Failed to list {path}: {e}")
            return []

    @staticmethod
    def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable."""
        return os.getenv(name, default)

    @staticmethod
    def set_env_var(name: str, value: str) -> None:
        """Set environment variable."""
        os.environ[name] = value

    @staticmethod
    def remove_directory(path: str) -> bool:
        """Remove directory recursively."""
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            return True
        except Exception as e:
            logger.error(f"Failed to remove {path}: {e}")
            return False
