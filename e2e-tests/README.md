# Mutation Maker E2E Tests

End-to-end tests for Mutation Maker using Playwright.

## Prerequisites

- Node.js 18+
- Running Mutation Maker application (frontend on port 3000)
- API server (port 8000) for API tests
- Celery worker for full integration tests

## Installation

```bash
npm install
npx playwright install chromium
```

## Running Tests

```bash
# Run all tests
npm test

# Run with UI mode
npm run test:ui

# Run in headed mode (visible browser)
npm run test:headed

# Debug mode
npm run test:debug

# View test report
npm run test:report

# Code generator (helps create tests)
npm run codegen
```

## Test Structure

```
tests/
  app.spec.ts       # UI tests for all workflows (32 tests)
  api.spec.ts       # API backend tests (9 tests, require Celery worker)
```

## Test Categories

### UI Tests (app.spec.ts) - 32 tests
- **Landing Page Tests**: Verify the home page and navigation links
- **SSM Workflow Tests**: Test the Single Site Mutagenesis form elements
- **QCLM Workflow Tests**: Test the QuikChange Multi Mutagenesis form
- **PAS Workflow Tests**: Test the Protein Analysis System form
- **Navigation Tests**: Verify routing between workflows
- **Accessibility Tests**: Check for labels and navigation elements

### API Tests (api.spec.ts) - 9 tests
- **SSM API Tests**: Submit jobs, degenerate mutations, multiple mutations
- **QCLM API Tests**: Submit jobs with different codon tables, status check
- **PAS API Tests**: Submit jobs with mutation frequencies

## Test Data

The tests use synthetic DNA sequences:

```typescript
// SSM test sequence (225bp gene of interest)
const SSM_SEQUENCE = {
  forwardPrimer: 'CAAGGAATGGTGCATGCAAG',
  reversePrimer: 'GAACGTGGCGAGAAAGGAAG',
  geneOfInterest: 'ATGACTTGCTGGCGCGTAATGGCTAAACAGATTTTGGATGCTGCCGCTG...',
  plasmidSequence: 'CAAGGAATGGTGCATGCAAGATGACTTGCTGGCGCGTAATGGCTAAACAG...'
}

// Valid DNA sequence for testing (183bp)
const VALID_DNA = 'ATGGCTAAACAGATTTTGGATGCTGCCGCTGGAAACTGGTGATTCAG...'

// Mutations
const MUTATIONS = {
  SSM: 'D32E',         // Position 32: Aspartic acid -> Glutamic acid
  degenerate: 'D32X',  // Position 32: any amino acid
  QCLM: 'E15W'         // Position 15: Glutamic acid -> Tryptophan
}
```

## Configuration

Tests are configured in `playwright.config.ts`. The configuration:
- Runs tests in parallel (4 workers)
- Connects to `http://localhost:3000`
- Captures screenshots on failure
- Records video on retry
- Supports Chromium and Firefox browsers

## CI Integration

For CI environments, the config automatically:
- Enables retries (2)
- Limits workers to 1
- Starts the frontend server if needed

## Running Full Integration Tests

To run all 41 tests (including API tests), ensure all services are running:

```bash
# Terminal 1: Redis
docker run -d -p 6379:6379 redis:alpine

# Terminal 2: API
cd api && gunicorn server:app --bind 0.0.0.0:8000

# Terminal 3: Celery Worker (requires PRIMER3HOME)
cd backend && PRIMER3HOME=/path/to/primer3/src/libprimer3 celery -A tasks worker --loglevel=INFO

# Terminal 4: Frontend
cd frontend && npm start

# Terminal 5: Run tests
cd e2e-tests && npm test
```

### Finding Primer3 Path

The Celery worker requires Primer3. If you have `primer3-py` installed:

```bash
# Find the primer3_core binary
find $(python -c "import primer3; import os; print(os.path.dirname(primer3.__file__))") -name "primer3_core"
```

## Test Results

```
Running 41 tests using 4 workers

  ✓  41 passed (7.9s)
    - 32 UI tests (app.spec.ts)
    -  9 API tests (api.spec.ts)
```
