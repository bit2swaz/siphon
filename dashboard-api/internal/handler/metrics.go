package handler

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"time"
)

type MetricsHandler struct{ db *sql.DB }

func NewMetricsHandler(db *sql.DB) *MetricsHandler { return &MetricsHandler{db: db} }

type snapshotResp struct {
	CTR          float64 `json:"ctr"`
	AvgWatchFrac float64 `json:"avg_watch_frac"`
	EventsPerSec float64 `json:"events_per_sec"`
	ModelVersion int     `json:"model_version"`
}

func (h *MetricsHandler) Snapshot(w http.ResponseWriter, r *http.Request) {
	resp := snapshotResp{}
	if h.db != nil {
		since := time.Now().Add(-60 * time.Second).UnixMilli()
		row := h.db.QueryRowContext(r.Context(),
			`SELECT
			   COALESCE(AVG(label::float), 0),
			   COALESCE(AVG(watch_frac), 0),
			   COALESCE(COUNT(*)::float / 60.0, 0)
			 FROM interactions WHERE created_at > $1`, since)
		var ctr, avgWF, eps float64
		if err := row.Scan(&ctr, &avgWF, &eps); err == nil {
			resp.CTR, resp.AvgWatchFrac, resp.EventsPerSec = ctr, avgWF, eps
		}
		vrow := h.db.QueryRowContext(r.Context(),
			`SELECT COALESCE(MAX(version),0) FROM training_runs WHERE finished_at IS NOT NULL`)
		_ = vrow.Scan(&resp.ModelVersion)
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}
