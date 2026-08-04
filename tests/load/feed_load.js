import http from 'k6/http';
import { check } from 'k6';

// user IDs to rotate through (matches seeded users u000000–u000499)
const USER_COUNT = 500;

export const options = {
  scenarios: {
    constant_rps: {
      executor: 'constant-arrival-rate',
      rate: 100,           // 100 reqs/sec
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 50,
      maxVUs: 100,
    },
  },
  thresholds: {
    http_req_duration: ['p(99)<200'],  // p99 must be under 200ms
    http_req_failed: ['rate<0.01'],    // error rate must be below 1%
  },
};

export default function () {
  const userIdx = Math.floor(Math.random() * USER_COUNT);
  const userId  = `u${String(userIdx).padStart(6, '0')}`;
  const res = http.get(`http://localhost:8005/feed?user_id=${userId}&limit=20`);

  check(res, {
    'status is 200':      r => r.status === 200,
    'feed array present': r => JSON.parse(r.body).feed !== undefined,
    'latency_ms present': r => JSON.parse(r.body).latency_ms !== undefined,
  });
}
