import base44 from "@base44/vite-plugin";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    base44({
      // Support legacy Base44 SDK imports
      legacySDKImports:
        process.env.BASE44_LEGACY_SDK_IMPORTS === "true",

      hmrNotifier: true,
      navigationNotifier: true,
      analyticsTracker: true,
      visualEditAgent: true,
    }),
    react(),
  ],

  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});