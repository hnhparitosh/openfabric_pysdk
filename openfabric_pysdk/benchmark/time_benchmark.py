import gc
import logging
import timeit
from functools import wraps
from typing import Dict, Optional

from runstats import Statistics

_stats: Dict[str, Statistics] = {}
_lasts: Dict[str, float] = {}


def add_timing(name: str, elapsed: float, no_print=True) -> Statistics:
    global _stats
    global _lasts

    stats = _stats.get(name, None)
    if stats is None:
        stats = Statistics()
        _stats[name] = stats
    stats.push(elapsed)
    _lasts[name] = elapsed

    if not no_print:
        logging.debug('Openfabric - timing "{}": {}s'.format(name, elapsed))
    return stats


def get_last(name: str) -> float:
    global _lasts
    return _lasts[name]


def get_timing(name: str) -> Statistics:
    global _stats
    return _stats.get(name)


def get_all_timings() -> Dict[str, Statistics]:
    global _stats
    return _stats


def get_all_timings_json():
    global _stats
    res = []
    for name in _stats:
        stats = _stats[name]
        count = len(stats)
        res.append({
            "name": f'{name}',
            'avg': f'{stats.mean():.2f}',
            'count': f'{count}',
            'stddev': f'{stats.stddev() if count > 1 else float("NaN"):.2f}',
            'min': f'{stats.minimum():.2f}',
            'max': f'{stats.maximum():.2f}',
        })

    return res


def print_all_timing() -> None:
    global _stats
    for name in _stats:
        print_timing(name)


def print_timing(name: str) -> None:
    global _stats
    stats = _stats.get(name, None)
    if stats is None:
        logging.debug(f'Openfabric - timing_name="{name}", avg=never_recorded')
    else:
        count = len(stats)
        logging.debug(f'Openfabric - timing_name="{name}", '
                      f'avg={stats.mean():.4g} '
                      f'count={count} '
                      f'stddev={stats.stddev() if count > 1 else float("NaN"):.4g} '
                      f'min={stats.minimum():.4g} '
                      f'max={stats.maximum():.4g} '
                      )


def clear_timings() -> None:
    global _stats
    _stats.clear()


def MeasureTime(f_py=None, no_print=True, disable_gc=False, name: Optional[str] = None):
    assert callable(f_py) or f_py is None

    def _decorator(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            gcold = gc.isenabled()
            if disable_gc:
                gc.disable()
            start_time = timeit.default_timer()
            try:
                result = f(*args, **kwargs)
            finally:
                elapsed = timeit.default_timer() - start_time
                if disable_gc and gcold:
                    gc.enable()
                fname = name or f.__name__
                add_timing(fname, elapsed, no_print=no_print)
            return result

        return _wrapper

    return _decorator(f_py) if callable(f_py) else _decorator


class MeasureBlockTime:
    def __init__(self, name: str, no_print=False, disable_gc=False):
        self.name = name
        self.no_print = no_print
        self.disable_gc = disable_gc

    def cur_elapsed(self) -> float:
        return timeit.default_timer() - self.start_time

    def __enter__(self):
        self.gcold = gc.isenabled()
        if self.disable_gc:
            gc.disable()
        self.start_time = timeit.default_timer()
        return self

    def __exit__(self, ty, val, tb):
        self.elapsed = self.cur_elapsed()
        if self.disable_gc and self.gcold:
            gc.enable()
        self.stats = add_timing(self.name, self.elapsed, no_print=self.no_print)
        return False  # re-raise any exceptions
