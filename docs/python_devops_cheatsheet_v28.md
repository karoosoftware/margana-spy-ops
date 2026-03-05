# Python DevOps Coding Test Cheat Sheet (v28)

## 1) Fast Pattern Selector (Read This First)

| ID | If question says... | Pattern Name | DS / Tool |
|---|---|---|---|
| `P01` | duplicate, repeated, seen before | Seen Before | `set` |
| `P02` | remove duplicates but keep order | Stable Dedupe | `set` + `list` |
| `P03` | first unique / non-repeating | Count + 2-Pass | `dict` |
| `P04` | most frequent (single winner) | Most Frequent | `dict` |
| `P05` | top k frequent | Top-K Ranking | `dict` + `heapq` / sort |
| `P06` | within k distance / near duplicate | Index Tracking | `dict` |
| `P07` | two numbers sum to target | Complement Lookup | `dict` |
| `P08` | sorted list + pair sum / reverse | Two Pointers | index pointers |
| `P09` | last N seconds / rolling | Sliding Window | `deque` |
| `P10` | N per W seconds per key | Per-Key Limiter | `dict[key] -> deque` |
| `P11` | merge windows / overlaps | Interval Merge | sort + scan |
| `P12` | depends on / pipeline order / cycle | Topo Sort | indegree + queue |
| `P13` | earliest index >= threshold | Binary Search | `bisect_left` |
| `P14` | next job by timestamp | Priority Scheduling | `heapq` |
| `P15` | range sum/count quickly | Prefix Sums | list prefix |
| `P16` | max profit / buy low sell high once | Running Minimum | scalar vars |

## 1.5) DevOps Focus Mode (What To Prioritize First)

If your goal is DevOps interview readiness (not pure algorithm rounds), master these first:

1. Log parsing (safe split/regex + malformed handling)
2. Sliding window metrics (`P09`)
3. Per-key rate limiting (`P10`)
4. Dedupe/idempotency with TTL
5. Top-K metrics (`P05`)
6. Most-frequent + counting (`P04`)
7. Interval merge (`P11`)
8. Dependency ordering / topo (`P12`)
9. Priority queue scheduling (`P14`)
10. Prefix/range metrics (`P15`)

Low priority for DevOps-first prep:
- `P08` reverse-only tasks
- `P16` stock-profit style questions
- heavy recursion/DP that is not tied to ops data processing

## 1.6) 80/20 Mapping (Prompt -> Pattern)

- "parse logs / skip bad lines" -> Parsing Toolkit + `P04`/`P05`
- "last N seconds" -> `P09`
- "N events per key in W seconds" -> `P10`
- "duplicate event suppression / idempotent" -> TTL Dedupe
- "top endpoints / busiest users" -> `P05`
- "merge maintenance windows" -> `P11`
- "deployment order / dependencies" -> `P12`
- "next job by earliest time" -> `P14`
- "many range sum/count queries" -> `P15`

## 2) Core Templates (Most Used)

### P01) Seen Before
**Use when:** duplicates / seen-before checks.


**DevOps example:** Drop duplicate alert IDs from an incident event stream so PagerDuty is not spammed.

**Template**
```python
seen = set()
for x in nums:
    if x in seen:
        return x
    seen.add(x)
return None
```

---

### P02) Stable Dedupe (Keep Order)
**Use when:** remove duplicates but preserve first-seen order.


**DevOps example:** Build a unique host list from logs while keeping first-seen order for timeline replay.

**Template**
```python
seen = set()
out = []
for x in items:
    if x not in seen:
        seen.add(x)
        out.append(x)
return out
```

---

### P04) Most Frequent (First-Seen Tie-Break)
**Use when:** most frequent with stable input-order tie-break.


**DevOps example:** Find the most frequent HTTP status in access logs to summarize an outage quickly.

