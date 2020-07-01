# Mutation Maker Frontend

## Overview

This is a frontend application for Mutation Maker.

Landing page presents links to three workflows (SSM, QCLM and PAS). Each workflow consists of Input Form and Results Report. 

Results are displayed in Interactive Table, Feature Viewer and Excel file.

### Packages

* TypeScript
* React (Create React App)
* Recompose
* React-router
* Ant Design
* Axios
* UUID
* XLSX
* file-saver
* lodash
* ramda

### Repository overview

Repository is created with [create-react-app](https://github.com/facebook/create-react-app)

Repository is structured along the lines of [How to better organize your react applications](https://medium.com/@alexmngn/how-to-better-organize-your-react-applications-2fd3ea1920f1).

Three main screens are defined in `src/scenes/SSM/index.tsx`, `src/scenes/QCLM/index.tsx`, `src/scenes/PAS/index.tsx`. They are based on `src/shared/components/WorkflowScene.tsx` which is the heart of this application.

### Application state

The state is provided from `src/App.tsx` via HOC `src/shared/components/withJobStore.ts`. State also serves as a cache (non-persistent) in order to save some network traffic. The state is explicitly propagated (with and/or via handlers) via props.

There are more local states handled via `recompose` for example in `src/shared/components/WorkflowScene.tsx` by utilizing `src/shared/components/withCurrentStepState.ts`. This approach is preferred to the React stateful components (except for `src/shared/components/FeatureViewerComponent/index.tsx`).

### API interaction

The application interacts with backend API via `src/shared/components/withJobStore.ts` which internally uses `src/services/api.ts`. Results are then later parsed and transformed to display friendly format in `src/shared/lib/ResultsData.ts` (@TODO@ this should be moved to somewhere else as `src/shared/lib` should contain just type definitions).

@TODO@

- API data is not validated as of now (there should be validations on API layer, throwing an error in case data is not in correct shape, currently it is just casted (to satisfy TypeScript))

### FeatureViewer

FeatureViewer is used via `src/shared/components/FeatureViewerComponent/index.tsx`. This component is used in all workflows. FeatureViewer itself does not have React friendly API, so it is somehow hidden under the hood in React stateful component.

@TODO@
- component unmount should do some destroy actions on the FeatureViewer objects

A lot of the complexity of the application is hidden in the connection of data table display and the widget. Because of a stateful API of the widget a lot of conditional checks and then side effects are triggered in lifecycle hooks.

