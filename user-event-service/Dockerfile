# user-event-service/Dockerfile: build context = repo root.
# We replicate the repo layout (service under /src/user-event-service, proto under
# /src/proto/gen/go) so the single `replace => ../proto/gen/go` in go.mod resolves
# identically for local `go build` and this image. no Docker-only replace path.
FROM golang:1.25-alpine AS builder
WORKDIR /src
COPY proto/gen/go/ ./proto/gen/go/
COPY user-event-service/ ./user-event-service/
WORKDIR /src/user-event-service
RUN go mod download
RUN go build -o /server ./cmd/server/

FROM alpine:3.20
COPY --from=builder /server /server
EXPOSE 8002
CMD ["/server"]
