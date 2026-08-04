package main

import (
	"database/sql"
	"log"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/bit2swaz/siphon/dashboard-api/internal/config"
	"github.com/bit2swaz/siphon/dashboard-api/internal/db"
	"github.com/bit2swaz/siphon/dashboard-api/internal/handler"
	"github.com/bit2swaz/siphon/dashboard-api/internal/livefeed"
)

func main() {
	cfg := config.Load()

	database, err := db.Open(cfg.PostgresDSN)
	if err != nil {
		log.Fatalf("db open: %v", err)
	}
	defer database.Close()

	ring := livefeed.NewRing(500)
	ws := handler.NewWSHandler(ring)
	metrics := handler.NewMetricsHandler(database)
	training := handler.NewTrainingHandler(database)
	ab := handler.NewABHandler(database)

	// poll DB for recent interactions and push to ring
	go pollInteractions(database, ring)

	r := chi.NewRouter()
	r.Get("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status":"ok"}`))
	})
	r.Get("/metrics/snapshot", metrics.Snapshot)
	r.Get("/training/history", training.History)
	r.Get("/ab/compare", ab.Compare)
	r.Get("/ws/live", ws.Live)
	r.Handle("/prom-metrics", promhttp.Handler())

	log.Printf("dashboard-api listening on :%s", cfg.Port)
	http.ListenAndServe(":"+cfg.Port, r)
}

func pollInteractions(db *sql.DB, ring *livefeed.Ring) {
	var lastID int64
	for {
		time.Sleep(100 * time.Millisecond)
		rows, err := db.Query(
			`SELECT id, user_id, video_id, watch_frac, event_type, created_at
			 FROM interactions WHERE id > $1 ORDER BY id ASC LIMIT 50`, lastID)
		if err != nil {
			continue
		}
		for rows.Next() {
			var e livefeed.Event
			var id int64
			if err := rows.Scan(&id, &e.UserID, &e.VideoID, &e.WatchFrac, &e.EventType, &e.TsMs); err == nil {
				ring.Push(e)
				lastID = id
			}
		}
		rows.Close()
	}
}
