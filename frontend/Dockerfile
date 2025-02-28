FROM node:18-alpine@sha256:b17bf243e453f407ac0acf47d55fe08ae8b5a63ae3c1bd62f474bd0eb1c4c467 AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN yarn global add pnpm && pnpm i --no-frozen-lockfile

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Declare all build args are env vars for build
#ARG GITHUB_ID
#ENV GITHUB_ID ${GITHUB_ID}
#ARG GITHUB_SECRET
#ENV GITHUB_SECRET ${GITHUB_SECRET}
#ARG NEXTAUTH_SECRET
#ENV NEXTAUTH_SECRET ${NEXTAUTH_SECRET}
#ARG NEXTAUTH_URL
#ENV NEXTAUTH_URL ${NEXTAUTH_URL}
#ARG NEXT_PUBLIC_API_URL
#ENV NEXT_PUBLIC_API_URL ${NEXT_PUBLIC_API_URL}

RUN yarn run prisma:generate
RUN yarn run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
