---
title: Phased React and Ant Design Upgrade
type: feat
date: 2026-02-13
---

# Phased React and Ant Design Upgrade Plan

## Overview

A phased migration from React 17 + antd 3 to React 18/19 + antd 5, building on the completed Vite migration. This plan prioritizes stability with incremental upgrades.

## Current State

| Package | Current Version | Phase 1 Target | Phase 2 Target | Phase 3 Target |
|---------|-----------------|----------------|-----------------|-----------------|
| React | 17.0.2 | 18.3.x | 19.x | 19.x |
| antd | 3.26.20 | 4.24.x | 5.x | 5.x |
| TypeScript | 4.9.5 | 5.x | 5.x | 5.x |
| Build | Vite 7.x | Vite 7.x | Vite 7.x | Vite 7.x |

### Completed Work
- ✅ Vite migration (from CRA)
- ✅ Python 3.11 upgrade
- ✅ FastAPI migration

### Research Findings Summary

**antd Form Patterns (Must Migrate):**
- `withForm.ts` - Form.create() wrapper (1 usage)
- `getFieldDecorator` - 83+ usages across 7 files
- Files affected:
  - `frontend/src/shared/withForm.ts:35` - Form.create()
  - `frontend/src/shared/components/CodonUsage.tsx` - 5 getFieldDecorator
  - `frontend/src/shared/components/ParametersFormSection/index.tsx` - 21 getFieldDecorator
  - `frontend/src/shared/components/MinOptMaxInputs/index.tsx` - 5 getFieldDecorator
  - `frontend/src/scenes/SSM/components/SSMForm.tsx` - 11 getFieldDecorator
  - `frontend/src/scenes/QCLM/components/QCLMForm.tsx` - 24 getFieldDecorator
  - `frontend/src/scenes/PAS/components/PASForm/index.tsx` - 14 getFieldDecorator
  - `frontend/src/scenes/PAS/components/PASForm/components/InputMutations/index.tsx` - 3 getFieldDecorator

**antd Icon Usage (Must Migrate):**
| File | Icon Type | Replacement |
|------|-----------|-------------|
| `FileUploadInput/index.tsx:77` | `inbox` | `InboxOutlined` |
| `FileUploadMutations.tsx:111` | `inbox` | `InboxOutlined` |
| `SSMResultTable/index.tsx:177` | `check` | `CheckOutlined` |
| `SSMResultTable/index.tsx:179` | `close` | `CloseOutlined` |
| `PrimerReportPopover.tsx:59` | `info-circle-o` | `InfoCircleOutlined` |

**React Deprecations:**
- `React.SFC` in `withForm.ts:33` → `React.FC`
- `ReactDOM.render` in `index.tsx:27` → `createRoot`

## Problem Statement

The application uses deprecated dependencies:
- **React 17**: Missing concurrent features, security updates
- **antd 3**: EOL, known security vulnerabilities, incompatible with modern React
- **TypeScript 4.9**: Missing latest type improvements

### Why Now (2026)
- React 19 is stable (released Dec 2024)
- antd 3 no longer receives security patches
- Many libraries now require React 18+ minimum
- antd 5 offers significant performance improvements with CSS-in-JS

---

## Phase 1: React 18 + antd 4 (Foundation)

**Goal:** Get to a stable modern baseline with minimal breaking changes.

**Duration:** 2-3 days

### Step 1.1: React 18 Upgrade

**Changes to `frontend/package.json`:**
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0"
  }
}
```

**File: `frontend/src/index.tsx`**
```typescript
// Before (React 17)
import * as ReactDOM from 'react-dom'
ReactDOM.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
  document.getElementById('root'),
)

// After (React 18)
import { createRoot } from 'react-dom/client'
const root = createRoot(document.getElementById('root')!)
root.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
)
```

**File: `frontend/src/shared/withForm.ts:33`**
```typescript
// Before
function withForm<P, D>(
  component: React.ComponentClass<P & WithFormInnerProps<D>> | React.SFC<P & WithFormInnerProps<D>>,
)

// After
function withForm<P, D>(
  component: React.ComponentClass<P & WithFormInnerProps<D>> | React.FC<P & WithFormInnerProps<D>>,
)
```

**Run codemod:**
```bash
cd frontend
npx types-react-codemod@latest preset-18 src
```

### Step 1.2: TypeScript 5 Upgrade

**Changes to `frontend/package.json`:**
```json
{
  "devDependencies": {
    "typescript": "^5.7.0"
  }
}
```

**Update `frontend/tsconfig.json`:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "moduleResolution": "bundler"
  }
}
```

