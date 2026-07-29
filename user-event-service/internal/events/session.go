// go-redis/v9 LPush, LTrim
package events

import (
	"context"

	"github.com/redis/go-redis/v9"
)

type RedisSession struct {
	rdb *redis.Client
}

func NewRedisSession(addr string) *RedisSession {
	return &RedisSession{
		rdb: redis.NewClient(&redis.Options{Addr: addr}),
	}
}

func (s *RedisSession) Record(userID, videoID string) error {
	ctx := context.Background()
	key := "session:" + userID
	pipe := s.rdb.Pipeline()
	pipe.LPush(ctx, key, videoID)
	pipe.LTrim(ctx, key, 0, 49) // keep last 50
	_, err := pipe.Exec(ctx)
	return err
}
