package config

import "os"

type Config struct {
	PostgresDSN string
	Port        string
}

func Load() Config {
	pg := "postgresql://" + getenv("POSTGRES_USER", "siphon") +
		":" + getenv("POSTGRES_PASSWORD", "siphon") +
		"@" + getenv("POSTGRES_HOST", "postgres") +
		":" + getenv("POSTGRES_PORT", "5432") +
		"/" + getenv("POSTGRES_DB", "siphon") + "?sslmode=disable"
	return Config{
		PostgresDSN: pg,
		Port:        getenv("PORT", "8006"),
	}
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