**Template**
```python
counts = {}
for x in nums:
    counts[x] = counts.get(x, 0) + 1
max_freq = max(counts.values())
for x in nums:  # preserves input order tie-break
    if counts[x] == max_freq:
        return x
```

---

### P05) Top-K with Lexicographic Tie-Break
**Use when:** top `k` by frequency with deterministic ordering.


**DevOps example:** Return the top 5 failing API paths for an observability dashboard.

**Template**
```python
from collections import Counter
counts = Counter(items)
top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
```

---

### P09) Sliding Window (Global)
**Use when:** rolling metrics over last `W` seconds/items.


**DevOps example:** Track requests in the last 60 seconds to drive autoscaling or alert thresholds.

**Template**
```python
from collections import deque
q = deque()
for t in times:
    q.append(t)
    start = t - W + 1  # inclusive window
    while q and q[0] < start:
        q.popleft()
    window_size = len(q)
```

---

### P10) Per-Key Rate Limiter
**Use when:** `N` events per key in `W`-second window.


**DevOps example:** Enforce per-IP login throttling like 100 attempts per 60 seconds.

**Template**
```python
from collections import defaultdict, deque

def rate_limit(events, N, W):
    buckets = defaultdict(deque)
    out = []
    for t, key in events:
        dq = buckets[key]
        start = t - W + 1
        while dq and dq[0] < start:
            dq.popleft()
        if len(dq) >= N:
            out.append("BLOCKED")
        else:
            out.append("ALLOWED")
            dq.append(t)
    return out
```

---

### TTL Dedupe
**Use when:** suppress duplicate emits inside cooldown/TTL.


**DevOps example:** Ignore repeated webhook delivery IDs for 5 minutes to keep processing idempotent.

**Template**
```python
last = {}  # key -> last emitted ts
for t, key in events:
    if key not in last or t - last[key] > TTL:
        emit(key)
        last[key] = t
```

---

### P11) Merge Intervals
**Use when:** merge overlapping/touching time windows.


**DevOps example:** Merge overlapping maintenance windows from multiple service teams into one schedule.

**Template**
```python
def merge(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    out = [intervals[0][:]]
    for s, e in intervals[1:]:
        if s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
```

---

### P12) Dependency Order (Topo + Cycle)
**Use when:** dependency graph ordering with cycle detection.


**DevOps example:** Compute safe deployment order for services and database migrations in CI/CD.

**Template**
```python
from collections import deque

def topo(deps):  # deps: node -> [prereqs]
    indeg, adj = {}, {}
    for n, prereqs in deps.items():
        indeg.setdefault(n, 0); adj.setdefault(n, [])
        for p in prereqs:
            indeg.setdefault(p, 0); adj.setdefault(p, [])
            adj[p].append(n); indeg[n] += 1

    q = deque([n for n, d in indeg.items() if d == 0])
    order = []
    while q:
        n = q.popleft(); order.append(n)
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    return order if len(order) == len(indeg) else "cycle"
```

---

## 3) Parsing Toolkit (DevOps Inputs)

### Safe Split Parse
**Template**
```python
parts = line.split()
if len(parts) < 5:
    return None  # or continue
```

---

### Regex (Fixed Valid Pattern)
**Template**
```python
import re
pat = re.compile(
    r'^(?P<ip>\S+)\s+(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\d+)$'
)
m = pat.match(line)
if not m:
    return None
ip = m['ip']
status = int(m['status'])
```

---

### JSON Safe Decode
**Template**
```python
import json
try:
    obj = json.loads(payload)
except json.JSONDecodeError:
    obj = None
```

---

### Datetime -> Epoch
**Template**
```python
from datetime import datetime

# ISO 8601
epoch = int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp())

# Apache style
epoch = int(datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z").timestamp())
```

## 4) Added High-ROI Patterns

### P14) Priority Queue Scheduling (next run first)
**Use when:** schedule/retry by earliest `next_run_ts`.


**DevOps example:** Run retry jobs in timestamp order so overdue tasks are executed first.

