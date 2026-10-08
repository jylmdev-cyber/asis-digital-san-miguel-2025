import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
export default defineConfig({output:'static', integrations:[react()], devToolbar:{enabled:false}, site:process.env.SITE_URL || 'https://asis-digital-san-miguel-2025.jimdev.chatgpt.site', base:process.env.BASE_PATH || '/', vite:{build:{chunkSizeWarningLimit:900}}});
