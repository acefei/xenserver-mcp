---
description: 'Modern Python project development using uv for dependency management and ruff for linting/formatting'
applyTo: '**/*.py, **/pyproject.toml, **/uv.lock, **/.python-version'
---

# Modern Python Development with uv and ruff

Modern Python project setup and development practices using uv for fast, reliable dependency management and ruff for lightning-fast linting and formatting.

## Project Context

- **Python Version**: 3.12+ required (3.14+ recommended for latest features and performance)
- **Package Manager**: uv (Rust-based, extremely fast pip replacement)
- **Linter/Formatter**: ruff (Rust-based, replaces flake8, black, isort, and more)
- **Build System**: hatchling or setuptools via pyproject.toml
- **Type Checking**: mypy 1.11+ or pyright (optional but recommended)

## General Instructions

- **ALWAYS run `uv run ruff format .` and `uv run ruff check --fix .` in root path of repository after making any code changes**
- Define all project metadata in `pyproject.toml`
- Use type hints for all function signatures and class attributes
- Use modern type hint syntax: `str | None` instead of `Optional[str]` (Python 3.10+)
- **Use PEP 695 type parameter syntax** for generic classes/functions (Python 3.12+)
- **Leverage PEP 701 f-string improvements** - quote reuse, multiline, backslashes (Python 3.12+)
- **Leverage deferred annotation evaluation** (PEP 649, Python 3.14+) - no need for string quotes in forward references
- **Use template strings (t-strings)** for safe string interpolation when needed (PEP 750, Python 3.14+)
- Use virtual environments managed by uv
- Follow PEP 8 style guide (enforced by ruff)
- Use absolute imports instead of relative imports when possible

## Project Initialization

### Creating a New Project

```bash
# Initialize new project with uv
uv init my-project
cd my-project

# Or initialize in existing directory
uv init

# Create with specific Python version (3.14 recommended, 3.12 minimum)
uv init --python 3.14

# Or pin version with .python-version file
echo "3.14" > .python-version
uv init

# Add dependencies
uv add requests pydantic
uv add --dev pytest ruff mypy
```

### Project Structure

```
project-name/
├── .python-version          # Python version specification
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Locked dependencies (commit this!)
├── README.md               # Project documentation
├── .gitignore              # Git ignore patterns
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       └── utils/
│           └── __init__.py
└── tests/
    ├── __init__.py
    └── test_main.py
```

## pyproject.toml Configuration

### Minimal Configuration

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### Full Configuration with All Options

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Comprehensive project description"
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.6.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/username/project"
Documentation = "https://project.readthedocs.io"
Repository = "https://github.com/username/project"
Issues = "https://github.com/username/project/issues"

