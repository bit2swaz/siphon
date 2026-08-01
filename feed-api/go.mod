module github.com/bit2swaz/siphon/feed-api

go 1.25.0

require (
	github.com/bit2swaz/siphon/proto/gen/go/siphon v0.0.0-00010101000000-000000000000
	github.com/go-chi/chi/v5 v5.1.0
	github.com/prometheus/client_golang v1.19.1
	github.com/qdrant/go-client v1.18.3
	github.com/redis/go-redis/v9 v9.5.3
	google.golang.org/grpc v1.83.0
)

require (
	github.com/beorn7/perks v1.0.1 // indirect
	github.com/cespare/xxhash/v2 v2.3.0 // indirect
	github.com/dgryski/go-rendezvous v0.0.0-20200823014737-9f7001d12a5f // indirect
	github.com/prometheus/client_model v0.5.0 // indirect
	github.com/prometheus/common v0.48.0 // indirect
	github.com/prometheus/procfs v0.12.0 // indirect
	golang.org/x/net v0.55.0 // indirect
	golang.org/x/sys v0.45.0 // indirect
	golang.org/x/text v0.37.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20260526163538-3dc84a4a5aaa // indirect
	google.golang.org/protobuf v1.36.11 // indirect
)

replace github.com/bit2swaz/siphon/proto/gen/go/siphon => ../proto/gen/go
