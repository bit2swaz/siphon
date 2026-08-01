package handler_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/go-chi/chi/v5"

	"github.com/bit2swaz/siphon/feed-api/internal/handler"
	"github.com/bit2swaz/siphon/feed-api/internal/retrieval"
)

type mockQdrant struct{}

func (m *mockQdrant) GetUserVec(_ context.Context, _ string) ([]float32, error) {
	return make([]float32, 256), nil
}
func (m *mockQdrant) SearchItems(_ context.Context, _ []float32, limit int) ([]retrieval.Candidate, error) {
	now := time.Now().UnixMilli()
	return []retrieval.Candidate{
		{VideoID: "v001", CreatorID: "c1", Score: 0.9, CreatedAt: now, DurationS: 15},
		{VideoID: "v002", CreatorID: "c2", Score: 0.8, CreatedAt: now, DurationS: 20},
	}, nil
}

type mockRedis2 struct{}

func (m *mockRedis2) ZRevRange(_ context.Context, _ string, _ int64) ([]string, error) { return nil, nil }
func (m *mockRedis2) LRange(_ context.Context, _ string, _ int64) ([]string, error)    { return nil, nil }
func (m *mockRedis2) HGetAll(_ context.Context, _ string) (map[string]string, error) {
	return map[string]string{}, nil
}

type mockScorer struct{}

func (m *mockScorer) ScoreBatch(_ context.Context, _ []float32, candidates []retrieval.Candidate) ([]retrieval.Candidate, int32, error) {
	return candidates, 1, nil
}

type mockFlags struct{}

func (m *mockFlags) IsFlagged(_ context.Context, _ string) (bool, error) { return false, nil }

func TestFeedHandler_Returns200WithFeed(t *testing.T) {
	h := handler.NewFeedHandler(&mockQdrant{}, &mockRedis2{}, &mockScorer{}, &mockFlags{})
	r := chi.NewRouter()
	r.Get("/feed", h.Handle)

	req := httptest.NewRequest(http.MethodGet, "/feed?user_id=u000001", nil)
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)

	if rec.Code != 200 {
		t.Fatalf("expected 200 got %d: %s", rec.Code, rec.Body.String())
	}
	var resp map[string]interface{}
	if err := json.NewDecoder(rec.Body).Decode(&resp); err != nil {
		t.Fatal(err)
	}
	if resp["user_id"] != "u000001" {
		t.Errorf("expected user_id u000001, got %v", resp["user_id"])
	}
	feed, ok := resp["feed"].([]interface{})
	if !ok || len(feed) == 0 {
		t.Fatal("expected non-empty feed")
	}
}

func TestFeedHandler_MissingUserID_Returns400(t *testing.T) {
	h := handler.NewFeedHandler(&mockQdrant{}, &mockRedis2{}, &mockScorer{}, &mockFlags{})
	r := chi.NewRouter()
	r.Get("/feed", h.Handle)

	req := httptest.NewRequest(http.MethodGet, "/feed", nil)
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)
	if rec.Code != 400 {
		t.Fatalf("expected 400 got %d", rec.Code)
	}
}
