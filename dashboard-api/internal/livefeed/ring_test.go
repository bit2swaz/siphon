package livefeed_test

import (
	"testing"

	"github.com/bit2swaz/siphon/dashboard-api/internal/livefeed"
)

func TestRing_LastN(t *testing.T) {
	r := livefeed.NewRing(10)
	for i := 0; i < 15; i++ {
		r.Push(livefeed.Event{UserID: "u", VideoID: "v", TsMs: int64(i)})
	}
	last := r.Last(5)
	if len(last) != 5 {
		t.Fatalf("expected 5, got %d", len(last))
	}
	// last 5 pushed were ts 10..14
	if last[0].TsMs != 10 {
		t.Errorf("expected TsMs=10, got %d", last[0].TsMs)
	}
}
