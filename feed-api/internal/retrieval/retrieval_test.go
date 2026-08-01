package retrieval_test

import (
	"context"
	"testing"

	"github.com/bit2swaz/siphon/feed-api/internal/retrieval"
)

type mockQdrant struct{}

func (m *mockQdrant) SearchItems(ctx context.Context, userVec []float32, limit int) ([]retrieval.Candidate, error) {
	return []retrieval.Candidate{
		{VideoID: "v001", CreatorID: "c001", Score: 0.9, CreatedAt: 1000, DurationS: 15.0},
		{VideoID: "v002", CreatorID: "c002", Score: 0.8, CreatedAt: 2000, DurationS: 20.0},
	}, nil
}
func (m *mockQdrant) GetUserVec(ctx context.Context, userID string) ([]float32, error) {
	vec := make([]float32, 256)
	return vec, nil
}

type mockRedis struct{}

func (m *mockRedis) ZRevRange(ctx context.Context, key string, stop int64) ([]string, error) {
	return []string{"v003", "v004"}, nil
}
func (m *mockRedis) LRange(ctx context.Context, key string, stop int64) ([]string, error) {
	return []string{"v003"}, nil
}
func (m *mockRedis) HGetAll(ctx context.Context, key string) (map[string]string, error) {
	return map[string]string{"creator_id": "c003", "duration_s": "12.0", "created_at": "3000"}, nil
}

func TestPointID_MatchesPython(t *testing.T) {
	// parity anchor: `python -c "from scripts.idhash import point_id; print(point_id('u000000'))"`
	// md5("u000000")[:8] big-endian: matches scripts/idhash.py:point_id("u000000")
	const want = uint64(5525968826559135932)
	if got := retrieval.PointID("u000000"); got != want {
		t.Fatalf("PointID drift: go=%d python=%d", got, want)
	}
}

func TestRetrieve_DeduplicatesAndMerges(t *testing.T) {
	candidates, err := retrieval.Retrieve(context.Background(), "u000001", &mockQdrant{}, &mockRedis{})
	if err != nil {
		t.Fatal(err)
	}
	// v003 appears in both ANN and trending. should appear once
	seen := map[string]int{}
	for _, c := range candidates {
		seen[c.VideoID]++
	}
	for vid, count := range seen {
		if count > 1 {
			t.Errorf("duplicate candidate: %s appears %d times", vid, count)
		}
	}
	if len(candidates) == 0 {
		t.Fatal("expected candidates, got none")
	}
}
