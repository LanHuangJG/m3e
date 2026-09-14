import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const docs = defineCollection({
  loader: glob({ pattern: "**/*.mdx", base: "./src/content/docs" }),
  schema: z.object({
    title: z.string(),
    description: z.string().default(""),
    summary: z.string().default(""),
    // 语言 + 章节 + 排序，用来生成本地化导航
    section: z.enum(["getting-started", "styles", "frameworks", "components"]),
    category: z
      .enum(["actions", "communication", "containment", "navigation", "selection", "basics"])
      .default("basics"),
    order: z.number().default(0),
    toc: z.boolean().default(true),
  }),
});

export const collections = { docs };