### Step 1.3: antd 4 Upgrade

**Changes to `frontend/package.json`:**
```json
{
  "dependencies": {
    "antd": "^4.24.15",
    "@ant-design/icons": "^4.8.0"
  }
}
```

**Install:**
```bash
cd frontend
npm install antd@^4.24.15 @ant-design/icons@^4.8.0
```

**Run codemod:**
```bash
npx -p @ant-design/codemod-v4 antd4-codemod src
```

**Manual Icon Migration (4 files):**

File: `frontend/src/shared/components/FileUploadInput/index.tsx`
```typescript
// Before
import { Icon } from 'antd'
<Icon type="inbox" />

// After
import { InboxOutlined } from '@ant-design/icons'
<InboxOutlined />
```

File: `frontend/src/scenes/PAS/components/PASForm/components/InputMutations/FileUploadMutations.tsx`
```typescript
// Before
import { Icon } from 'antd'
<Icon type="inbox" />

// After
import { InboxOutlined } from '@ant-design/icons'
<InboxOutlined />
```

File: `frontend/src/scenes/SSM/components/SSMResult/components/SSMResultTable/index.tsx`
```typescript
// Before
import { Icon } from 'antd'
<Icon type="check" />
<Icon type="close" />

// After
import { CheckOutlined, CloseOutlined } from '@ant-design/icons'
<CheckOutlined />
<CloseOutlined />
```

File: `frontend/src/scenes/SSM/components/SSMResult/components/SSMResultTable/components/PrimerReportPopover.tsx`
```typescript
// Before
import { Icon } from 'antd'
<Icon type="info-circle-o" />

// After
import { InfoCircleOutlined } from '@ant-design/icons'
<InfoCircleOutlined />
```

**Update CSS import in `frontend/src/index.tsx`:**
```typescript
// Before
import 'antd/dist/antd.css'

// After (antd 4)
import 'antd/dist/antd.css' // Same for antd 4
```

### Step 1.4: Form Migration (antd 4)

**CRITICAL:** The `Form.create()` and `getFieldDecorator` pattern has no direct antd 4 equivalent. The codemod converts to `Form.useForm()` hooks.

**File: `frontend/src/shared/withForm.ts`**

The `withForm` HOC wraps forms with `Form.create()`. This needs complete rewrite:

```typescript
// Before (antd 3)
import { Form } from 'antd'
import { WrappedFormUtils, FormComponentProps } from 'antd/lib/form/Form'

function withForm<P, D>(
  component: React.FC<P & WithFormInnerProps<D>>,
) {
  return Form.create<P & WithFormOuterProps<D>>({
    mapPropsToFields({ data }) { ... }
  })(component)
}

// After (antd 4)
import { Form, FormInstance } from 'antd'

// New approach: Use render prop or context instead of HOC
// Option A: Refactor forms to use Form.useForm() directly
// Option B: Create a compatible wrapper component

// Recommended: Gradual migration - keep withForm as wrapper
// but update internal implementation
function withForm<P, D>() {
  return function (
    Component: React.FC<P & WithFormInnerProps<D>>
  ): React.FC<P & WithFormOuterProps<D>> {
    const WrappedComponent: React.FC<P & WithFormOuterProps<D>> = (props) => {
      const [form] = Form.useForm()
      
      React.useEffect(() => {
        if (props.data) {
          form.setFieldsValue(props.data as any)
        }
      }, [props.data])
      
      return (
        <Form form={form} onFinish={props.onSubmit}>
          <Component {...props} form={form} />
        </Form>
      )
    }
    return WrappedComponent
  }
}
```

**Individual Form Component Updates:**

Each form using `getFieldDecorator` needs update:

```typescript
// Before (antd 3)
{getFieldDecorator('fieldName', {
  rules: [{ required: true, message: 'Required' }]
})(
  <Input />
)}

// After (antd 4)
<Form.Item 
  name="fieldName"
  rules={[{ required: true, message: 'Required' }]}
>
  <Input />
</Form.Item>
```

**Affected Files (manual migration required):**
- `frontend/src/scenes/SSM/components/SSMForm.tsx` - 11 fields
- `frontend/src/scenes/QCLM/components/QCLMForm.tsx` - 24 fields
- `frontend/src/scenes/PAS/components/PASForm/index.tsx` - 14 fields
- `frontend/src/scenes/PAS/components/PASForm/components/InputMutations/index.tsx` - 3 fields
- `frontend/src/shared/components/CodonUsage.tsx` - 5 fields
- `frontend/src/shared/components/ParametersFormSection/index.tsx` - 21 fields
- `frontend/src/shared/components/MinOptMaxInputs/index.tsx` - 5 fields

