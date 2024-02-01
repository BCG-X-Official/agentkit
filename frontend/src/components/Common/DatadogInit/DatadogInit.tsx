// Necessary if using App Router to ensure this file runs on the client
"use client"

import { datadogRum } from "@datadog/browser-rum"
import { env } from "~/env.mjs"

if (env.NEXT_PUBLIC_DATADOG_APPLICATION_ID && env.NEXT_PUBLIC_DATADOG_CLIENT_TOKEN) {
  datadogRum.init({
    applicationId: env.NEXT_PUBLIC_DATADOG_APPLICATION_ID,
    clientToken: env.NEXT_PUBLIC_DATADOG_CLIENT_TOKEN,
    site: "datadoghq.com",
    service: "agentx-public-demo",
    env: "demo",
    version: "1.0.0",
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: "allow",
  })
}

export const DatadogInit = () => {
  // Render nothing - this component is only included so that the init code
  // above will run client-side
  return null
}
