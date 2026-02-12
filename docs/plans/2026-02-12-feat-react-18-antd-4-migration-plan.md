---
title: React 18 and antd 4+ Migration
type: feat
date: 2026-02-12
---

# React 18 and antd 4+ Migration Plan

## Overview

Upgrade the Mutation Maker frontend from React 16 + antd 3 to React 18 + antd 4+ to ensure compatibility with modern tooling, improved performance, and security updates.

## Current State

| Package       | Current Version | Target Version  |
| ------------- | --------------- | --------------- |
| React         | 16.14.0         | 18.x            |
| antd          | 3.26.20         | 4.x or 5.x      |
| react-scripts | 5.0.1           | Migrate to Vite |
| TypeScript    | 4.9.5           | 5.x             |

## Problem Statement

The current frontend uses deprecated technologies:

- React 16 is EOL (end of life)
- antd 3 has known security issues
- Create React App is deprecated (no longer maintained)
- Modern libraries require newer React versions

### Research Insights

**Why now matters:**
- CRA officially deprecated as of early 2025
- Many libraries now require React 18+ minimum
- React 19 is now stable (December 2024) - consider jumping to 18.3 first for smoother future upgrades

### Performance Impact

| Metric | Before | After (estimated) |
|--------|--------|------------------|
| Dev server startup | ~30s+ | <1s |
| Hot reload | 2-5s | <100ms |
| Production build | ~60s | ~20s |
| Bundle size | baseline | 20-40% smaller |

## TypeScript Changes

### Named Exports for React Types

In React 18+ with TypeScript 5+, prefer named imports over `React.` namespace:

```typescript
// Before (React 16 style)
import React from 'react';
const MyComponent: React.FC<Props> = (props) => ...

// After (React 18+ recommended style)
import type { FC, FCWithChildren } from 'react';
const MyComponent: FC<Props> = (props) => ...

// Or standard function component (most flexible)
function MyComponent(props: Props): JSX.Element { ... }

// With children
type PropsWithChildren = {
  children?: React.ReactNode
};
const MyComponent: FC<PropsWithChildren> = ({ children }) => ...
```

## Proposed Solution

### Phase 1: React 18 Upgrade

1. Update `package.json` dependencies:
   - `react`: ^18.2.0
   - `react-dom`: ^18.2.0
   - `@types/react`: ^18.2.0
   - `@types/react-dom`: ^18.2.0

2. Fix React.FC vs React.SFC TypeScript types
   - Replace `React.SFC` with `React.FC` or standard function components

3. Update entry point for createRoot API:
   ```typescript
   // frontend/src/index.tsx
   // Before (React 16)
   import React from 'react';
   import ReactDOM from 'react-dom';
   import App from './App';
   
   ReactDOM.render(<App />, document.getElementById('root'));
   
   // After (React 18)
   import { createRoot } from 'react-dom/client';
   import App from './App';
   
   const root = createRoot(document.getElementById('root')!);
   root.render(<App />);
   ```

4. Handle StrictMode changes (effects run twice in dev)

5. Run codemod for automatic fixes:
   ```bash
   npx types-react-codemod@latest preset-18 src
   ```

### Phase 2: antd 4+ Upgrade

1. Install `@ant-design/icons` ^4.x or ^5.x

2. Migrate Icon components:

   ```typescript
   // Before (antd 3)
   import { Icon } from 'antd';
   <Icon type="check" />

   // After (antd 4+)
   import { CheckOutlined } from '@ant-design/icons';
   <CheckOutlined />
   ```

3. Migrate Form API:

   ```typescript
   // Before (antd 3)
   Form.create()
   getFieldDecorator('field', rules)(<Input />)

   // After (antd 4+)
   const [form] = Form.useForm()
   <Form.Item name="field" rules={rules}><Input /></Form.Item>
   ```

4. Run official codemod:
   ```bash
   npx -p @ant-design/codemod-v4 antd4-codemod src
   ```

### Phase 3: Build System Migration (CRA → Vite)

Replace Create React App with Vite for better performance and modern tooling.

**Why Vite?**
- Significantly faster dev server startup (under 1s vs 30s+ for CRA)
- Hot Module Replacement (HMR) is instantaneous
- Built-in support for TypeScript, CSS modules, PostCSS
- Smaller bundle sizes with rollup-based production builds
- Active maintenance and ecosystem support
- CRA is officially deprecated

**Migration Steps:**

1. Install Vite and plugins:
   ```bash
   npm uninstall react-scripts
   npm install --save-dev vite @vitejs/plugin-react
   ```

2. Create `vite.config.ts`:
   ```typescript
   import { defineConfig } from 'vite';
   import react from '@vitejs/plugin-react';

   export default defineConfig({
     plugins: [react()],
     server: {
       port: 3000,
       proxy: {
         '/v1': 'http://localhost:8000'
       }
     },
     build: {
       outDir: 'build'
     }
   });
   ```

3. Move `public/index.html` to root as `index.html` and update:
   ```html
   <script type="module" src="/src/index.tsx"></script>
   ```

4. Update npm scripts in `package.json`:
   ```json
   {
     "scripts": {
       "dev": "vite",
       "build": "tsc && vite build",
       "preview": "vite preview",
       "test": "vitest"
     }
   }
   ```

5. Handle environment variables (CRA → Vite):
   - `REACT_APP_*` → `VITE_*`
   - Access via `import.meta.env.VITE_*`

6. Install Vitest for testing (optional):
   ```bash
   npm install --save-dev vitest @testing-library/react jsdom
   ```

