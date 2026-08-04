// nhooyr.io/websocket Accept + wsjson.Write, CloseRead write-only pattern
package handler

import (
	"context"
	"net/http"
	"time"

	"nhooyr.io/websocket"
	"nhooyr.io/websocket/wsjson"

	"github.com/bit2swaz/siphon/dashboard-api/internal/livefeed"
)

type WSHandler struct{ ring *livefeed.Ring }

func NewWSHandler(ring *livefeed.Ring) *WSHandler { return &WSHandler{ring: ring} }

func (h *WSHandler) Live(w http.ResponseWriter, r *http.Request) {
	conn, err := websocket.Accept(w, r, &websocket.AcceptOptions{
		// no origin check needed. internal Docker network only, no browser cross-origin risk
		OriginPatterns: []string{"*"},
	})
	if err != nil {
		return
	}
	defer conn.CloseNow()
	ctx := conn.CloseRead(context.Background())

	ticker := time.NewTicker(100 * time.Millisecond) // ~10Hz
	defer ticker.Stop()

	var lastSent int
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			events := h.ring.Last(20)
			if len(events) == 0 || len(events) == lastSent {
				continue
			}
			lastSent = len(events)
			if err := wsjson.Write(ctx, conn, events); err != nil {
				return
			}
		}
	}
}
