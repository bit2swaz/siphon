// ring buffer shared between event writers (interaction poller) and WS readers.
// simple slice ring with mutex, no need for pub/sub bus
package livefeed

import "sync"

type Event struct {
	UserID    string  `json:"user_id"`
	VideoID   string  `json:"video_id"`
	WatchFrac float64 `json:"watch_frac"`
	EventType string  `json:"event_type"`
	TsMs      int64   `json:"ts_ms"`
}

type Ring struct {
	mu   sync.Mutex
	buf  []Event
	head int
	size int
}

func NewRing(capacity int) *Ring {
	return &Ring{buf: make([]Event, capacity), size: capacity}
}

func (r *Ring) Push(e Event) {
	r.mu.Lock()
	r.buf[r.head%r.size] = e
	r.head++
	r.mu.Unlock()
}

func (r *Ring) Last(n int) []Event {
	r.mu.Lock()
	defer r.mu.Unlock()
	if n > r.size {
		n = r.size
	}
	out := make([]Event, 0, n)
	start := r.head - n
	if start < 0 {
		start = 0
	}
	for i := start; i < r.head; i++ {
		out = append(out, r.buf[i%r.size])
	}
	return out
}
