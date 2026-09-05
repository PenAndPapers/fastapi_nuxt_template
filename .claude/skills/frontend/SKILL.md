---
name: frontend-engineer
description: Standards for Nuxt 4, Vue 3, TypeScript, composables, SFC, components, state management (Pinia), and CSS (Tailwind). Load when building UI components, pages, or client-side logic.
---

# Frontend Skill Rules

## Framework & Structure
- **Nuxt 4** with **Vue 3** `<script setup>` SFCs.
- File-based routing under `app/pages/`.
- Auto-imports for composables, components, utils (`nuxt.config.ts`).
- Use `app/` directory (Nuxt 4 default).

## TypeScript
- Strict mode enabled (`tsconfig.json`).
- Prefer `interface` over `type` for object shapes.
- Use `defineProps<{}>()` and `defineEmits<{}>` with type inference.
- Leverage Nuxt's auto-generated types (`#imports`).

## Composables
- Extract reusable logic into `app/composables/use*.ts`.
- Return `ref`/`computed` for reactive state.
- Use `useAsyncData` / `useFetch` for server/data fetching.
- Keep composables **pure** (no side effects outside lifecycle).

## Components
- **PascalCase** filenames (`UserCard.vue`).
- Single responsibility: presentational vs. container.
- Use `defineSlots()` for typed slots.
- Prefer `<script setup>`; avoid `setup()` function.
- Global components in `app/components/` (auto-registered).

## State Management (Pinia)
- One store per domain (`stores/auth.ts`, `stores/ui.ts`).
- Use **setup stores** (`defineStore('auth', () => { ... })`).
- Persist sensitive state with `pinia-plugin-persistedstate` (secure storage).
- Access via `useAuthStore()` in components/composables.

## Styling (Tailwind CSS)
- Utility-first; avoid custom CSS unless necessary.
- Use `@apply` sparingly in `app/assets/css/main.css`.
- Dark mode via `class` strategy (`dark:` variants).
- Responsive: `mobile-first` breakpoints (`sm:`, `md:`, `lg:`, `xl:`).

## Data Fetching
- `useFetch('/api/...')` for SSR-friendly calls.
- `useAsyncData(key, handler)` for complex logic.
- Handle loading/error states via returned `pending`, `error`, `data`.
- Use `$fetch` for client-only navigation.

## Performance
- Code-split via Nuxt routes (automatic).
- Lazy-load heavy components with `defineAsyncComponent`.
- Optimize images: Nuxt Image (`<NuxtImg>`).
- Minimize bundle: analyze with `pnpm build --analyze`.

## Testing
- Unit: `vitest` + `@vue/test-utils` (components/composables).
- E2E: `playwright` (critical user flows).
- Mock API with `msw` or `vi.mock()`.

## Code Quality
- Lint: `eslint.config.mjs` (Vue, TS, Nuxt plugins).
- Format: `prettier` (single quotes, trailing commas).
- Type-check: `nuxt typecheck` (runs `vue-tsc`).