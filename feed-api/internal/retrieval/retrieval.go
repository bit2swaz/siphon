// qdrant-client-go Search, go-redis ZRevRange, HGetAll
package retrieval

import (
	"context"
	"crypto/md5"
	"encoding/binary"
	"strconv"
)

type Candidate struct {
	VideoID   string
	CreatorID string
	Score     float64
	CreatedAt int64
	DurationS float64
}

// PointID must match scripts/idhash.py:point_id exactly: md5(s), first 8 bytes,
// big-endian, as an unsigned 64-bit int. Qdrant user/item points are written by
// the Python services using that scheme; a Go lookup with any other hash misses
func PointID(s string) uint64 {
	sum := md5.Sum([]byte(s))
	return binary.BigEndian.Uint64(sum[:8])
}

type QdrantSearcher interface {
	GetUserVec(ctx context.Context, userID string) ([]float32, error)
	SearchItems(ctx context.Context, userVec []float32, limit int) ([]Candidate, error)
}

type RedisClient interface {
	ZRevRange(ctx context.Context, key string, stop int64) ([]string, error)
	LRange(ctx context.Context, key string, stop int64) ([]string, error)
	HGetAll(ctx context.Context, key string) (map[string]string, error)
}

func Retrieve(ctx context.Context, userID string, q QdrantSearcher, rdb RedisClient) ([]Candidate, error) {
	seen := map[string]bool{}
	var candidates []Candidate

	// stage 1a: ANN from Qdrant
	userVec, err := q.GetUserVec(ctx, userID)
	if err == nil && len(userVec) > 0 {
		if ann, err := q.SearchItems(ctx, userVec, 500); err == nil {
			for _, c := range ann {
				if !seen[c.VideoID] {
					seen[c.VideoID] = true
					candidates = append(candidates, c)
				}
			}
		}
	}

	// stage 1b: trending recall
	trending, _ := rdb.ZRevRange(ctx, "trending:24h", 49)
	for _, vid := range trending {
		if seen[vid] {
			continue
		}
		fields, err := rdb.HGetAll(ctx, "item:"+vid)
		if err != nil || len(fields) == 0 {
			continue
		}
		seen[vid] = true
		candidates = append(candidates, candidateFromFields(vid, fields, 0.5))
	}

	// stage 1c: filter out the user's already-watched items (session history)
	session, _ := rdb.LRange(ctx, "session:"+userID, 49)
	watched := map[string]bool{}
	for _, v := range session {
		watched[v] = true
	}
	filtered := candidates[:0]
	for _, c := range candidates {
		if !watched[c.VideoID] {
			filtered = append(filtered, c)
		}
	}
	return filtered, nil
}

func candidateFromFields(videoID string, fields map[string]string, defaultScore float64) Candidate {
	c := Candidate{VideoID: videoID, Score: defaultScore, CreatorID: fields["creator_id"]}
	if v, err := strconv.ParseFloat(fields["duration_s"], 64); err == nil {
		c.DurationS = v
	}
	if v, err := strconv.ParseInt(fields["created_at"], 10, 64); err == nil {
		c.CreatedAt = v
	}
	return c
}
