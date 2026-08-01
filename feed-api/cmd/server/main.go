package main

import (
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/bit2swaz/siphon/feed-api/internal/clients"
	"github.com/bit2swaz/siphon/feed-api/internal/config"
	"github.com/bit2swaz/siphon/feed-api/internal/handler"
)

func main() {
	cfg := config.Load()

	qd, err := clients.NewQdrant(cfg.QdrantAddr)
	if err != nil {
		log.Fatalf("qdrant: %v", err)
	}
	rd := clients.NewRedis(cfg.RedisAddr)
	sc, err := clients.NewScorer(cfg.ModelServerAddr, rd) // rd fetches item embeds for scoring
	if err != nil {
		log.Fatalf("scorer: %v", err)
	}

	feed := handler.NewFeedHandler(qd, rd, sc, rd) // rd satisfies RedisClient and FlagChecker

	r := chi.NewRouter()
	r.Get("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status":"ok"}`))
	})
	r.Get("/feed", feed.Handle)
	r.Handle("/metrics", promhttp.Handler())

	log.Printf("feed-api listening on :%s", cfg.Port)
	http.ListenAndServe(":"+cfg.Port, r)
}
