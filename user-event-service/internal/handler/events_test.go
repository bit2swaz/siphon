package handler_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/go-chi/chi/v5"

	"github.com/bit2swaz/siphon/user-event-service/internal/events"
	"github.com/bit2swaz/siphon/user-event-service/internal/handler"
)

type mockPublisher struct{ called bool }

func (m *mockPublisher) Publish(_ events.UserEventData) error { m.called = true; return nil }

type mockSession struct{ called bool }

func (m *mockSession) Record(_, _ string) error { m.called = true; return nil }

func TestPostEvent_ValidWatch(t *testing.T) {
	pub := &mockPublisher{}
	ses := &mockSession{}
	h := handler.NewEventHandler(pub, ses)

	r := chi.NewRouter()
	r.Post("/events", h.Handle)

	body, _ := json.Marshal(map[string]interface{}{
		"user_id": "u000001", "video_id": "v000001",
		"event_type": "watch", "watch_ms": 7500, "duration_ms": 15000,
	})
	req := httptest.NewRequest(http.MethodPost, "/events", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d: %s", rec.Code, rec.Body.String())
	}
	if !pub.called {
		t.Fatal("expected publisher to be called")
	}
	if !ses.called {
		t.Fatal("expected session recorder to be called")
	}
}

func TestPostEvent_InvalidEventType(t *testing.T) {
	h := handler.NewEventHandler(&mockPublisher{}, &mockSession{})
	r := chi.NewRouter()
	r.Post("/events", h.Handle)

	body, _ := json.Marshal(map[string]interface{}{
		"user_id": "u1", "video_id": "v1", "event_type": "explode",
	})
	req := httptest.NewRequest(http.MethodPost, "/events", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)
	if rec.Code != http.StatusUnprocessableEntity {
		t.Fatalf("expected 422, got %d", rec.Code)
	}
}
