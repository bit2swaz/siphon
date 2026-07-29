// Generated proto package as a local Go module so proto-dependent Go services
// (user-event, feed-api, ...) can reference it via a `replace` directive.
// Module path matches the `option go_package` in proto/*.proto; the files live
// at this dir root and declare `package siphon`.
module github.com/bit2swaz/siphon/proto/gen/go/siphon

go 1.25.0

require (
	google.golang.org/grpc v1.82.1
	google.golang.org/protobuf v1.36.11
)

require (
	golang.org/x/net v0.53.0 // indirect
	golang.org/x/sys v0.43.0 // indirect
	golang.org/x/text v0.36.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20260414002931-afd174a4e478 // indirect
)
