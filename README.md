# NeonGo 🏃

Yuqori unumdorlikli runtime, mikroservis ishga tushiruvchi va task ijro qatlamı.

## Kalit so'zlar
`go`, `spawn`, `service`, `parallel`, `schedule`, `repeat`, `microservice`, `async`, `task`, `worker`

## O'rnatish
```bash
pip install https://github.com/SuhoPro777/NeonGo.git
```

## Ishlatish

```python
from NeonGo import NeonGo
import time

ng = NeonGo(max_workers=8)

future = ng.go(lambda: sum(range(1000000)), name="big_sum")
print(f"Natija: {future.result()}")

def process(x): return x * x
results = ng.spawn(
    lambda: process(10),
    lambda: process(20),
    lambda: process(30),
)
for r in results:
    print(r['result'])

ng.service("greet", lambda name: f"Salom, {name}!")
print(ng.call("greet", "Rustam"))

ng.schedule(lambda: print("3 sekunddan keyin!"), delay=3.0)

print(ng.stats())
time.sleep(4)
ng.shutdown()
```

## Real misol

```python
from NeonGo import NeonGo
import time, random

ng = NeonGo(max_workers=16)

# Mikroservislargani ro'yxatdan o'tkazish
ng.service("image_resize", lambda img: f"Resized: {img}")
ng.service("send_email", lambda to: f"Email sent to {to}")
ng.service("update_db", lambda data: f"DB updated: {data}")

# Parallel ijro
start = time.time()
tasks = ng.spawn(
    lambda: ng.call("image_resize", "photo.jpg"),
    lambda: ng.call("send_email", "user@example.com"),
    lambda: ng.call("update_db", {"id": 1}),
)
elapsed = time.time() - start

print(f"3 ta vazifa {elapsed:.3f}s da bajarildi:")
for t in tasks:
    print(f"  ✅ {t['result']}")

ng.shutdown()
```
