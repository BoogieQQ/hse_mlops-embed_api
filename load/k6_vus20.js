import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';
import { SharedArray } from 'k6/data';

const simpleLatency = new Trend('latency_simple');
const onnxLatency = new Trend('latency_onnx');
const dynamicLatency = new Trend('latency_dynamic');

const simpleRPS = new Counter('rps_simple');
const onnxRPS = new Counter('rps_onnx');
const dynamicRPS = new Counter('rps_dynamic');

const memeQuotes = new SharedArray('meme quotes', function () {
  return [
    "Работа не волк, работа - ворк, а волк - это ходить.",
    "Лучше быть последним в списке миллиардеров, чем первым в списке в очереди в Пятёрочку.",
    "Если тебе тяжело идти, значит ты жирный.",
    "Не делай сегодня то, что можно сделать послезавтра.",
    "Слабые скажут «не судьба», сильные скажут «я еще посплю».",
    "Если ты упал - встань. Если ты опять упал - ну, значит, ты упал.",
    "Запомните, а то забудете.",
    "Брат за брата - так за основу взято.",
    "Я не ленивый, я просто нахожусь в режиме энергосбережения.",
    "Никогда не сдавайся, позорься до конца!"
  ];
});

export const options = {
  scenarios: {
    scenario_simple: {
      executor: 'constant-vus',
      vus: 20,
      duration: '20s',
      exec: 'testSimple',
      startTime: '0s',
    },
    scenario_onnx: {
      executor: 'constant-vus',
      vus: 20,
      duration: '20s',
      exec: 'testOnnx',
      startTime: '25s', 
    },
    scenario_dynamic: {
      executor: 'constant-vus',
      vus: 20,
      duration: '20s',
      exec: 'testDynamic',
      startTime: '50s',
    },
  },
};

const url = 'http://localhost:8000';
const params = { headers: { 'Content-Type': 'application/json' } };

function getPayload() {
  const text = memeQuotes[Math.floor(Math.random() * memeQuotes.length)];
  return JSON.stringify({ text: text });
}

export function testSimple() {
  const res = http.post(`${url}/simple_embed`, getPayload(), params);
  if (res.status === 200) {
    simpleLatency.add(res.timings.waiting);
    simpleRPS.add(1);
  }
}

export function testOnnx() {
  const res = http.post(`${url}/onnx_embed`, getPayload(), params);
  if (res.status === 200) {
    onnxLatency.add(res.timings.waiting);
    onnxRPS.add(1);
  }
}

export function testDynamic() {
  const res = http.post(`${url}/onnx_dynamic_batch`, getPayload(), params);
  if (res.status === 200) {
    dynamicLatency.add(res.timings.waiting);
    dynamicRPS.add(1);
  }
}