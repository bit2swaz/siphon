package handler

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"
)

type ABHandler struct{ db *sql.DB }

func NewABHandler(db *sql.DB) *ABHandler { return &ABHandler{db: db} }

type abModelStats struct {
	Version      int     `json:"version"`
	CTR          float64 `json:"ctr"`
	AvgWatchFrac float64 `json:"avg_watch_frac"`
}

func (h *ABHandler) Compare(w http.ResponseWriter, r *http.Request) {
	modelA, _ := strconv.Atoi(r.URL.Query().Get("model_a"))
	modelB, _ := strconv.Atoi(r.URL.Query().Get("model_b"))

	statsA := h.statsForVersion(r, modelA)
	statsB := h.statsForVersion(r, modelB)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]any{"model_a": statsA, "model_b": statsB})
}

func (h *ABHandler) statsForVersion(r *http.Request, version int) abModelStats {
	s := abModelStats{Version: version}
	if h.db == nil || version == 0 {
		return s
	}
	// get start/end timestamps for this version from training_runs
	var startedAt, finishedAt int64
	row := h.db.QueryRowContext(r.Context(),
		`SELECT started_at, COALESCE(finished_at, EXTRACT(EPOCH FROM NOW())::bigint * 1000)
		 FROM training_runs WHERE version=$1`, version)
	if err := row.Scan(&startedAt, &finishedAt); err != nil {
		return s
	}
	row2 := h.db.QueryRowContext(r.Context(),
		`SELECT COALESCE(AVG(label::float),0), COALESCE(AVG(watch_frac),0)
		 FROM interactions WHERE created_at BETWEEN $1 AND $2`,
		startedAt, finishedAt)
	_ = row2.Scan(&s.CTR, &s.AvgWatchFrac)
	return s
}