[project.scripts]
project-name = "project_name.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.ruff.lint]
# Enable comprehensive rule sets
select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "W",      # pycodestyle warnings
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "RUF",    # ruff-specific rules
]
ignore = [
    "E501",   # Line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert in tests
"__init__.py" = ["F401"]    # Allow unused imports in __init__

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.ruff.lint.isort]
known-first-party = ["project_name"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_unreachable = true
```

## Dependency Management with uv

### Common Commands

```bash
# Add production dependency
uv add requests

# Add with version constraint
uv add "pydantic>=2.0,<3.0"

# Add development dependency
uv add --dev pytest ruff mypy

# Add optional dependency group
uv add --optional docs sphinx sphinx-rtd-theme

# Remove dependency
uv remove requests

# Update all dependencies
uv lock --upgrade

# Sync environment with lock file
uv sync

# Install project in editable mode
uv pip install -e .

# Run command in virtual environment
uv run python main.py
uv run pytest
uv run ruff check .
```

### Dependency Pinning Best Practices

```toml
# Good - Allow compatible updates
[project]
dependencies = [
    "requests>=2.31.0,<3.0.0",  # Allow patch and minor updates
    "pydantic>=2.0.0,<3.0.0",   # Lock to major version
]

# Good - Exact pinning for critical dependencies
[project]
dependencies = [
    "cryptography==41.0.7",     # Security-critical, pin exactly
]

# Bad - Too loose
[project]
dependencies = [
    "requests",                  # No version constraint
    "pydantic>=1.0",            # Allows breaking changes
]
```

## Code Formatting and Linting with ruff

### Running ruff

```bash
# Check for issues
uv run ruff check .

# Check and auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check formatting without making changes
uv run ruff format . --check

# Run both checks and formatting
uv run ruff check . --fix && uv run ruff format .
```

### Integration in Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Code Standards

### Naming Conventions

```python
# Variables and functions: snake_case
user_name = "John"
user_count = 10

def calculate_total(items: list) -> float:
    return sum(item.price for item in items)

# Classes: PascalCase
class UserAccount:
    pass

class HTTPClient:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100
API_BASE_URL = "https://api.example.com"

# Private attributes/methods: leading underscore
class MyClass:
    def __init__(self):
        self._internal_state = None
    
    def _helper_method(self):
        pass

# Protected in modules: leading underscore
_internal_function()

# Module names: lowercase, underscores if needed
# my_module.py, data_processor.py
```

### Import Organization

ruff automatically organizes imports. Follow this order:

```python
# Standard library imports
import json
import os
from pathlib import Path
from typing import Optional

# Third-party imports
import requests
from pydantic import BaseModel, Field

# Local application imports
from project_name.config import settings
from project_name.utils import helper_function
```

### Type Hints

```python
from typing import Any
from collections.abc import Callable, Iterable

# Function signatures with type hints - use | for unions (Python 3.10+)
def process_data(
    data: list[dict[str, Any]],
    callback: Callable[[dict], None] | None = None,
) -> list[str]:
    """Process data with optional callback."""
    results = []
    for item in data:
        if callback:
            callback(item)
        results.append(str(item))
    return results

# Class attributes with type hints - use | instead of Optional
class User:
    """User model."""
    
    name: str
    age: int
    email: str | None = None
    
    def __init__(self, name: str, age: int, email: str | None = None) -> None:
        self.name = name
        self.age = age
        self.email = email
```

### Docstrings

Use Google-style or NumPy-style docstrings:

```python
def calculate_statistics(data: list[float], precision: int | None = None) -> dict[str, float]:
    """Calculate basic statistics for a dataset.
    
    Args:
        data: List of numeric values to analyze
        precision: Optional decimal precision for results
        
    Returns:
        Dictionary containing mean, median, and standard deviation
        
    Raises:
        ValueError: If data is empty
        
    Example:
        >>> calculate_statistics([1, 2, 3, 4, 5])
        {'mean': 3.0, 'median': 3.0, 'std': 1.58}
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    return {
        "mean": sum(data) / len(data),
        "median": sorted(data)[len(data) // 2],
        "std": calculate_std(data),
    }
```

## Python 3.12+ Modern Features

### PEP 701: F-String Improvements (Python 3.12+)

Python 3.12+ removes many f-string limitations:

```python
# ✅ Quote reuse (Python 3.12+)
songs = ['Take me back to Eden', 'Alkaline', 'Ascensionism']
playlist = f"Playlist: {', '.join(songs)}"

# ✅ Multi-line expressions with comments
result = f"""Configuration: {
    ', '.join([
        f"host={config['host']}",      # Database host
        f"port={config['port']}",      # Database port  
        f"db={config['database']}"     # Database name
    ])
}"""

# ✅ Backslashes and unicode characters
items = ['apple', 'banana', 'cherry']
print(f"Items:\n{'\n'.join(items)}")
print(f"Separator: {'\N{BLACK HEART SUIT}'.join(['a', 'b', 'c'])}")

# ✅ Nested f-strings
outer = "world"
result = f"Hello {f"beautiful {outer}"}"

# ❌ Python 3.11 - These would cause SyntaxError
# playlist = f"Playlist: {", ".join(songs)}"  # Quote issue
# result = f"Items:\n{"\n".join(items)}"      # Backslash issue
```

### Improved Error Messages (Python 3.12+)

Python 3.12+ provides significantly better error messages:

```python
# Suggests imports for NameError
>>> sys.version_info
NameError: name 'sys' is not defined. Did you forget to import 'sys'?

# Suggests correct attribute names
>>> from collections import chainmap
ImportError: cannot import name 'chainmap' from 'collections'. 
Did you mean: 'ChainMap'?

# Better syntax error messages  
>>> import x from y
SyntaxError: Did you mean to use 'from ... import ...' instead?

# Suggests keyword argument corrections
>>> "test".split(max_split=1)
TypeError: split() got an unexpected keyword argument 'max_split'. 
Did you mean 'maxsplit'?
```

### Python 3.13+ Additional Features

#### TypeVar Defaults (PEP 696, Python 3.13+)

```python
from typing import TypeVar

# Type parameter with default
T = TypeVar('T', default=str)

class Container[T = int]:
    """Container with default int type."""
    def __init__(self, value: T) -> None:
        self.value = value

# Usage
Container()          # Container[int] (uses default)
Container("hello")   # Container[str] (inferred from argument)
```

#### Deprecation Decorator (PEP 702, Python 3.13+)

```python
from warnings import deprecated

@deprecated("Use new_function() instead")
def old_function() -> None:
    """Deprecated function."""
    pass

@deprecated("Use NewClass instead", category=DeprecationWarning)
class OldClass:
    """Deprecated class."""
    pass

# Type checkers will warn about usage
old_function()  # Type checker shows deprecation warning
```

#### ReadOnly TypedDict (PEP 705, Python 3.13+)

```python
from typing import TypedDict, ReadOnly

class User(TypedDict):
    id: ReadOnly[int]      # Cannot be modified
    name: str              # Can be modified
    email: ReadOnly[str]   # Cannot be modified

def update_user(user: User, name: str) -> None:
    user["name"] = name    # ✅ OK
    user["id"] = 123       # ❌ Type checker error
```

#### TypeIs for Better Type Narrowing (PEP 742, Python 3.13+)

```python
from typing import TypeIs

def is_str_list(val: list[object]) -> TypeIs[list[str]]:
    """Check if all items are strings."""
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_str_list(items):
        # Type checker knows items is list[str] here
        result = ", ".join(items)  # ✅ OK
```

### Standard Library Improvements

#### itertools.batched() (Python 3.12+)

```python
from itertools import batched

# Process items in batches
data = range(10)
for batch in batched(data, 3):
    print(batch)
# Output: (0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)

# Python 3.13+: strict parameter
try:
    for batch in batched(range(10), 3, strict=True):
        print(batch)
except ValueError:
    print("Incomplete final batch")
```

#### pathlib Enhancements (Python 3.12+)

```python
from pathlib import Path

# pathlib.Path now supports subclassing
class ProjectPath(Path):
    """Custom Path subclass."""
    
    def read_json(self):
        """Read JSON from file."""
        import json
        return json.loads(self.read_text())
    
    def write_json(self, data):
        """Write JSON to file."""
        import json
        self.write_text(json.dumps(data, indent=2))

# Use custom path class
config_path = ProjectPath("config.json")
config = config_path.read_json()
```

#### TypedDict for **kwargs (PEP 692, Python 3.12+)

```python
from typing import TypedDict, Unpack

class MovieInfo(TypedDict):
    title: str
    year: int
    director: str

def create_movie(**kwargs: Unpack[MovieInfo]) -> None:
    """Create movie with type-safe kwargs."""
    print(f"{kwargs['title']} ({kwargs['year']})")
    print(f"Director: {kwargs['director']}")

# Type checker validates arguments
create_movie(title="Inception", year=2010, director="Nolan")  # ✅ OK
create_movie(title="Test")  # ❌ Type checker error: missing year, director
```

#### Override Decorator (PEP 698, Python 3.12+)

```python
from typing import override

class Base:
    def method(self) -> str:
        return "base"
    
    def other_method(self) -> int:
        return 42

class Derived(Base):
    @override  # Type checker ensures this actually overrides
    def method(self) -> str:
        return "derived"
    
    @override
    def meth0d(self) -> str:  # ❌ Type checker error: doesn't override anything
        return "typo"
```

### Performance Considerations (Python 3.13+)

#### JIT Compiler

```bash
# Enable experimental JIT compiler
PYTHON_JIT=1 python script.py

# Modest performance improvements (5-10% typical)
# More improvements expected in future releases
```

#### Free-Threading Mode

```bash
# Build Python with --disable-gil
# Or use python3.13t executable

# Allows true parallel execution of Python threads
# Not recommended for production yet (experimental)
```

#### Faster isinstance() Checks

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    """Protocol for drawable objects."""
    def draw(self) -> None: ...

# isinstance() checks 2-20x faster in Python 3.13+
if isinstance(obj, Drawable):
    obj.draw()
```

### Python 3.14+ Exclusive Features

#### Deferred Annotation Evaluation (PEP 649/749, Python 3.14+)

Annotations are no longer evaluated eagerly - forward references work without quotes:

```python
# ✅ Python 3.14+ - No quotes needed for forward references
class Node:
    """Binary tree node."""
    def __init__(self, value: int, left: Node | None = None, right: Node | None = None):
        self.value = value
        self.left = left
        self.right = right

# ❌ Python 3.13 and earlier - Needed quotes or from __future__ import
class Node:
    def __init__(self, value: int, left: "Node | None" = None, right: "Node | None" = None):
        pass

# Use annotationlib for introspection (Python 3.14+)
from annotationlib import get_annotations, Format

def func(arg: UndefinedType) -> int:
    return 42

# Get annotations as values (may raise NameError)
annotations = get_annotations(func, format=Format.VALUE)

# Get annotations with ForwardRef for undefined names
annotations = get_annotations(func, format=Format.FORWARDREF)
# {'arg': ForwardRef('UndefinedType'), 'return': int}

# Get annotations as strings
annotations = get_annotations(func, format=Format.STRING)
# {'arg': 'UndefinedType', 'return': 'int'}
```

#### Template String Literals (PEP 750, Python 3.14+)

Use `t` prefix for safe, custom string processing (alternative to f-strings for special cases):

```python
from string.templatelib import Interpolation

# Basic template string
variety = 'Stilton'
template = t'Try some {variety} cheese!'

# Access parts of template
list(template)
# ['Try some ', Interpolation('Stilton', 'variety', None, ''), ' cheese!']

# Custom processing - example: lowercase static, uppercase interpolations
def lower_upper(template):
    """Render static parts lowercase and interpolations uppercase."""
    parts = []
    for part in template:
        if isinstance(part, Interpolation):
            parts.append(str(part.value).upper())
        else:
            parts.append(part.lower())
    return ''.join(parts)

name = 'Wenslydale'
result = lower_upper(t'Mister {name}')
# 'mister WENSLYDALE'

# Use case: Safe HTML rendering (prevents XSS)
def html(template):
    """Render template with HTML escaping for interpolations."""
    # Implementation escapes user input but not static HTML
    pass

user_input = '<script>alert("xss")</script>'
safe_html = html(t'<div>User: {user_input}</div>')
# '<div>User: &lt;script&gt;alert("xss")&lt;/script&gt;</div>'

# Use case: Safe SQL queries (prevents SQL injection)
def sql(template):
    """Render template with proper SQL parameterization."""
    pass

username = "admin'; DROP TABLE users--"
query = sql(t'SELECT * FROM users WHERE name = {username}')
# Properly parameterized query, safe from injection
```

#### Multiple Interpreters in Standard Library (PEP 734, Python 3.14+)

Run multiple isolated Python interpreters for true parallelism:

```python
import concurrent.interpreters as interpreters

# Create a new interpreter
interp = interpreters.create()

# Run code in the interpreter
code = """
import sys
print(f"Running in interpreter {sys.version}")
result = 2 + 2
"""
interp.exec(code)

# Share data between interpreters using channels
with interpreters.Pipe() as (send_ch, recv_ch):
    # Run code that sends data
    interp.exec("""
    import concurrent.interpreters as interpreters
    ch = interpreters.channel.from_id({send_ch.id})
    ch.send("Hello from interpreter!")
    """)
    
    # Receive data in main interpreter
    message = recv_ch.recv()
    print(message)

# Use InterpreterPoolExecutor for parallel work
from concurrent.futures import InterpreterPoolExecutor

def compute(n):
    return sum(i * i for i in range(n))

with InterpreterPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(compute, [1000000, 2000000, 3000000]))

# Benefits over multiprocessing:
# - Lower memory usage (shared runtime)
# - Faster startup
# - Same process, better efficiency
# - True parallelism (no GIL sharing between interpreters)

# Current limitations (being addressed):
# - Startup overhead not yet optimized
# - Not all extension modules compatible
# - Limited data sharing options
```

#### Improved Error Messages (Python 3.14+)

```python
# Suggests corrections for typos in keywords
>>> whille True:
...     pass
SyntaxError: invalid syntax. Did you mean 'while'?

# Better suggestions for misspelled names
>>> from collections import chainmap
ImportError: cannot import name 'chainmap' from 'collections'. 
Did you mean: 'ChainMap'?

# Clearer syntax error messages
>>> import x from y
SyntaxError: Did you mean to use 'from ... import ...' instead?
```

#### Incremental Garbage Collection (Python 3.14+)

```python
import gc

# GC is now incremental - reduces pause times significantly
# For large heaps, pauses are 10x+ shorter

# The meaning of gc functions has changed slightly:
# gc.collect(0) - collects only generation 0 (young objects)
# gc.collect(1) - performs one increment of GC work
# gc.collect(2) - full collection (old behavior for generation 2)

# Check GC stats
stats = gc.get_stats()
# Stats structure changed to reflect incremental collection

# For most code, this is transparent and just works better
```

#### New Standard Library Modules (Python 3.14+)

```python
# annotationlib - for working with annotations
from annotationlib import get_annotations, Format

# compression.zstd - Zstandard compression (PEP 784)
from compression import zstd

# Compress data
data = b"Hello, World!" * 100
compressed = zstd.compress(data, level=3)  # level 1-22
decompressed = zstd.decompress(compressed)

# Streaming compression
with open("file.txt", "rb") as input_file:
    with open("file.txt.zst", "wb") as output_file:
        compressor = zstd.ZstdCompressor(level=3)
        for chunk in input_file:
            output_file.write(compressor.compress(chunk))
        output_file.write(compressor.flush())

# string.templatelib - for template string support (see above)
from string.templatelib import Template, Interpolation

# concurrent.interpreters - for multiple interpreters (see above)
from concurrent.interpreters import create, Pipe
```

#### Standard Library Improvements (Python 3.14+)

```python
# bytes.fromhex() now accepts bytes
data = bytes.fromhex(b"48656c6c6f")  # New in 3.14

# map() now has strict parameter like zip()
result = map(func, iter1, iter2, strict=True)  # Raises if lengths differ

# memoryview supports subscripting (generic type)
from typing import Buffer
view: memoryview[int] = memoryview(array('i', [1, 2, 3]))

# NotImplemented now raises TypeError in boolean context
if NotImplemented:  # Raises TypeError in 3.14
    pass

# pathlib improvements
from pathlib import Path
path = Path("file.txt")
info = path.info  # New: cached stat() results and file type info

# asyncio improvements - better introspection
import asyncio

async def main():
    # Call graph introspection
    graph = await asyncio.capture_call_graph()
    asyncio.print_call_graph(graph)

# unittest improvements - colored output by default
# Just run: python -m pytest
# Color controlled by NO_COLOR, FORCE_COLOR environment variables
```

#### Deprecations to Avoid (Python 3.14+)

```python
# ❌ Avoid - Deprecated in 3.14
from __future__ import annotations  # Being phased out, use native 3.14 behavior

complex(1+2j, 0)  # Deprecated: complex numbers as real/imag args

asyncio.iscoroutinefunction(func)  # Use inspect.iscoroutinefunction()

codecs.open('file.txt')  # Use built-in open() instead

os.popen('command')  # Use subprocess module
os.spawn*('command')  # Use subprocess module

# ❌ pathlib - deprecated
from pathlib import PurePath
PurePath.as_uri()  # Use Path.as_uri() instead

# ✅ Correct alternatives
import inspect
from subprocess import run
from pathlib import Path

inspect.iscoroutinefunction(func)
run(['ls', '-la'], capture_output=True)
Path('file.txt').as_uri()
```

## Best Practices

### Error Handling

```python
# Good - Specific exception handling
def read_config(path: Path) -> dict:
    """Read configuration from file."""
    try:
        with path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config: {e}")
        raise

# Bad - Catch-all exception
def read_config(path: Path) -> dict:
    try:
        with path.open() as f:
            return json.load(f)
    except Exception:  # Too broad
        return {}
```

### Context Managers

```python
# Good - Use context managers for resources
from pathlib import Path

def process_file(path: Path) -> None:
    """Process file content."""
    with path.open() as f:
        data = f.read()
        # Process data

# Good - Custom context manager
from contextlib import contextmanager

@contextmanager
def database_connection(url: str):
    """Manage database connection."""
    conn = connect(url)
    try:
        yield conn
    finally:
        conn.close()

with database_connection("postgresql://...") as conn:
    conn.execute("SELECT * FROM users")
```

### Path Handling

```python
from pathlib import Path

# Good - Use pathlib.Path
config_dir = Path(__file__).parent / "config"
config_file = config_dir / "settings.json"

if config_file.exists():
    content = config_file.read_text()

# Bad - String concatenation
config_dir = os.path.dirname(__file__) + "/config"
config_file = config_dir + "/settings.json"
```

### Data Classes and Pydantic

```python
from dataclasses import dataclass
from pydantic import BaseModel, Field, EmailStr

# Good - Use dataclass for simple data containers
@dataclass
class Point:
    """2D point."""
    x: float
    y: float

# Good - Use Pydantic for validation
class UserCreate(BaseModel):
    """User creation model."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(ge=0, le=150)

# Automatic validation
user = UserCreate(
    username="john",
    email="john@example.com",
    age=30
)
```

### Async/Await

```python
import asyncio
from collections.abc import AsyncIterator

# Good - Async function with proper typing
async def fetch_data(url: str) -> dict:
    """Fetch data from URL asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Good - Async generator
async def stream_data(source: str) -> AsyncIterator[dict]:
    """Stream data from source."""
    async for item in fetch_items(source):
        processed = process_item(item)
        yield processed

# Usage
async def main() -> None:
    data = await fetch_data("https://api.example.com")
    
    async for item in stream_data("source"):
        print(item)

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing with pytest

### Test Structure

```python
# tests/test_calculator.py
import pytest
from project_name.calculator import Calculator

class TestCalculator:
    """Test calculator functionality."""
    
    def test_add(self):
        """Test addition operation."""
        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5
    
    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        calc = Calculator()
        with pytest.raises(ZeroDivisionError):
            calc.divide(10, 0)
    
    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 5),
        (-1, 1, 0),
        (0, 0, 0),
    ])
    def test_add_parametrized(self, a: int, b: int, expected: int):
        """Test addition with multiple inputs."""
        calc = Calculator()
        assert calc.add(a, b) == expected
```

### Fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Create temporary config file."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"api_key": "test"}')
    return config_file

def test_read_config(temp_config_file: Path):
    """Test config file reading."""
    config = read_config(temp_config_file)
    assert config["api_key"] == "test"
```

## Common Patterns

### Singleton Pattern

```python
class DatabaseConnection:
    """Singleton database connection."""
    
    _instance: "DatabaseConnection | None" = None
    
    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.connect()
```

### Factory Pattern

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    """Abstract animal base class."""
    
    @abstractmethod
    def speak(self) -> str:
        pass

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

class AnimalFactory:
    """Factory for creating animals."""
    
    @staticmethod
    def create_animal(animal_type: str) -> Animal:
        """Create animal by type."""
        animals = {
            "dog": Dog,
            "cat": Cat,
        }
        
        animal_class = animals.get(animal_type.lower())
        if not animal_class:
            raise ValueError(f"Unknown animal type: {animal_type}")
        
        return animal_class()
```

### Dependency Injection

```python
from abc import ABC, abstractmethod

class Database(ABC):
    """Abstract database interface."""
    
    @abstractmethod
    def query(self, sql: str) -> list[dict]:
        pass

class PostgresDatabase(Database):
    """PostgreSQL implementation."""
    
    def query(self, sql: str) -> list[dict]:
        # Implementation
        pass

class UserService:
    """User service with dependency injection."""
    
    def __init__(self, database: Database) -> None:
        self.db = database
    
    def get_users(self) -> list[dict]:
        """Get all users."""
        return self.db.query("SELECT * FROM users")

# Usage
db = PostgresDatabase()
service = UserService(database=db)
users = service.get_users()
```

## Performance Considerations

### List Comprehensions vs Loops

```python
# Good - List comprehension (faster)
squares = [x**2 for x in range(1000)]

# Good - Generator for large datasets
squares_gen = (x**2 for x in range(1000000))

# Avoid - Unnecessary loops
squares = []
for x in range(1000):
    squares.append(x**2)
```

### String Concatenation

```python
# Good - Join for multiple strings
parts = ["part1", "part2", "part3"]
result = "".join(parts)

# Good - f-strings for formatting
name = "John"
greeting = f"Hello, {name}!"

# Avoid - String concatenation in loops
result = ""
for part in parts:
    result += part  # Creates new string each iteration
```

### Caching

```python
from functools import lru_cache, cache

# Good - Cache expensive computations
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Calculate Fibonacci number with caching."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Good - Simple cache (Python 3.9+)
@cache
def get_config() -> dict:
    """Load and cache configuration."""
    return load_config_from_file()
```

## Validation Commands

```bash
# Format code
uv run ruff format .

# Check and fix linting issues
uv run ruff check . --fix

# Type checking
uv run mypy src

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run all checks
uv run ruff format . && \
uv run ruff check . --fix && \
uv run mypy src && \
uv run pytest --cov=src
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12', '3.13', '3.14']  # Test multiple versions
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        
      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}
        
      - name: Install dependencies
        run: uv sync --all-extras --dev
        
      - name: Format check
        run: uv run ruff format . --check
        
      - name: Lint
        run: uv run ruff check .
        
      - name: Type check
        run: uv run mypy src
        
      - name: Test
        run: uv run pytest --cov=src --cov-report=xml
        
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## References

- [Python 3.14 What's New](https://docs.python.org/3.14/whatsnew/3.14.html)
- [Python 3.13 What's New](https://docs.python.org/3.13/whatsnew/3.13.html)
- [Python 3.12 What's New](https://docs.python.org/3.12/whatsnew/3.12.html)
- [uv Documentation](https://docs.astral.sh/uv/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [PEP 649 - Deferred Evaluation of Annotations](https://peps.python.org/pep-0649/)
- [PEP 749 - Implementing PEP 649](https://peps.python.org/pep-0749/)
- [PEP 750 - Template Strings](https://peps.python.org/pep-0750/)
- [PEP 734 - Multiple Interpreters](https://peps.python.org/pep-0734/)
- [PEP 784 - Zstandard Support](https://peps.python.org/pep-0784/)
- [Type Hints PEP 484](https://peps.python.org/pep-0484/)
- [PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [Python Packaging Guide](https://packaging.python.org/)