**Template**
```python
import heapq

# (next_run_ts, job_id, payload)
pq = []
heapq.heappush(pq, (next_ts, job_id, payload))

while pq:
    t, job_id, payload = heapq.heappop(pq)
    if should_retry(payload):
        heapq.heappush(pq, (t + backoff_s, job_id, payload))
```

---

### P15) Prefix Sums (Range Queries)
**Use when:** many range sum/count queries on static array.


**DevOps example:** Query total requests between minute ranges repeatedly from pre-aggregated metrics.

**Template**
```python
# arr: per-minute request counts
prefix = [0]
for x in arr:
    prefix.append(prefix[-1] + x)

# sum over [l, r] inclusive
window_sum = prefix[r + 1] - prefix[l]
```

---

## 5) Complexity Quick Table

| Pattern | Time | Space |
|---|---|---|
| set/dict seen-before | `O(n)` | `O(n)` |
| counting dict | `O(n)` | `O(n)` |
| sort + scan (interval merge) | `O(n log n)` | `O(n)` |
| top-k heap | `O(n log k)` | `O(k)` |
| top-k full sort | `O(n log n)` | `O(n)` |
| sliding window deque | `O(n)` | `O(n)` |
| two-sum lookup | `O(n)` | `O(n)` |
| topo sort | `O(V+E)` | `O(V+E)` |
| bisect lookup | `O(log n)` | `O(1)` |
| prefix query after build | build `O(n)`, query `O(1)` | `O(n)` |
| max profit (running minimum) | `O(n)` | `O(1)` |

## 6) Exam Guardrails (Read Before Coding)

### Output Contract Checklist
- Exact return type: `None` vs `[]` vs `False`
- Output order required? (input order / sorted / any)
- Tie-break rule required? (first-seen / lexicographic)
- Case-sensitive keys or normalized?
- If no solution, what exactly return?

### Tie-Break Rules
- First-seen tie-break: do count first, then second pass on original order.
- Lexicographic tie-break: `sorted(items, key=lambda kv: (-kv[1], kv[0]))`.
- If unspecified, state assumption in a short comment.

### Malformed Input Policy
- Decide once: skip malformed lines OR fail fast.
- Wrap risky parse points (`int`, `json`, datetime) in `try/except`.
- Keep counters if useful: `processed`, `skipped`, `errors`.

### Boundary Rules (Common Bugs)
- Sliding time window inclusive: `start = t - W + 1`; keep `ts >= start`.
- Interval overlap condition: `next_start <= current_end`.
- Duplicate suppression: clarify `>` vs `>=` in TTL checks.

### Safe Defaults
```python
if not items:
    return []  # or None / False based on contract
```

## 7) 90-Second Solve Workflow

1. Write input/output + tie-break + malformed policy in comments.
2. Map cue phrase to pattern.
3. Pick DS (`set/dict/deque/heap`).
4. Code smallest correct template.
5. Run 3 checks mentally: empty input, boundary timestamp, tie case.

## 7.5) Pre-Submit Tick List (Print Checklist)

Tick these before submitting:

- [ ] Return type exactly matches prompt (`None` vs `[]` vs `False` vs value).
- [ ] Output ordering matches requirement (input-order / sorted / any-order).
- [ ] Tie-break rule is implemented (first-seen / lexicographic / other).
- [ ] Empty input behavior is handled explicitly.
- [ ] No-solution behavior is handled explicitly.
- [ ] Boundary conditions checked (`<=`, `>=`, `t - W + 1`, touching intervals).
- [ ] Malformed input policy is consistent (skip vs strict fail-fast).
- [ ] Time/space complexity is acceptable for expected input size.
- [ ] Quick smoke tests run:
  - [ ] normal case
  - [ ] tie case (if relevant)
  - [ ] single-element case
  - [ ] empty input case
  - [ ] boundary timestamp/range case

## 8) Practice Exam Addendum (Missing Patterns)

