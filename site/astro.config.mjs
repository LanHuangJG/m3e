import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";

// TODO: 部署时改成真实域名（sitemap / canonical 会用它）
export default defineConfig({
  site: "https://m3e.example.com",
  trailingSlash: "always",
  build: { format: "directory" },
  integrations: [mdx(), sitemap()],
  prefetch: { prefetchAll: true, defaultStrategy: "viewport" },
  markdown: {
    shikiConfig: { themes: { light: "github-light", dark: "github-dark" } },
  },
  i18n: {
    defaultLocale: "en",
    locales: ["en", "zh"],
    routing: { prefixDefaultLocale: false },
  },
});
