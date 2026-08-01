package ranking_test

import (
	"testing"
	"time"

	"github.com/bit2swaz/siphon/feed-api/internal/ranking"
	"github.com/bit2swaz/siphon/feed-api/internal/retrieval"
)

func TestRerank_RemovesFlagged(t *testing.T) {
	now := time.Now().UnixMilli()
	candidates := []retrieval.Candidate{
		{VideoID: "v001", CreatorID: "c1", Score: 0.9, CreatedAt: now},
		{VideoID: "v002", CreatorID: "c2", Score: 0.8, CreatedAt: now},
		{VideoID: "v003", CreatorID: "c3", Score: 0.7, CreatedAt: now},
	}
	flagged := map[string]bool{"v002": true}
	out := ranking.Rerank(candidates, flagged, now)
	for _, c := range out {
		if c.VideoID == "v002" {
			t.Fatal("flagged video v002 should have been removed")
		}
	}
}

func TestRerank_DiversityWindow(t *testing.T) {
	now := time.Now().UnixMilli()
	candidates := []retrieval.Candidate{
		{VideoID: "v001", CreatorID: "c1", Score: 0.9, CreatedAt: now},
		{VideoID: "v002", CreatorID: "c1", Score: 0.8, CreatedAt: now},
		{VideoID: "v003", CreatorID: "c1", Score: 0.7, CreatedAt: now},
		{VideoID: "v004", CreatorID: "c2", Score: 0.6, CreatedAt: now},
		{VideoID: "v005", CreatorID: "c1", Score: 0.5, CreatedAt: now},
	}
	out := ranking.Rerank(candidates, map[string]bool{}, now)
	for i := 2; i < len(out); i++ {
		if out[i].CreatorID == out[i-1].CreatorID && out[i-1].CreatorID == out[i-2].CreatorID {
			t.Errorf("3 consecutive same creator at positions %d-%d", i-2, i)
		}
	}
}

func TestRerank_FreshnessDecay(t *testing.T) {
	now := time.Now().UnixMilli()
	old := now - int64(72*3600*1000) // 72 hours ago
	candidates := []retrieval.Candidate{
		{VideoID: "fresh", CreatorID: "c1", Score: 0.5, CreatedAt: now},
		{VideoID: "stale", CreatorID: "c2", Score: 0.5, CreatedAt: old},
	}
	out := ranking.Rerank(candidates, map[string]bool{}, now)
	if len(out) >= 2 && out[0].VideoID == "stale" {
		t.Error("expected fresh video to rank above stale video")
	}
}
