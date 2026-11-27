import http from 'k6/http';
import exec from 'k6/execution';
import {check, sleep} from 'k6';
import {Gauge, Rate} from 'k6/metrics';

const config = JSON.parse(open('../evidence/phase5/targets.json'));
const run = config.run_order.find(item => item.id === __ENV.MEDIHUB_P5_RUN);
if (!run || config.origin !== 'http://127.0.0.1:5001') {
  throw new Error('Use a configured Phase 5 run against the isolated loopback app');
}
const profile = config.profiles[run.profile];
const warm = config.warmup_seconds * 1000;
const end = warm + config.steady_seconds * 1000;
const unexpected = new Rate('phase5_unexpected');
const boundary = new Gauge('phase5_boundary_ms');
const measured = {phase: 'steady', operation: 'availability'};
const warmup = {phase: 'warmup', operation: 'availability'};
const hours = [9, 10, 11, 12, 15, 16, 17, 18];
const time = hour => `${String(hour).padStart(2, '0')}:00`;
const clock = hour => `${String(hour % 12 || 12).padStart(2, '0')}:00 ${hour < 12 ? 'AM' : 'PM'}`;
const url = `${config.origin}${config.operation}?doctor_id=${config.doctor_id}&date=${config.date}`;
let entered = false;
let left = false;

http.setResponseCallback(http.expectedStatuses(200));

export const options = {
  setupTimeout: '65s',
  scenarios: {
    availability: {
      executor: 'constant-vus',
      vus: profile.vus,
      duration: `${config.warmup_seconds + config.steady_seconds + config.tail_seconds}s`,
      gracefulStop: '3s',
    },
  },
  tags: {experiment: run.id},
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max', 'count'],
  thresholds: {
    'http_req_duration{phase:steady}': [`p(95)<=${profile.p95_max_ms}`],
    'phase5_unexpected{phase:steady}': [`rate<${profile.unexpected_max_exclusive_fraction}`],
  },
};

export function setup() {
  if (!__ENV.MEDIHUB_P5_PASSWORD) throw new Error('Missing synthetic fixture password');
  const tokens = [];
  for (let n = 1; n <= 5; n += 1) {
    const response = http.post(`${config.origin}/api/auth/login`, JSON.stringify({
      username: `phase5-patient-${n}`,
      password: __ENV.MEDIHUB_P5_PASSWORD,
    }), {headers: {'Content-Type': 'application/json'}, tags: {phase: 'setup'}, timeout: '10s'});
    if (response.status !== 200 || !response.json('data.token')) {
      throw new Error(`Synthetic login failed with HTTP ${response.status}`);
    }
    tokens.push(response.json('data.token'));
  }
  return tokens;
}

function contract(response) {
  if (response.status !== 200) return false;
  try {
    const body = response.json();
    const data = body.data;
    return body.success === true && data.doctor_id === config.doctor_id && data.date === config.date
      && Array.isArray(data.slots) && data.slots.length === hours.length
      && data.slots.every((slot, i) => {
        const hour = hours[i];
        return slot.appointment_time === time(hour) && slot.time === `${time(hour)}-${time(hour + 1)}`
          && slot.slot_type === (hour < 13 ? 'morning' : 'evening') && slot.status === 'available'
          && slot.display === `${clock(hour)} - ${clock(hour + 1)}`;
      });
  } catch (_) {
    return false;
  }
}

export default function (tokens) {
  const now = Date.now();
  const elapsed = now - exec.scenario.startTime;
  const vu = String(exec.vu.idInTest);
  if (elapsed >= end) {
    if (!left) {
      boundary.add(now, {event: 'left', vu});
      left = true;
    }
    sleep(config.think_time_seconds);
    return;
  }
  const tags = elapsed < warm ? warmup : measured;
  if (tags === measured && !entered) {
    boundary.add(now, {event: 'entered', vu});
    entered = true;
  }
  const response = http.get(url, {
    headers: {Authorization: `Bearer ${tokens[exec.vu.idInTest - 1]}`},
    tags,
    timeout: config.http_timeout,
  });
  const ok = check(response, {'availability returned HTTP 200': r => r.status === 200,
    'availability matched its fixture contract': contract}, tags);
  unexpected.add(!ok, tags);
  sleep(config.think_time_seconds);
}
