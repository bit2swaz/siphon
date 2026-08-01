// qdrant/go-client NewClient, Query, Get, NewIDNum, payload accessors (v1.18)
package clients

import (
	"context"
	"net"
	"strconv"

	"github.com/qdrant/go-client/qdrant"

	"github.com/bit2swaz/siphon/feed-api/internal/retrieval"
)

type Qdrant struct{ c *qdrant.Client }

func NewQdrant(addr string) (*Qdrant, error) {
	host, portStr, err := net.SplitHostPort(addr)
	if err != nil {
		return nil, err
	}
	port, err := strconv.Atoi(portStr)
	if err != nil {
		return nil, err
	}
	c, err := qdrant.NewClient(&qdrant.Config{Host: host, Port: port})
	if err != nil {
		return nil, err
	}
	return &Qdrant{c: c}, nil
}

// GetUserVec fetches the user's 256-dim embedding by its md5-derived point ID
func (q *Qdrant) GetUserVec(ctx context.Context, userID string) ([]float32, error) {
	pts, err := q.c.Get(ctx, &qdrant.GetPoints{
		CollectionName: "users",
		Ids:            []*qdrant.PointId{qdrant.NewIDNum(retrieval.PointID(userID))},
		WithVectors:    qdrant.NewWithVectors(true),
	})
	if err != nil || len(pts) == 0 {
		return nil, err
	}
	return pts[0].Vectors.GetVector().GetData(), nil
}

func (q *Qdrant) SearchItems(ctx context.Context, userVec []float32, limit int) ([]retrieval.Candidate, error) {
	lim := uint64(limit)
	res, err := q.c.Query(ctx, &qdrant.QueryPoints{
		CollectionName: "items",
		Query:          qdrant.NewQuery(userVec...),
		Limit:          &lim,
		WithPayload:    qdrant.NewWithPayload(true),
	})
	if err != nil {
		return nil, err
	}
	out := make([]retrieval.Candidate, 0, len(res))
	for _, p := range res {
		pl := p.Payload
		out = append(out, retrieval.Candidate{
			VideoID:   pl["video_id"].GetStringValue(),
			CreatorID: pl["creator_id"].GetStringValue(),
			Score:     float64(p.Score),
			CreatedAt: pl["created_at"].GetIntegerValue(),
			DurationS: pl["duration_s"].GetDoubleValue(),
		})
	}
	return out, nil
}