**Potential Issues:**
- JSX files need `.jsx` or `.tsx` extensions in imports
- Some webpack-specific imports may need adjustment
- Environment variable handling differs

## Technical Considerations

### Breaking Changes to Handle

**React 18:**

- `ReactDOM.render` → `createRoot`
- `React.SFC` deprecated → use `React.FC` or standard functions
- Automatic batching (may affect timing)
- StrictMode double-invokes effects in dev

**antd 4+:**

- Icon: string type → separate component imports
- Form: `Form.create()` → `Form.useForm()`
- Various prop name changes

### Edge Cases and Known Issues

**React 18:**
1. **setTimeout in effects**: If code relies on timing between renders, may need adjustment due to automatic batching
2. **StrictMode**: Effects run twice in dev - ensure cleanup functions are idempotent
3. **useEffect dependencies**: May need review if relying on specific render counts

**antd 4+:**
1. **Form validation**: `validateTrigger` behavior changed - use `onChange` instead of `onBlur`
2. **DatePicker**: Use `picker` prop instead of separate components
3. **Table nested dataIndex**: Use array syntax `['user', 'name']` instead of string `'user.name'`

### Rollback Plan

1. Keep backup of `package.json` and `package-lock.json`
2. Test each phase independently before proceeding
3. Use git branches for each phase
4. If issues occur:
   - React 18: Revert to React 17 (most compatible)
   - antd 4+: Use `@ant-design/compatible` for legacy support
   - Vite: Revert to react-scripts (requires reverting package.json)

## Files to Modify

1. `frontend/package.json` - Update dependencies
2. `frontend/src/index.tsx` - createRoot migration
3. `frontend/src/App.tsx` - Potentially needs updates
4. All components using `Icon` from antd
5. All components using `Form.create()`

## Affected Components (Icon Usage)

- `frontend/src/scenes/PAS/components/PASForm/components/InputMutations/FileUploadMutations.tsx`
- `frontend/src/shared/components/FileUploadInput/index.tsx`
- `frontend/src/shared/components/WorkflowSteps/index.tsx`
- `frontend/src/scenes/SSM/components/SSMResult/components/SSMResultTable/index.tsx`
- `frontend/src/scenes/SSM/components/SSMResult/components/SSMResultTable/components/PrimerReportPopover.tsx`

## Affected Components (Form Usage)

- All form components using `Form.create()` pattern

## Acceptance Criteria

- [ ] React upgraded to 18.x
- [ ] antd upgraded to 4.x or 5.x
- [ ] TypeScript uses named exports (FC from 'react' instead of React.FC)
- [ ] Build system migrated from CRA to Vite
- [ ] All TypeScript errors resolved
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Frontend starts without errors (`npm start`)
- [ ] All forms work correctly
- [ ] All icons display correctly

## Testing Requirements

- Run `npm run build` to verify production build
- Run `npm start` to verify development server
- Test all three workflows: SSM, QCLM, PAS
- Verify file uploads work
- Verify result tables display correctly

## Dependencies & Risks

| Risk                        | Mitigation                     |
| --------------------------- | ------------------------------ |
| Breaking changes in antd 4+ | Use codemod tool, manual fixes |
| React 18 StrictMode issues  | Disable temporarily if needed  |
| TypeScript errors           | Fix incrementally              |
| Test failures               | Update tests or fix code       |

## Alternative Approaches

1. **Stay on React 16 + antd 3** - Not recommended (security risks)
2. **Gradual migration** - Migrate component by component (lower risk, longer timeline)
3. **Skip antd 4, go to antd 5** - More changes but longer support

## References

### React 18
- [React 18 Upgrade Guide](https://react.dev/blog/2022/03/08/react-18-upgrade-guide)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [React 16 → 18 migration experiences](https://inside.caratlane.com/react-18-upgrade-journey-migrating-from-react-16-to-react-18-145d850613fd)
- [SonarQube React 18 lessons](https://securityboulevard.com/2024/01/lessons-learned-upgrading-to-react-18-in-sonarqube/)
- [Codemen: React 18 migration](https://medium.com/@gadnandev/how-to-move-to-react-18-a-step-by-step-guide-cdaf0ba3728d)

### antd 4+/5
- [antd 4 Migration Guide](https://4x.ant.design/docs/react/migration-v4)
- [Official Codemod Tool](https://github.com/ant-design/codemod-v4)

### Vite Migration
- [Vite Official Migration Guide](https://vite.dev/guide/migration)
- [CRA to Vite Step-by-Step](https://dev.to/sahi11k/migrating-from-create-react-app-to-vite-a-step-by-step-guide-1b4k)
- [Real-world CRA to Vite Migration](https://klimer.eu/2024/07/06/migrating-from-create-react-app-to-vite/)

## Implementation Estimate

- React 18 upgrade: 2-4 hours
- antd 4+ upgrade: 4-8 hours (most time in Icon/Form changes)
- Vite migration: 2-4 hours
- Testing/fixes: 2-4 hours
- **Total: 2-3 days**

---

## Enhancement Summary

**Deepened on:** 2026-02-12

### Key Improvements Added:
1. **Detailed createRoot migration code** - Exact code for updating `index.tsx`
2. **Vite migration enhanced** - Specific steps including index.html handling, env variables, Vitest
3. **Edge cases documented** - Known issues with each phase and how to handle
4. **Rollback plan** - How to recover if issues occur
5. **Performance metrics** - Expected improvements with numbers
6. **Codemod commands** - Automated tools to help with migration

### New Sections:
- Research Insights (why now matters)
- Performance Impact table
- Edge Cases and Known Issues
- Rollback Plan
