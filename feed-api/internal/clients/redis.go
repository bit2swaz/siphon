// go-redis/v9 ZRevRange, LRange, HGetAll, SIsMember
package clients

import (
	"context"

	"github.com/redis/go-redis/v9"
)

type Redis struct{ rdb *redis.Client }

func NewRedis(addr string) *Redis {
	return &Redis{rdb: redis.NewClient(&redis.Options{Addr: addr})}
}

func (r *Redis) ZRevRange(ctx context.Context, key string, stop int64) ([]string, error) {
	return r.rdb.ZRevRange(ctx, key, 0, stop).Result()
}
func (r *Redis) LRange(ctx context.Context, key string, stop int64) ([]string, error) {
	return r.rdb.LRange(ctx, key, 0, stop).Result()
}
func (r *Redis) HGetAll(ctx context.Context, key string) (map[string]string, error) {
	return r.rdb.HGetAll(ctx, key).Result()
}
func (r *Redis) IsFlagged(ctx context.Context, videoID string) (bool, error) {
	return r.rdb.SIsMember(ctx, "flagged", videoID).Result()
}

// ItemVec returns the 256-dim projected item embedding cached at item:{id}/item_vec_b64
// (base64 of float32s). this is the same space written to Qdrant so scoring matches
// training. empty slice if the item isnt cached
func (r *Redis) ItemVec(ctx context.Context, videoID string) ([]float32, error) {
	b64, err := r.rdb.HGet(ctx, "item:"+videoID, "item_vec_b64").Result()
	if err != nil {
		return nil, err
	}
	return decodeVecB64(b64)
}
