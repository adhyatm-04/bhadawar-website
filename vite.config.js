import { cpSync, existsSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { defineConfig } from 'vite';

const root = process.cwd();

export default defineConfig({
  publicDir: false,
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:4175'
    }
  },
  plugins: [{
    name: 'copy-restaurant-assets',
    closeBundle() {
      const source = resolve(root, 'assets');
      const destination = resolve(root, 'dist', 'assets');
      if (!existsSync(source)) return;
      mkdirSync(destination, { recursive: true });
      cpSync(source, destination, { recursive: true, force: true });
    }
  }],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    minify: 'oxc',
    cssMinify: true,
    sourcemap: false,
    rollupOptions: {
      input: {
        home: resolve(root, 'index.html'),
        account: resolve(root, 'account.html'),
        team: resolve(root, 'team.html'),
        corporate: resolve(root, 'corporate.html'),
        photoCredits: resolve(root, 'photo-credits.html')
      }
    }
  }
});
