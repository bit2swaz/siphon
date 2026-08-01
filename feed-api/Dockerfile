# feed-api/Dockerfile: build context = repo root.
# Replicates the repo layout (service under /src/feed-api, proto under
# /src/proto/gen/go) so the single `replace => ../proto/gen/go` in go.mod resolves
# identically for local `go build` and this image. Same pattern as user-event-service.
FROM golang:1.25-alpine AS builder
WORKDIR /src
COPY proto/gen/go/ ./proto/gen/go/
COPY feed-api/ ./feed-api/
WORKDIR /src/feed-api
RUN go mod download
RUN go build -o /feed-api ./cmd/server/

FROM alpine:3.20
COPY --from=builder /feed-api /feed-api
EXPOSE 8005
CMD ["/feed-api"]
