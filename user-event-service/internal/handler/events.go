package handler

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"

	"github.com/bit2swaz/siphon/user-event-service/internal/events"
)

var (
	eventsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "user_event_total", Help: "User events received",
	}, []string{"event_type"})
	validTypes = map[string]bool{
		"watch": true, "like": true, "share": true, "skip": true, "replay": true,
	}
)

type EventRequest struct {
	UserID     string `json:"user_id"`
	VideoID    string `json:"video_id"`
	EventType  string `json:"event_type"`
	WatchMs    int64  `json:"watch_ms"`
	DurationMs int64  `json:"duration_ms"`
}

// Publisher and SessionRecorder are interfaces so tests can mock them.
// Publish takes the shared named type (NOT interface{}) so there is no
// runtime type assertion that could panic on an anonymous struct.
type Publisher interface {
	Publish(event events.UserEventData) error
}
type SessionRecorder interface {
	Record(userID, videoID string) error
}

type EventHandler struct {
	pub Publisher
	ses SessionRecorder
}

func NewEventHandler(pub Publisher, ses SessionRecorder) *EventHandler {
	return &EventHandler{pub: pub, ses: ses}
}

func (h *EventHandler) Handle(w http.ResponseWriter, r *http.Request) {
	var req EventRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid json"}`, http.StatusUnprocessableEntity)
		return
	}
	if req.UserID == "" || req.VideoID == "" || !validTypes[req.EventType] {
		http.Error(w, `{"error":"invalid fields"}`, http.StatusUnprocessableEntity)
		return
	}

	watchFrac := float32(0)
	if req.DurationMs > 0 {
		watchFrac = float32(req.WatchMs) / float32(req.DurationMs)
		if watchFrac > 1.0 {
			watchFrac = 1.0
		}
	}

	_ = h.pub.Publish(events.UserEventData{
		UserID:    req.UserID,
		VideoID:   req.VideoID,
		EventType: req.EventType,
		Timestamp: time.Now().UnixMilli(),
		WatchFrac: watchFrac,
	})

	_ = h.ses.Record(req.UserID, req.VideoID)

	eventsTotal.WithLabelValues(req.EventType).Inc()
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"status":"ok"}`))
}