### Reverse In-Place (Two Pointers)
**Use when:** reverse array/string buffer without extra array.


**DevOps example:** Reverse a buffered event batch in place before replaying latest-first entries.

**Template**
```python
l, r = 0, len(arr) - 1
while l < r:
    arr[l], arr[r] = arr[r], arr[l]
    l += 1
    r -= 1
```

---

### Two Pointers on Sorted Array (Pair Sum)
**Use when:** sorted input and need pair sum.


**DevOps example:** Find two reserved capacity blocks that exactly match a target resource amount.

**Template**
```python
l, r = 0, len(nums) - 1
while l < r:
    s = nums[l] + nums[r]
    if s == target:
        return [l, r]
    if s < target:
        l += 1
    else:
        r -= 1
return None
```

---

### Binary Search (First Value >= T)
**Use when:** sorted monotonic list.


**DevOps example:** In sorted timestamps, find the first log/event at or after an incident start time.

**Template**
```python
import bisect
i = bisect.bisect_left(xs, T)
return None if i == len(xs) else i
```

---

### Anagram Check (Count Method)
**Use when:** compare normalized strings.


**DevOps example:** Validate normalized token/tag strings when cleaning inconsistent metadata feeds.

**Template**
```python
def is_anagram(a, b):
    a = a.replace(" ", "").lower()
    b = b.replace(" ", "").lower()
    if len(a) != len(b):
        return False
    counts = {}
    for c in a:
        counts[c] = counts.get(c, 0) + 1
    for c in b:
        counts[c] = counts.get(c, 0) - 1
    return all(v == 0 for v in counts.values())
```

---

### Retry with Exponential Backoff + Jitter
**Use when:** transient failures (`timeout`, `5xx`) only.


**DevOps example:** Retry flaky upstream API calls without causing synchronized retry storms.

**Template**
```python
import random

def retry_plan(outcomes, base=0.1, cap=10.0):
    delays = []
    attempt = 0
    for outcome in outcomes:
        if outcome == "ok":
            break
        attempt += 1
        transient = outcome in {"timeout", "5xx", "conn_reset"}
        if not transient:
            break
        delay = min(base * (2 ** (attempt - 1)), cap)
        delays.append(random.uniform(0, delay))  # full jitter
    return delays
```

---

### CLI Skeleton (stdin/stdout + exit code)
**Use when:** platform asks for script behavior.


**DevOps example:** Build a Unix-style log filter that reads stdin and outputs only 5xx lines.

**Template**
```python
import sys

def main() -> int:
    for line in sys.stdin:
        line = line.rstrip("\\n")
        if not line:
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        status = int(parts[3])
        if status >= 500:
            print(line)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

---

### Monotonic Queue (Rolling Max)
**Use when:** max/min over last `k` values in `O(n)`.


**DevOps example:** Compute rolling max latency over the last 100 samples for alerting.

**Template**
```python
from collections import deque

