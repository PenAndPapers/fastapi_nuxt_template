---
name: frontend
description: Procedure for creating Vue 3 components, Nuxt composables, and Pinia stores. Trigger when creating or updating UI features.
---

# Frontend Implementation Procedure

## Step 1: Define TypeScript Types
1. Map backend Pydantic schemas to frontend interfaces in `frontend/types/`.

## Step 2: State & Data Fetching
1. Build API client composables using `useFetch` / `useAsyncData`.
2. If state spans multiple pages, create a store in `frontend/stores/`.

## Step 3: Vue 3 Components
1. Create reusable UI parts in `frontend/components/`. Use `<script setup lang="ts">`.
2. Assemble component into target page in `frontend/pages/`.
3. Verify component rendering and state updates.