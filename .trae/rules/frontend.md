---
alwaysApply: false
description: Standards for Vue 3, Nuxt, TypeScript, Tailwind CSS, and UI component architecture.
globs:
  - "frontend/nuxt/**/*.vue"
  - "frontend/nuxt/**/*.ts"
  - "frontend/nuxt/**/*.js"
  - "frontend/nuxt/**/*.css"
  - "frontend/nuxt/**/*.scss"
---

# Frontend Rules (Vue 3 / Nuxt)

## Component Architecture
- Build UI components using **Vue 3 Composition API** (`<script setup lang="ts">`).
- Keep components modular, and single-purpose; extract reusable UI parts.
- Use local component state where possible; reserve **Pinia** for state shared across multiple routes.
- Follow test-driven development (TDD) practices for unit testing.

## API Integration & Typing
- Fetch data using Nuxt composables (`useFetch`, `useAsyncData`).
- Ensure all API response objects explicitly match backend Pydantic DTO interface types.