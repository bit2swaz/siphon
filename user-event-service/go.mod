module github.com/bit2swaz/siphon/user-event-service

go 1.25.0

// proto generated code is a local (unpublished) Go module. both local build/test
// and the docker image (which replicates the repo layout) resolve it via this
// one relative path (see Dockerfile). a repo-root go.work is the phase 9 cleanup
require github.com/bit2swaz/siphon/proto/gen/go/siphon v0.0.0

replace github.com/bit2swaz/siphon/proto/gen/go/siphon => ../proto/gen/go

require (
	github.com/go-chi/chi/v5 v5.1.0
	github.com/prometheus/client_golang v1.19.1
	github.com/redis/go-redis/v9 v9.21.0
	github.com/segmentio/kafka-go v0.4.51
	google.golang.org/protobuf v1.36.11
)

require (
	github.com/beorn7/perks v1.0.1 // indirect
	github.com/cespare/xxhash/v2 v2.3.0 // indirect
	github.com/klauspost/compress v1.15.9 // indirect
	github.com/pierrec/lz4/v4 v4.1.15 // indirect
	github.com/prometheus/client_model v0.5.0 // indirect
	github.com/prometheus/common v0.48.0 // indirect
	github.com/prometheus/procfs v0.12.0 // indirect
	go.uber.org/atomic v1.11.0 // indirect
	golang.org/x/net v0.53.0 // indirect
	golang.org/x/sys v0.43.0 // indirect
	golang.org/x/text v0.36.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20260414002931-afd174a4e478 // indirect
	google.golang.org/grpc v1.82.1 // indirect
)