def rolling_max(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and dq[-1][1] <= x:
            dq.pop()
        dq.append((i, x))
        while dq and dq[0][0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(dq[0][1])
    return out
```

---

### Streaming Median (Two Heaps)
**Use when:** median after each insert.


**DevOps example:** Track median response time in a live telemetry stream.

**Template**
```python
import heapq

def running_median(nums):
    lo, hi = [], []  # lo=max-heap via negatives, hi=min-heap
    out = []
    for x in nums:
        heapq.heappush(lo, -x)
        heapq.heappush(hi, -heapq.heappop(lo))
        if len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        if len(lo) == len(hi):
            out.append((-lo[0] + hi[0]) / 2.0)
        else:
            out.append(float(-lo[0]))
    return out
```

---

### K-Way Merge (Sorted Streams)
**Use when:** merge multiple sorted log streams.


**DevOps example:** Merge per-pod sorted logs into one globally time-ordered output.

**Template**
```python
import heapq

def merge_streams(streams):
    heap = []
    out = []
    for si, stream in enumerate(streams):
        if stream:
            ts, msg = stream[0]
            heapq.heappush(heap, (ts, si, 0, msg))
    while heap:
        ts, si, idx, msg = heapq.heappop(heap)
        out.append((ts, msg))
        ni = idx + 1
        if ni < len(streams[si]):
            nts, nmsg = streams[si][ni]
            heapq.heappush(heap, (nts, si, ni, nmsg))
    return out
```

---

### Circuit Breaker (State Simulation)
**Use when:** open/half-open/closed transitions by failures + timeout.


**DevOps example:** Simulate service-to-service call protection state during repeated upstream failures.

**Template**
```python
def simulate(events, fail_threshold=3, reset_timeout=30):
    state = "closed"
    fail_count = 0
    opened_at = None
    out = []

    for t, ok in events:  # ok: bool
        if state == "open" and opened_at is not None and t - opened_at >= reset_timeout:
            state = "half-open"

        if state in {"closed", "half-open"}:
            if ok:
                state = "closed"
                fail_count = 0
            else:
                fail_count += 1
                if state == "half-open" or fail_count >= fail_threshold:
                    state = "open"
                    opened_at = t
        out.append(state)
    return out
```

---

## 9) Optional Algorithm Patterns (Moved from Core)

Use these when a platform includes more general algorithm questions.

### P03) Count + First Unique (2-pass)
**Use when:** first unique / first non-repeating.


**DevOps example:** Find the first unique request ID in a noisy batch to identify a single bad actor.

**Template**
```python
counts = {}
for x in nums:
    counts[x] = counts.get(x, 0) + 1
for x in nums:
    if counts[x] == 1:
        return x
return None
```

---

### P06) Index Tracking (Near Duplicate Within K)
**Use when:** detect repeated value within index distance `k`.


**DevOps example:** Detect repeated job IDs arriving too close together in a queue stream.

**Template**
```python
last_seen = {}
for i, x in enumerate(items):
    if x in last_seen and i - last_seen[x] <= k:
        return True
    last_seen[x] = i
return False
```

---

### P07) Two Sum
**Use when:** find pair indices that sum to target.


**DevOps example:** Pick two instance sizes that combine to a required temporary capacity target.

**Template**
```python
seen = {}
for i, x in enumerate(nums):
    y = target - x
    if y in seen:
        return [seen[y], i]
    seen[x] = i
return None
```

---

### P08) Two Pointers (Reverse / Sorted Pair Sum)
**Use when:** reverse in-place OR sorted pair sum.


**DevOps example:** Reverse an in-memory batch or match two sorted quota values to a target total.

**Template**
```python
def reverse_in_place(arr):
    l, r = 0, len(arr) - 1
    while l < r:
        arr[l], arr[r] = arr[r], arr[l]
        l += 1
        r -= 1
    return arr

def sorted_pair_sum(nums, target):
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return [l, r]  # indices in sorted array
        if s < target:
            l += 1
        else:
            r -= 1
    return None
```

---

### P13) Binary Search (First Value >= T)
**Use when:** sorted monotonic list, find earliest threshold index.


**DevOps example:** Find the first deployment event at or after a known outage timestamp.

**Template**
```python
import bisect
i = bisect.bisect_left(xs, T)
return None if i == len(xs) else i
```

---

### P16) Single-Transaction Max Profit (Running Minimum)
**Use when:** one buy + one sell, maximize `sell - buy` with buy before sell.


**DevOps example:** Model best single buy/sell point in spot-price data for cost optimization exercises.

**Template**
```python
def max_profit(prices):
    min_price = float("inf")
    max_profit = 0

    for p in prices:
        if p < min_price:
            min_price = p
        else:
            max_profit = max(max_profit, p - min_price)

    return max_profit
```

---

Print note: this sheet is optimized for fast lookup during timed online coding tests.
