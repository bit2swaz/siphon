import os

FEED_API_URL        = os.getenv("FEED_API_URL",   "http://feed-api:8005")
EVENT_API_URL       = os.getenv("EVENT_API_URL",  "http://user-event-service:8002")
NUM_USERS           = int(os.getenv("SIM_NUM_USERS",          500))
SPEED_MULTIPLIER    = float(os.getenv("SIM_SPEED_MULTIPLIER", 10.0))
KUAIREC_PATH        = os.getenv("KUAIREC_PATH", "data/small_matrix.csv")
DRIFT_STD           = 0.01
DRIFT_EVERY_N_TICKS = 100
