FROM node:22-alpine AS base

FROM base AS deps
WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile

FROM base AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN yarn build

FROM base AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/build ./build
COPY --from=deps --chown=nextjs:nodejs /app/package.json /app/yarn.lock ./
RUN yarn install --production --ignore-scripts

USER nextjs

EXPOSE 3000
ENV PORT="3000"
ENV HOSTNAME="0.0.0.0"

CMD ["node", "build"]