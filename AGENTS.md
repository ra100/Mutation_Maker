# Mutation Maker - Agent Guidelines

This document provides guidance for AI coding agents working on the Mutation Maker codebase.

## Project Overview

Mutation Maker is a mutagenic primer design application with three main workflows:

- **SSM** (Single Site Mutagenesis)
- **QCLM** (QuikChange Multi Mutagenesis)
- **PAS** (Protein Analysis System)

The application consists of:

- **frontend/**: React TypeScript application (Create React App)
- **backend/**: Python Celery worker for task processing
- **api/**: Python API server (Hug/Gunicorn)
- **lambda/**: AWS Lambda endpoint for Primer3 execution
- **webserver/**: Nginx proxy

## Build Commands

```bash
# Install all dependencies
make conda-env              # Create conda environment with Python dependencies
make env-frontend           # Install frontend packages (npm ci)

# Build frontend
make build-frontend         # Production build
cd frontend && npm run build

# Docker
make docker-build           # Build all containers
make docker-run             # Run all containers with docker-compose
```

## Test Commands

```bash
# Run all backend unit tests
make test
cd backend && PYTHONHASHSEED=0 python -m unittest tests/unit_tests/*

# Run a single test file
cd backend && PYTHONHASHSEED=0 python -m unittest tests/unit_tests/test_ssm.py

# Run a single test class or method
cd backend && PYTHONHASHSEED=0 python -m unittest tests/unit_tests/test_ssm.TestSSM
cd backend && PYTHONHASHSEED=0 python -m unittest tests/unit_tests/test_ssm.TestSSM.test_method_name

# Frontend tests
cd frontend && npm test
```

## Lint Commands

```bash
# Frontend lint (tslint)
cd frontend && npm run lint

# Frontend type check
cd frontend && npm run types
```

## Development Servers

```bash
make run                    # Run all services locally
make run-frontend           # Frontend dev server (localhost:3000)
make run-api                # API server (localhost:8000)
make run-worker             # Celery worker
make run-lambda             # AWS Lambda local (SAM CLI)
make run-monitor            # Celery flower monitor
```

## Python Code Style

### Import Order

1. Standard library imports
2. Third-party imports (numpy, biopython, etc.)
3. Local application imports (mutation*maker.*, tasks, tests.\_)

```python
import itertools
import math
from typing import List, Tuple, NamedTuple

import numpy as np
from Bio.Seq import Seq

from mutation_maker.mutation import AminoMutation
from .section_timer import SectionTimer
```

### Naming Conventions

- **Classes**: PascalCase (`SSMSolver`, `PrimerSpec`)
- **Functions/Methods**: snake_case (`ssm_solve`, `parse_codon_mutation`)
- **Variables**: snake_case (`mutation_string`, `fw_primers`)
- **Constants**: UPPER_SNAKE_CASE (`CODON_LENGTH`, `MAX_PRIMER3_PRIMER_SIZE`)
- **Type aliases**: PascalCase (`AminoAcid = NewType('AminoAcid', str)`)

### Type Hints

- Use type hints on function parameters and return types
- Import types from `typing` module (`List`, `Tuple`, `Set`, `Mapping`, `Optional`)
- Use forward references with quotes for circular dependencies

```python
def get_sequence(self, position: int, length: int) -> str:
    ...

def parse_mutations(self, data: List[str]) -> Tuple[AminoMutation, ...]:
    ...
```

### Error Handling

- Create custom exceptions for domain errors (`PASNoSolutionException`)
- Use `ValueError` for validation errors with descriptive messages
- Use `assert` for internal consistency checks

### License Header

All Python files must start with the 17-line GPL license header.
Excluding Merck copyright as for OpenSource not create by Merck it's not valid.

## TypeScript Code Style

### Import Order

1. External libraries (`react`, `ramda`, `axios`)
2. UI component libraries (`antd`)
3. Shared/internal components (`shared/components/...`)
4. Types and utilities (`shared/lib/...`)

```typescript
import React, { ReactNode } from 'react'
import * as R from 'ramda'
import { Button, Form, Input } from 'antd'

import FileUploadInput from 'shared/components/FileUploadInput'
import { SSMFormData } from 'shared/lib/FormData'
```

### Naming Conventions

- **Components**: PascalCase (`SSMForm`, `QCLMResult`)
- **Functions**: camelCase (`formParametersToRequestConfig`)
- **Variables**: camelCase (`ssmFormData`, `fwPrimer`)
- **Constants**: UPPER_SNAKE_CASE (`API_PREFIX`)
- **Types/Interfaces**: PascalCase (`SSMFormData`, `QCLMFormOuterProps`)

### Formatting (Prettier)

```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": false,
  "singleQuote": true,
  "trailingComma": "all",
  "bracketSpacing": true,
  "jsxBracketSameLine": true
}
```

### Component Patterns

- Use functional components with `React.FC` or `React.SFC`
- Use HOC pattern with `withForm` wrapper for forms
- Destructure props in function signatures
- Arrow functions for event handlers to preserve `this`

```typescript
type SSMFormInnerProps = SSMFormOuterProps & WithFormInnerProps<SSMFormData>

const SSMForm: React.FC<SSMFormInnerProps> = ({ formData, onSubmit }) => {
  // ...
}

export default withForm<SSMFormOuterProps, SSMFormData>(SSMForm)
```

### License Header

All TypeScript files must start with the 17-line GPL license block comment.
Excluding Merck copyright as for OpenSource not create by Merck it's not valid.

## Key Architectural Notes

- Frontend state is managed via `src/shared/components/withJobStore.ts` HOC
- API interactions go through `src/services/api.ts`
- Backend uses Celery with Redis for async task processing
- Primer3 can run locally, in Docker, or via AWS Lambda
- All three workflows share common components in `src/shared/`

## Testing Requirements

- Run `PYTHONHASHSEED=0` for consistent hash ordering in Python tests
- Frontend uses Jest with `--env=jsdom`
- Test files are located in `backend/tests/unit_tests/`
