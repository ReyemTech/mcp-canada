import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://reyemtech.github.io",
  base: "/mcp-canada",
  integrations: [sitemap()],
});
