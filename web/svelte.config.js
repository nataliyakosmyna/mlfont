import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** Set BASE_PATH=/mlfont for GitHub Pages project sites (see .github/workflows/pages.yml). */
const base = process.env.BASE_PATH ?? '';

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    paths: { base }
  }
};
