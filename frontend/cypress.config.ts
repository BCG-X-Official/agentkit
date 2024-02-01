// @ts-nocheck

import { addCucumberPreprocessorPlugin } from "@badeball/cypress-cucumber-preprocessor"
import createEsbuildPlugin from "@badeball/cypress-cucumber-preprocessor/esbuild"
import createBundler from "@bahmutov/cypress-esbuild-preprocessor"
import { defineConfig } from "cypress"

export default defineConfig({
  env: {
    SHOW_LANDING_OPTIONS: process.env.NEXT_PUBLIC_LANDING_OPTIONS,
    EMAIL: "cypress",
    PASSWORD: "cypress",
  },
  screenshotOnRunFailure: false,
  e2e: {
    baseUrl: "http://localhost:3000",
    specPattern: "cypress/e2e/features/**/*.feature",
    async setupNodeEvents(
      on: Cypress.PluginEvents,
      config: Cypress.PluginConfigOptions
    ): Promise<Cypress.PluginConfigOptions> {
      await addCucumberPreprocessorPlugin(on, config)

      on(
        "file:preprocessor",
        createBundler({
          plugins: [createEsbuildPlugin(config)],
        })
      )

      return config
    },
  },
})
