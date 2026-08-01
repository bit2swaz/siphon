package handler

import (
	"context"
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"

	"github.com/bit2swaz/siphon/feed-api/internal/ranking"
	"github.com/bit2swaz/siphon/feed-api/internal/retrieval"
)

var feedLatency = promauto.NewHistogram(prometheus.HistogramOpts{
	Name:    "feed_latency_ms",
	Help:    "Feed API latency in ms",
	Buckets: []float64{10, 25, 50, 100, 150, 200, 300, 500},
})

type Scorer interface {
	ScoreBatch(ctx context.Context, userEmbed []float32, candidates []retrieval.Candidate) ([]retrieval.Candidate, int32, error)
}
type FlagChecker interface {
	IsFlagged(ctx context.Context, videoID string) (bool, error)
}

type FeedHandler struct {
	retriever retrieval.QdrantSearcher
	redis     retrieval.RedisClient
	scorer    Scorer
	flags     FlagChecker
}

func NewFeedHandler(q retrieval.QdrantSearcher, rdb retrieval.RedisClient, sc Scorer, fl FlagChecker) *FeedHandler {
	return &FeedHandler{retriever: q, redis: rdb, scorer: sc, flags: fl}
}

type feedItem struct {
	VideoID   string  `json:"video_id"`
	Score     float64 `json:"score"`
	Rank      int     `json:"rank"`
	CreatorID string  `json:"creator_id"`
	DurationS float64 `json:"duration_s"`
}

type feedResponse struct {
	UserID       string     `json:"user_id"`
	Feed         []feedItem `json:"feed"`
	ModelVersion int32      `json:"model_version"`
	LatencyMs    int64      `json:"latency_ms"`
}

func (h *FeedHandler) Handle(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	userID := r.URL.Query().Get("user_id")
	limit := 20
	if l := r.URL.Query().Get("limit"); l != "" {
		if n, err := strconv.Atoi(l); err == nil && n > 0 && n <= 100 {
			limit = n
		}
	}
	if userID == "" {
		http.Error(w, `{"error":"user_id required"}`, http.StatusBadRequest)
		return
	}

	ctx := r.Context()
	w.Header().Set("Content-Type", "application/json")

	// stage 1: retrieval
	candidates, err := retrieval.Retrieve(ctx, userID, h.retriever, h.redis)
	if err != nil || len(candidates) == 0 {
		json.NewEncoder(w).Encode(feedResponse{UserID: userID, Feed: []feedItem{}, LatencyMs: time.Since(start).Milliseconds()})
		return
	}

	// stage 2: ranking via model-server gRPC (falls back to retrieval order on failure)
	userVec, _ := h.retriever.GetUserVec(ctx, userID)
	ranked, modelVer, _ := h.scorer.ScoreBatch(ctx, userVec, candidates)

	// stage 3: re-ranking (safety filter + freshness + diversity)
	flagged := map[string]bool{}
	for _, c := range ranked {
		if ok, _ := h.flags.IsFlagged(ctx, c.VideoID); ok {
			flagged[c.VideoID] = true
		}
	}
	reranked := ranking.Rerank(ranked, flagged, time.Now().UnixMilli())
	if len(reranked) > limit {
		reranked = reranked[:limit]
	}

	items := make([]feedItem, len(reranked))
	for i, c := range reranked {
		items[i] = feedItem{VideoID: c.VideoID, Score: c.Score, Rank: i + 1, CreatorID: c.CreatorID, DurationS: c.DurationS}
	}

	latency := time.Since(start).Milliseconds()
	feedLatency.Observe(float64(latency))
	json.NewEncoder(w).Encode(feedResponse{UserID: userID, Feed: items, ModelVersion: modelVer, LatencyMs: latency})
}
