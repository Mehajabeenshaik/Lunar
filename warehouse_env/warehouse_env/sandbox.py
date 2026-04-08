"""Safe code execution sandbox for agent-submitted actions."""

import signal
import sys
from typing import Tuple, Any, Optional
from contextlib import contextmanager


class TimeoutError(Exception):
    """Execution timeout error."""
    pass


class SandboxExecutor:
    """Safe execution environment with timeout and restricted access."""
    
    # Restricted builtins (similar to APEX)
    RESTRICTED_BUILTINS = {
        '__import__': None,
        'open': None,
        'input': None,
        'eval': None,
        'exec': None,
        'compile': None,
        'globals': None,
        'locals': None,
        'vars': None,
        'dir': None,
        'getattr': None,
        'setattr': None,
        'delattr': None,
        'hasattr': None,
        'type': None,
        '__loader__': None,
        '__spec__': None,
    }
    
    ALLOWED_MODULES = {
        'numpy': 'np',
        'pandas': 'pd',
        'math': 'math',
        'random': 'random',
        'json': 'json',
    }
    
    def __init__(self, timeout_sec: int = 5):
        """Initialize sandbox.
        
        Args:
            timeout_sec: Execution timeout in seconds (default 5)
        """
        self.timeout_sec = timeout_sec
    
    def _timeout_handler(self, signum, frame):
        """Handle execution timeout."""
        raise TimeoutError(f"Execution exceeded {self.timeout_sec} seconds")
    
    def execute_action(self, action_code: str, context: dict = None) -> Tuple[bool, Any, str]:
        """Execute agent action in restricted sandbox.
        
        Args:
            action_code: Python code to execute
            context: Available variables in execution context
            
        Returns:
            (success, result, error_message)
        """
        context = context or {}
        
        # Validate code length (prevent DOS)
        if len(action_code) > 50000:
            return False, None, "Action code exceeds size limit (50KB)"
        
        # Create restricted namespace
        safe_globals = {
            '__builtins__': {},
            **self.ALLOWED_MODULES,
            **context,
        }
        
        # Add safe builtins
        for name in ['len', 'range', 'enumerate', 'zip', 'map', 'filter', 
                     'sum', 'min', 'max', 'sorted', 'reversed', 'abs', 'round',
                     'int', 'float', 'str', 'list', 'dict', 'set', 'tuple',
                     'print', 'len', 'range']:
            try:
                safe_globals['__builtins__'][name] = __builtins__[name]
            except (KeyError, TypeError):
                pass
        
        try:
            # Set timeout (Unix only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.timeout_sec)
            
            # Execute in restricted environment
            local_vars = {}
            exec(action_code, safe_globals, local_vars)
            
            # Cancel alarm if set
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            # Get result
            result = local_vars.get('result', None)
            return True, result, None
            
        except TimeoutError as e:
            return False, None, f"Timeout: {str(e)}"
        except SyntaxError as e:
            return False, None, f"Syntax error: {str(e)}"
        except Exception as e:
            error_type = type(e).__name__
            return False, None, f"{error_type}: {str(e)}"
        finally:
            # Always cancel alarm
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
    
    def validate_action(self, action_code: str) -> Tuple[bool, str]:
        """Pre-validate action code for dangerous operations.
        
        Returns:
            (is_safe, reason)
        """
        # Check for dangerous patterns
        dangerous_patterns = [
            'import os',
            'import sys',
            'import subprocess',
            '__import__',
            'eval(',
            'exec(',
            'compile(',
            'open(',
            'input(',
        ]
        
        for pattern in dangerous_patterns:
            if pattern in action_code:
                return False, f"Code contains dangerous operation: {pattern}"
        
        return True, "Code is safe to execute"


class SandboxResult:
    """Result of sandbox execution."""
    
    def __init__(self, success: bool, result: Any = None, error: str = None, 
                 execution_time: float = 0.0):
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.score = self._calculate_score()
    
    def _calculate_score(self) -> float:
        """Calculate score based on execution result."""
        if not self.success:
            if "Timeout" in (self.error or ""):
                return 0.2  # Partial credit for timeout
            elif "Syntax" in (self.error or ""):
                return 0.1  # No credit for syntax errors
            else:
                return 0.15  # Minimal credit for runtime errors
        
        # Success gets baseline credit
        score = 0.5
        
        # Bonus for speed (under timeout)
        if self.execution_time < 1.0:
            score += 0.2
        elif self.execution_time < 3.0:
            score += 0.15
        else:
            score += 0.05
        
        # Result-based adjustment
        if self.result is not None:
            score += 0.25
        
        return min(1.0, score)
