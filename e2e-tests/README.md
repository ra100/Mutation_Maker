# Mutation Maker E2E Tests

End-to-end tests for Mutation Maker using Playwright.

## Prerequisites

- Node.js 18+
- Running Mutation Maker application (frontend on port 3000)

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
  app.spec.ts      # Main application tests
```

## Test Categories

- **Landing Page Tests**: Verify the home page and navigation links
- **SSM Workflow Tests**: Test the Single Site Mutagenesis form
- **Navigation Tests**: Verify routing between workflows
- **Accessibility Tests**: Check for labels and navigation elements

## Configuration

Tests are configured in `playwright.config.ts`. The configuration:
- Runs tests in parallel
- Connects to `http://localhost:3000`
- Captures screenshots on failure
- Records video on retry
- Supports Chromium, Firefox, and WebKit browsers

## CI Integration

For CI environments, the config automatically:
- Enables retries (2)
- Limits workers to 1
- Starts the frontend server if needed
