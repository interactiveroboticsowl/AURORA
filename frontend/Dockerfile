FROM node:20 AS build

WORKDIR /app

COPY package*.json .

RUN npm ci

COPY . .
RUN npm run build
RUN npm prune --production
FROM node:20 AS run

ENV NODE_ENV=production
ENV PORT=81
EXPOSE 81

WORKDIR /app
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/node_modules ./node_modules
RUN ulimit -c unlimited
ENTRYPOINT ["node", "build"]