import { defineConfig } from "vitest/config";

import { playwright } from "@vitest/browser-playwright";
import deno from "@deno/vite-plugin";

export default defineConfig({
  plugins: [deno()],
  test: {
    globals: true,
    browser: {
      provider: playwright({
        launchOptions: {
          // needed to access WebGL in headless
          args: ["--use-gl=angle", "--use-angle=swiftshader"],
        },
      }),
      enabled: true,
      instances: [
        { browser: "chromium", headless: true },
      ],
    },
  },
});
