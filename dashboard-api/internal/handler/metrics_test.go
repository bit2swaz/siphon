package handler_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/bit2swaz/siphon/dashboard-api/internal/handler"
	"github.com/go-chi/chi/v5"
)

func TestMetricsSnapshot_ReturnsFields(t *testing.T) {
	// use nil db. handler must handle nil gracefully with zero values
	h := handler.NewMetricsHandler(nil)
	r := chi.NewRouter()
	r.Get("/metrics/snapshot", h.Snapshot)

	req := httptest.NewRequest(http.MethodGet, "/metrics/snapshot", nil)
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)

	if rec.Code != 200 {
		t.Fatalf("expected 200 got %d", rec.Code)
	}
	var resp map[string]interface{}
	if err := json.NewDecoder(rec.Body).Decode(&resp); err != nil {
		t.Fatal(err)
	}
	for _, field := range []string{"ctr", "avg_watch_frac", "events_per_sec", "model_version"} {
		if _, ok := resp[field]; !ok {
			t.Errorf("missing field %q in response", field)
		}
	}
}