### Step 1.5: Testing Phase 1

```bash
# Build
cd frontend && npm run build

# Dev server
npm run dev

# Lint
npm run lint

# Type check
npm run types
```

**Test all workflows:**
- [ ] SSM form submission
- [ ] QCLM form submission
- [ ] PAS form submission
- [ ] File uploads
- [ ] Result tables display

### Phase 1 Acceptance Criteria

- [ ] React 18.3.x installed
- [ ] ReactDOM.render → createRoot migration complete
- [ ] React.SFC → React.FC complete
- [ ] TypeScript 5.x installed
- [ ] antd 4.24.x installed
- [ ] @ant-design/icons installed
- [ ] All Icon components migrated (4 files)
- [ ] All Form components migrated (7 files)
- [ ] Build passes
- [ ] Dev server starts
- [ ] All three workflows function correctly

---

## Phase 2: React 19 + antd 5 (Modern)

**Goal:** Upgrade to latest stable versions with CSS-in-JS.

**Duration:** 2-3 days

**Prerequisite:** Phase 1 complete and stable

### Step 2.1: React 19 Upgrade

**Changes to `frontend/package.json`:**
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0"
  }
}
```

**Run codemod:**
```bash
npx react-codemod@latest react19-preset src
```

### Step 2.2: antd 5 Upgrade

**Changes to `frontend/package.json`:**
```json
{
  "dependencies": {
    "antd": "^5.22.0",
    "@ant-design/icons": "^5.5.0"
  }
}
```

**Run codemod:**
```bash
npx -p @ant-design/codemod-v5 antd5-codemod src
```

**Key antd 5 Changes:**

1. **CSS-in-JS** - No more Less files (we don't have any custom Less)
2. **moment.js → day.js** - If using date pickers, migrate to day.js
3. **Remove babel-plugin-import** - Not needed anymore
4. **Component Token system** - For theming

**Update CSS import in `frontend/src/index.tsx`:**
```typescript
// Before (antd 4)
import 'antd/dist/antd.css'

// After (antd 5)
// No import needed! CSS-in-JS handles styles automatically
// Or for reset styles:
import 'antd/dist/reset.css'
```

### Step 2.3: Date Library Migration (if needed)

**If using DatePicker/RangePicker:**
```bash
npm uninstall moment
npm install dayjs
```

**Update DatePicker usage:**
```typescript
// Before
import moment from 'moment'
const value = moment()

// After
import dayjs from 'dayjs'
const value = dayjs()
```

### Step 2.4: Theme Configuration (Optional)

**File: `frontend/vite.config.ts`**
```typescript
// For antd 5 theme customization
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [
          [
            'import',
            {
              libraryName: 'antd',
              libraryDirectory: 'es',
              style: 'css-in-js', // for antd 5
            },
          ],
        ],
      },
    }),
  ],
})
```

### Step 2.5: Testing Phase 2

```bash
# Build
cd frontend && npm run build

# Dev server  
npm run dev

# Lint
npm run lint

