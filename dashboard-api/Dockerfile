FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /dashboard-api ./cmd/server/

FROM alpine:3.20
COPY --from=builder /dashboard-api /dashboard-api
EXPOSE 8006
CMD ["/dashboard-api"]
