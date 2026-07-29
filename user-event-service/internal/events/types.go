package events

// UserEventData is the payload handler -> publisher. named type so no interface{}
// assertion (which would panic on an anonymous struct) is ever needed
type UserEventData struct {
	UserID    string
	VideoID   string
	EventType string
	Timestamp int64
	WatchFrac float32
}
