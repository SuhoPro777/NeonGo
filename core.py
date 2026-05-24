import time, threading, queue, concurrent.futures
from typing import Any, Callable, Dict, List, Optional


class Task:
    def __init__(self, name: str, fn: Callable, args: tuple = (), kwargs: dict = None, priority: int = 0):
        self.name = name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.created_at = time.time()

    def __lt__(self, other):
        return self.priority > other.priority


class NeonGo:
    """High-performance task runner, microservice and edge execution engine."""

    def __init__(self, max_workers: int = 8, queue_size: int = 1000):
        self.max_workers = max_workers
        self._task_queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=queue_size)
        self._results: Dict[str, Any] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._services: Dict[str, Callable] = {}
        self._running_tasks: List[str] = []
        self._completed = 0
        self._failed = 0

    def go(self, fn: Callable, *args, name: str = None, priority: int = 0, **kwargs) -> concurrent.futures.Future:
        """Execute a task immediately in thread pool."""
        task_name = name or f"task_{int(time.time()*1000)}"
        self._running_tasks.append(task_name)
        future = self._executor.submit(fn, *args, **kwargs)
        def done_cb(f):
            self._running_tasks.remove(task_name) if task_name in self._running_tasks else None
            if f.exception():
                self._failed += 1
                self._results[task_name] = {"error": str(f.exception()), "success": False}
            else:
                self._completed += 1
                self._results[task_name] = {"result": f.result(), "success": True}
        future.add_done_callback(done_cb)
        return future

    def spawn(self, *fns: Callable, data: Any = None) -> List[Any]:
        """Spawn multiple tasks in parallel."""
        futures = [self._executor.submit(fn, data) for fn in fns]
        results = []
        for f in concurrent.futures.as_completed(futures, timeout=30):
            try:
                results.append({"result": f.result(), "success": True})
            except Exception as e:
                results.append({"error": str(e), "success": False})
        return results

    def service(self, name: str, fn: Callable) -> 'NeonGo':
        """Register a microservice."""
        self._services[name] = fn
        return self

    def call(self, service_name: str, *args, **kwargs) -> Any:
        """Call a registered microservice."""
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not registered")
        return self._services[service_name](*args, **kwargs)

    def schedule(self, fn: Callable, delay: float, *args, **kwargs) -> threading.Timer:
        """Schedule a task after delay (seconds)."""
        timer = threading.Timer(delay, fn, args=args, kwargs=kwargs)
        timer.daemon = True
        timer.start()
        return timer

    def repeat(self, fn: Callable, interval: float, max_runs: int = None) -> threading.Thread:
        """Repeat a task at fixed interval."""
        runs = [0]
        stop_event = threading.Event()
        def _loop():
            while not stop_event.is_set():
                fn()
                runs[0] += 1
                if max_runs and runs[0] >= max_runs:
                    break
                stop_event.wait(interval)
        t = threading.Thread(target=_loop, daemon=True)
        t.start()
        return t

    def stats(self) -> Dict:
        return {
            "workers": self.max_workers,
            "completed": self._completed,
            "failed": self._failed,
            "running": len(self._running_tasks),
            "services": list(self._services.keys()),
        }

    def shutdown(self, wait: bool = True):
        self._executor.shutdown(wait=wait)
