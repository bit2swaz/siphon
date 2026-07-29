package main

import (
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/bit2swaz/siphon/user-event-service/internal/config"
	"github.com/bit2swaz/siphon/user-event-service/internal/events"
	"github.com/bit2swaz/siphon/user-event-service/internal/handler"
)

func main() {
	cfg := config.Load()

	pub := events.NewKafkaPublisher(cfg.KafkaBootstrap, cfg.KafkaTopic)
	ses := events.NewRedisSession(cfg.RedisAddr)
	evtHandler := handler.NewEventHandler(pub, ses)

	r := chi.NewRouter()
	r.Get("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status":"ok"}`))
	})
	r.Post("/events", evtHandler.Handle)
	r.Handle("/metrics", promhttp.Handler())

	http.ListenAndServe(":"+cfg.Port, r)
}
