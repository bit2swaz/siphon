package handler

import (
	"database/sql"
	"encoding/json"
	"net/http"
)

type TrainingHandler struct{ db *sql.DB }

func NewTrainingHandler(db *sql.DB) *TrainingHandler { return &TrainingHandler{db: db} }

type trainingRun struct {
	Version    int       `json:"version"`
	StartedAt  int64     `json:"started_at"`
	FinishedAt *int64    `json:"finished_at"`
	AUC        *float64  `json:"auc"`
	Loss       []float64 `json:"loss"`
}

func (h *TrainingHandler) History(w http.ResponseWriter, r *http.Request) {
	var runs []trainingRun
	if h.db != nil {
		rows, err := h.db.QueryContext(r.Context(),
			`SELECT version, started_at, finished_at, auc, loss_json FROM training_runs ORDER BY version DESC LIMIT 50`)
		if err == nil {
			defer rows.Close()
			for rows.Next() {
				var tr trainingRun
				var lossJSON *string
				var finAt sql.NullInt64
				var auc sql.NullFloat64
				if err := rows.Scan(&tr.Version, &tr.StartedAt, &finAt, &auc, &lossJSON); err == nil {
					if finAt.Valid {
						tr.FinishedAt = &finAt.Int64
					}
					if auc.Valid {
						tr.AUC = &auc.Float64
					}
					if lossJSON != nil {
						_ = json.Unmarshal([]byte(*lossJSON), &tr.Loss)
					}
					runs = append(runs, tr)
				}
			}
		}
	}
	if runs == nil {
		runs = []trainingRun{}
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(runs)
}
