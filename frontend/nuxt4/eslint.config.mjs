// https://eslint.org/docs/latest/use/configure/configuration-files-new
// Standalone ESLint flat config (works before `nuxt prepare` generates anything)
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import prettier from 'eslint-config-prettier'

const ignores = [
  'node_modules/**',
  '.nuxt/**',
  '.output/**',
  '.nitro/**',
  '.data/**',
  'dist/**',
  'pnpm-lock.yaml',
  '*.config.{js,ts,mjs,cjs}',
  'eslint.config.mjs'
]

export default [
  { ignores },
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  prettier,
  {
    files: ['**/*.{ts,vue,js,mjs,cjs}'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      },
      globals: {
        // Nuxt auto-imports (kept broad; vue-tsc handles real type diagnostics)
        defineProps: 'readonly',
        defineEmits: 'readonly',
        defineExpose: 'readonly',
        defineOptions: 'readonly',
        defineNuxtConfig: 'readonly',
        useFetch: 'readonly',
        useState: 'readonly',
        useRuntimeConfig: 'readonly',
        useNuxtApp: 'readonly',
        useAsyncData: 'readonly',
        navigateTo: 'readonly',
        useRoute: 'readonly',
        useRouter: 'readonly',
        ref: 'readonly',
        reactive: 'readonly',
        computed: 'readonly',
        watch: 'readonly',
        onMounted: 'readonly',
        onUnmounted: 'readonly',
        onBeforeMount: 'readonly',
        onBeforeUnmount: 'readonly',
        defineStore: 'readonly',
        storeToRefs: 'readonly'
      }
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/html-self-closing': 'off',
      'vue/max-attributes-per-line': 'off',
      'vue/first-attribute-linebreak': 'off',
      'no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
      ],
      'no-console': ['warn', { allow: ['warn', 'error'] }]
    }
  }
]
