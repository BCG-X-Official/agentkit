import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  /**
   * Specify your server-side environment variables schema here. This way you can ensure the app
   * isn't built with invalid env vars.
   */
  server: {
    NODE_ENV: z.enum(['development', 'test', 'production']),
    NEXTAUTH_SECRET:
    (process.env.NODE_ENV === 'production' && process.env.NEXT_PUBLIC_USE_AUTH === 'true')
        ? z.string().min(1)
        : z.string().optional(), // Optional in development, test and when auth is disabled
    NEXTAUTH_URL: z.preprocess(
      // This makes Vercel deployments not fail if you don't set NEXTAUTH_URL
      // Since NextAuth.js automatically uses the VERCEL_URL if present.
      (str) => process.env.VERCEL_URL ?? str,
      // VERCEL_URL doesn't include `https` so it cant be validated as a URL
      process.env.VERCEL ? z.string().min(1) : z.string().url(),
    ),
    // Add `.min(1) on ID and SECRET if you want to make sure they're not empty
    GITHUB_ID: z.string(),
    GITHUB_SECRET: z.string(),
    NEXT_PUBLIC_ENABLE_MESSAGE_FEEDBACK: z.enum(['true', 'false']).optional().transform((str) => str === 'true'),
    NEXT_PUBLIC_API_URL: z.string().url(),
    NEXT_PUBLIC_USE_AUTH: z.enum(['true', 'false']).default('false').transform((str) => str === 'true'),
  },

  /**
   * Specify your client-side environment variables schema here. This way you can ensure the app
   * isn't built with invalid env vars. To expose them to the client, prefix them with
   * `NEXT_PUBLIC_`.
   */
  client: {
    NEXT_PUBLIC_ENABLE_MESSAGE_FEEDBACK: z.enum(['true', 'false']).optional().transform((str) => str === 'true'),
    NEXT_PUBLIC_API_URL: z.string().url(),
    NEXT_PUBLIC_USE_AUTH: z.enum(['true', 'false']).default('false').transform((str) => str === 'true'),
  },

  /**
   * You can't destruct `process.env` as a regular object in the Next.js edge runtimes (e.g.
   * middlewares) or client-side so we need to destruct manually.
   */
  runtimeEnv: {
    NODE_ENV: process.env.NODE_ENV,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    GITHUB_ID: process.env.GITHUB_ID,
    GITHUB_SECRET: process.env.GITHUB_SECRET,
    NEXT_PUBLIC_ENABLE_MESSAGE_FEEDBACK: process.env.NEXT_PUBLIC_ENABLE_MESSAGE_FEEDBACK,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_USE_AUTH: process.env.NEXT_PUBLIC_USE_AUTH,
    // NEXT_PUBLIC_CLIENTVAR: process.env.NEXT_PUBLIC_CLIENTVAR,
  },
});
