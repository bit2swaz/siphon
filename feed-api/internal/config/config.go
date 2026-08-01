package config

import "os"

type Config struct {
	QdrantAddr      string
	RedisAddr       string
	ModelServerAddr string // gRPC host:port
	Port            string
}

func Load() Config {
	return Config{
		QdrantAddr:      getenv("QDRANT_HOST", "qdrant") + ":" + getenv("QDRANT_GRPC_PORT", "6334"),
		RedisAddr:       getenv("REDIS_HOST", "redis") + ":" + getenv("REDIS_PORT", "6379"),
		ModelServerAddr: getenv("MODEL_SERVER_ADDR", "model-server:50051"),
		Port:            getenv("PORT", "8005"),
	}
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
