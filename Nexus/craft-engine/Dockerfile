FROM node:24-bookworm-slim
WORKDIR /engine
COPY app/craftingdesk/*.js ./math/
COPY craft-engine/*.cjs ./
ENV NODE_ENV=production NODE_OPTIONS=--max-old-space-size=4096
USER 65534:65534
CMD ["node","server.cjs"]