# Type check
npm run types
```

### Phase 2 Acceptance Criteria

- [ ] React 19.x installed
- [ ] antd 5.x installed
- [ ] @ant-design/icons 5.x installed
- [ ] moment.js removed (if was used)
- [ ] day.js installed (if date pickers used)
- [ ] CSS imports updated
- [ ] Build passes
- [ ] Dev server starts
- [ ] All three workflows function correctly
- [ ] No console errors
- [ ] Visual regression check

---

## Phase 3: Cleanup & Optimization

**Goal:** Remove legacy code, optimize bundle, update documentation.

**Duration:** 1 day

### Step 3.1: Remove Legacy Dependencies

**Remove from `frontend/package.json`:**
```json
{
  "devDependencies": {
    // Remove if present
    "babel-plugin-import": "remove",
    "less": "remove",
    "less-loader": "remove"
  }
}
```

### Step 3.2: Bundle Analysis

```bash
# Analyze bundle
npm run build -- --mode production
npx vite-bundle-visualizer
```

### Step 3.3: Update Documentation

**Update `frontend/README.md`:**
- React version
- antd version
- Build system (Vite)
- New form patterns

**Update `AGENTS.md`:**
- Update test commands if changed
- Update dependency versions

### Step 3.4: Performance Baseline

| Metric | Before | After |
|--------|--------|-------|
| Dev server startup | ~30s | <1s |
| Hot reload | 2-5s | <100ms |
| Production build | ~60s | ~20s |
| Bundle size | baseline | 20-40% smaller |

### Phase 3 Acceptance Criteria

- [ ] Legacy dependencies removed
- [ ] Bundle size optimized
- [ ] Documentation updated
- [ ] AGENTS.md updated
- [ ] All tests pass
- [ ] CI pipeline green

---

## Risk Analysis & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Form migration breaks workflows | High | Critical | Manual testing each form, keep backup branch |
| Third-party lib incompatibility | Medium | High | Check peer dependencies before upgrade |
| TypeScript errors cascade | Medium | Medium | Upgrade incrementally, fix as you go |
| Visual regression | Medium | Medium | Screenshot comparison, manual review |
| Performance regression | Low | Medium | Bundle analysis, performance profiling |

## Rollback Strategy

Each phase has a dedicated git branch:
- `feat/react-18-antd-4` - Phase 1
- `feat/react-19-antd-5` - Phase 2

If issues found:
1. Revert to previous branch
2. Fix issue on feature branch
3. Re-attempt merge

## Dependencies & Prerequisites

- Node.js 18+ (for React 19)
- npm 9+ or pnpm 8+
- Working Vite build (complete)
- Python 3.11 backend (complete)

## Estimated Timeline

| Phase | Duration | Parallel Work |
|-------|----------|---------------|
| Phase 1 | 2-3 days | Can start E2E test setup |
| Phase 2 | 2-3 days | After Phase 1 stable |
| Phase 3 | 1 day | After Phase 2 stable |
| **Total** | **5-7 days** | |

## References

### React
- [React 18 Upgrade Guide](https://react.dev/blog/2022/03/08/react-18-upgrade-guide)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [React 19 Release Notes](https://react.dev/blog/2024/12/05/react-19)

### Ant Design
- [antd 4 Migration Guide](https://4x.ant.design/docs/react/migration-v4)
- [antd 5 Migration Guide](https://ant.design/docs/react/migration-v5)
- [antd 4 Codemod](https://github.com/ant-design/codemod-v4)
- [antd 5 Codemod](https://github.com/ant-design/codemod-v5)

### TypeScript
- [TypeScript 5 Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html)

---

## Appendix: Complete File Change List

### Phase 1 Files

| File | Change Type | Description |
|------|-------------|-------------|
| `frontend/package.json` | modify | Update dependencies |
| `frontend/tsconfig.json` | modify | Update TS config |
| `frontend/src/index.tsx` | modify | createRoot migration |
| `frontend/src/shared/withForm.ts` | rewrite | Form.create → Form.useForm |
| `frontend/src/shared/components/FileUploadInput/index.tsx` | modify | Icon migration |
| `frontend/src/scenes/PAS/components/PASForm/components/InputMutations/FileUploadMutations.tsx` | modify | Icon migration |
| `frontend/src/scenes/SSM/components/SSMResult/components/SSMResultTable/index.tsx` | modify | Icon migration |
| `frontend/src/scenes/SSM/components/SSMResult/components/SSMResultTable/components/PrimerReportPopover.tsx` | modify | Icon migration |
| `frontend/src/scenes/SSM/components/SSMForm.tsx` | modify | Form migration |
| `frontend/src/scenes/QCLM/components/QCLMForm.tsx` | modify | Form migration |
| `frontend/src/scenes/PAS/components/PASForm/index.tsx` | modify | Form migration |
| `frontend/src/scenes/PAS/components/PASForm/components/InputMutations/index.tsx` | modify | Form migration |
| `frontend/src/shared/components/CodonUsage.tsx` | modify | Form migration |
| `frontend/src/shared/components/ParametersFormSection/index.tsx` | modify | Form migration |
| `frontend/src/shared/components/MinOptMaxInputs/index.tsx` | modify | Form migration |

### Phase 2 Files

| File | Change Type | Description |
|------|-------------|-------------|
| `frontend/package.json` | modify | Update to React 19, antd 5 |
| `frontend/src/index.tsx` | modify | Remove CSS import |
| `frontend/vite.config.ts` | modify | Theme config (optional) |

---

## Next Steps

1. **Review this plan** - Confirm approach and timeline
2. **Create Phase 1 branch** - `feat/react-18-antd-4`
3. **Begin Step 1.1** - React 18 upgrade
4. **Test incrementally** - After each sub-step
