---
agent: 'agent'
description: 'Guide for creating high-quality GitHub Copilot instruction files with proper structure, examples, and best practices'
---

# Instructions File Writer

Create a comprehensive, well-structured instruction file for GitHub Copilot that provides clear guidance for code generation and follows established patterns.

## Your Task

Generate a complete `.instructions.md` file for the specified technology, framework, or coding practice. The file should be production-ready and immediately usable by GitHub Copilot.

## Required Structure

### 1. YAML Frontmatter

```yaml
---
description: 'Clear, concise description of what these instructions cover (1-500 characters)'
applyTo: 'Glob pattern(s) for target files, e.g., **/*.py, **/*.ts, **/*.java'
---
```

**Guidelines for frontmatter:**
- Description must be single-quoted and specific
- Use appropriate glob patterns:
  - Language files: `**/*.py`, `**/*.ts`, `**/*.java`
  - Multiple extensions: `**/*.ts, **/*.tsx, **/*.js`
  - Specific directories: `src/**/*.py`
  - All files: `**` (use sparingly)
  - Configuration files: `**/package.json`, `**/pyproject.toml`

### 2. Title and Introduction

```markdown
# [Technology/Framework] Development

Brief introduction explaining:
- Purpose and scope of these instructions
- Target audience
- Key technologies and versions covered
```

### 3. Core Content Sections

Organize content logically based on the domain:

**For Programming Languages:**
- General Instructions
- Code Standards
- Best Practices
- Common Patterns
- Error Handling
- Testing Approaches
- Performance Considerations

**For Frameworks:**
- Project Structure
- Configuration
- Component/Module Patterns
- API/Service Patterns
- State Management
- Testing Strategies
- Deployment Guidelines

**For Practices (Security, Testing, etc.):**
- Principles and Philosophy
- Implementation Guidelines
- Common Scenarios
- Tools and Automation
- Validation Methods

### 4. Examples and Code Snippets

Always include concrete examples:

```markdown
### Good Example
\`\`\`language
// Clear, working example of recommended approach
code here
\`\`\`

### Bad Example
\`\`\`language
// Anti-pattern to avoid
code here
\`\`\`
```

### 5. Validation Section (if applicable)

```markdown
## Validation

- Build command: `npm run build` or `uv run test`
- Linting: `eslint .` or `ruff check`
- Testing: `npm test` or `pytest`
- Formatting: `prettier --check` or `black --check`
```

## Writing Guidelines

### Style and Tone

- Use imperative mood: "Use", "Implement", "Avoid", "Ensure"
- Be specific and actionable
- Avoid vague terms: "should", "might", "possibly"
- Keep sentences short and scannable
- Use bullet points and numbered lists
- Add inline code references with backticks

### Content Requirements

**Must Include:**
- Clear, specific guidance that Copilot can follow
- Real code examples (not pseudo-code)
- Naming conventions for files, functions, classes, variables
- Project organization and file structure patterns
- Common patterns for the domain
- Security considerations (if applicable)
- Performance tips (if applicable)

**Should Include:**
- Links to official documentation
- Version numbers for dependencies
- Tables for comparing options or listing rules
- Explanations of "why" behind recommendations
- Common pitfalls and how to avoid them
- Testing requirements and patterns

**Must Avoid:**
- Ambiguous or generic advice
- Outdated practices or deprecated features
- Copy-pasted documentation without context
- Contradictory guidelines
- Abstract concepts without examples
- Personal preferences without rationale

### Formatting Best Practices

**Use Tables for Structured Data:**

```markdown
| Pattern           | Use Case              | Example                    |
| ----------------- | --------------------- | -------------------------- |
| Factory Pattern   | Object creation       | `UserFactory.create()`     |
| Strategy Pattern  | Algorithm selection   | `PaymentStrategy.process()`|
```

**Use Nested Lists for Hierarchy:**

```markdown
## Code Organization

- Source code
  - Components
    - Named exports
    - One component per file
  - Services
    - API clients
    - Business logic
  - Utils
    - Pure functions
    - Helper methods
```

**Use Code Blocks with Language Tags:**

```markdown
\`\`\`python
# Always use type hints
def calculate_total(items: list[Item]) -> Decimal:
    return sum(item.price for item in items)
\`\`\`
```

## Examples by Category

### For a Programming Language (Python, TypeScript, etc.)

```markdown
---
description: 'Python development standards and best practices'
applyTo: '**/*.py'
---

# Python Development

## General Instructions

- Use Python 3.10+ features
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for all public functions and classes

## Code Standards

### Naming Conventions
- Variables and functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Imports
- Order: standard library, third-party, local
- Use absolute imports
- One import per line

## Best Practices

### Type Hints
\`\`\`python
from typing import Optional

def process_user(user_id: int, name: str) -> Optional[dict]:
    """Process user data and return result."""
    return {"id": user_id, "name": name}
\`\`\`
```

### For a Framework (React, FastAPI, Spring Boot, etc.)

```markdown
---
description: 'FastAPI development standards and patterns'
applyTo: '**/*.py, **/main.py'
---

# FastAPI Development

## Project Structure

\`\`\`
project/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   ├── core/
│   │   └── config.py
│   ├── models/
│   └── services/
└── tests/
\`\`\`

## API Patterns

### Route Definitions
\`\`\`python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    email: str

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user."""
    pass
\`\`\`
```

### For a Practice (Testing, Security, Performance, etc.)

```markdown
---
description: 'Comprehensive secure coding instructions based on OWASP'
applyTo: '**'
---

# Security Best Practices

## Principles

- Validate all user input
- Use parameterized queries for database access
- Implement proper authentication and authorization
- Never store secrets in code

## Input Validation

### Good Example
\`\`\`python
from pydantic import BaseModel, EmailStr, constr

class UserInput(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
\`\`\`

### Bad Example
\`\`\`python
def process_input(data: dict):
    # No validation - dangerous!
    db.execute(f"SELECT * FROM users WHERE name = '{data['name']}'")
\`\`\`
```

## Checklist Before Submitting

- [ ] YAML frontmatter is properly formatted
- [ ] `description` is clear and concise
- [ ] `applyTo` glob pattern matches target files
- [ ] Title is descriptive and uses `#` heading
- [ ] Introduction explains scope and purpose
- [ ] All sections are relevant to the domain
- [ ] Code examples are correct and runnable
- [ ] Examples show both good and bad patterns
- [ ] Naming conventions are specified
- [ ] File organization is described
- [ ] Security considerations included (if applicable)
- [ ] Performance tips included (if applicable)
- [ ] Testing approach described (if applicable)
- [ ] Language/framework versions specified
- [ ] Links to official docs included
- [ ] No contradictory advice
- [ ] No outdated or deprecated patterns
- [ ] Content is scannable with bullets and lists
- [ ] Tables used for structured comparisons
- [ ] Imperative mood used throughout

## Output Format

Provide the complete instruction file as markdown, ready to be saved as `.github/instructions/[name].instructions.md`. Include all sections, examples, and proper formatting.

Generate a comprehensive, production-ready instruction file that will help GitHub Copilot generate high-quality, consistent code for the specified domain.
