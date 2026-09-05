## Folder Structure

```
frontend/nuxt4/
├── app/                     # Main application directory (Nuxt 4)
│   ├── assets/              # Global CSS, images, fonts
│   │   └── css/             # Main stylesheet (main.css)
│   ├── composables/         # Reusable logic (composables)
│   ├── components/          # Vue components (global & local)
│   ├── pages/               # Page-level components (auto-routing)
│   ├── plugins/             # Nuxt plugins (auth, etc.)
│   ├── public/              # Static assets (favicon, robots.txt)
│   ├── server/              # Server-side code (API routes, middleware)
│   └── utils/               # Helper utilities
│
├── config/                  # Nuxt configuration files
│   ├── nuxt.config.ts       # Main Nuxt configuration
│   ├── pnpm-workspace.yaml  # pnpm workspace definition
│   └── tsconfig.json        # TypeScript compiler options
│
├── public/                  # Public static assets (served directly)
│   ├── favicon.ico          # Website favicon
│   └── robots.txt           # SEO robots file
│
├── tests/                   # Test files (Vitest, Playwright)
│   ├── unit/                # Component/unit tests
│   ├── e2e/                 # End-to-end tests
│   └── setup.ts             # Test setup/teardown
│
├── .env                     # Environment variables (local dev)
├── .env.example             # Example environment file
├── .gitignore               # Git ignore patterns
├── .prettierignore          # Prettier ignore patterns
├── .prettierrc              # Prettier configuration
├── eslint.config.mjs        # ESLint configuration
├── package.json             # Dependencies & scripts
├── pnpm-lock.yaml           # pnpm lockfile
├── pnpm-workspace.yaml      # pnpm workspace configuration
├── tailwind.config.ts       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript compiler settings
```

## Key Files

| File | Purpose |
|------|---------|
| `nuxt.config.ts` | Main Nuxt configuration (modules, routes, plugins) |
| `tsconfig.json` | TypeScript compiler settings |
| `tailwind.config.ts` | Tailwind CSS configuration |
| `package.json` | Dependencies, scripts, and project metadata |
| `pnpm-lock.yaml` | pnpm dependency lockfile |
| `public/` | Static assets served at root path |
| `app/` | Core application files (components, pages, composables) |
| `tests/` | Test suite for frontend components and flows |
| `public/` | Static files that don't need processing (favicon, robots.txt) |

## Development Workflow

1. **Setup**: Install dependencies with `pnpm install`
2. **Develop**: Start dev server with `pnpm dev` (http://localhost:3000)
3. **Build**: Create production build with `pnpm build`
4. **Preview**: Preview production build with `pnpm preview`

## Best Practices

- Use `<script setup>` for component scripts
- Keep components small and focused on one responsibility
- Use composables for shared logic across components
- Leverage Nuxt's auto-imports for auto-registered components and composables
- Follow Tailwind CSS utility-first approach
- Keep public assets in `/public` directory
- Use environment variables in `.env` files (never commit secrets)