package config

import "os"

type Config struct {
	KafkaBootstrap string
	KafkaTopic     string
	RedisAddr      string
	Port           string
}

func Load() Config {
	return Config{
		KafkaBootstrap: getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
		KafkaTopic:     "user.events",
		RedisAddr:      getenv("REDIS_HOST", "redis") + ":" + getenv("REDIS_PORT", "6379"),
		Port:           getenv("PORT", "8002"),
	}
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
