from src.utils.statistics import Statistics

class ConditionCache:
    all_cache = {}
    monotone_cache = {}

    enabled = True

    @staticmethod
    def disable():
        ConditionCache.enabled = False

    @staticmethod
    def enable():
        ConditionCache.enabled = True

    @staticmethod
    def update(key : str, value : bool, monotone: bool = False):

        if not ConditionCache.enabled:
            return

        if monotone:
            ConditionCache.monotone_cache[key] = value
        else:
            ConditionCache.all_cache[key] = value

    @staticmethod
    def canSkipSolver(keys: list[str], monotone: bool = False) -> bool:
        cache = ConditionCache.monotone_cache if monotone else ConditionCache.all_cache

        if not ConditionCache.enabled:
            return False

        canSkip = all(key != "" and key in cache for key in keys) 
        
        if canSkip:
            if monotone:
                Statistics.log_cache_hit_monotone()
            else:
                Statistics.log_cache_hit_non_monotone()
        else:
            if monotone:
                Statistics.log_cache_miss_monotone()
            else:
                Statistics.log_cache_miss_non_monotone()
        
        return canSkip

    @staticmethod
    def invalidate(monotone: bool = False):

        if not ConditionCache.enabled:
            return

        if monotone:
            ConditionCache.monotone_cache = {}
            Statistics.log_monotone_cache_invalidation()
        else:
            ConditionCache.all_cache = {}
            Statistics.log_non_monotone_cache_invalidation()

    @staticmethod
    def invalidateAll():
        ConditionCache.invalidate(monotone=True)
        ConditionCache.invalidate(monotone=False)

    @staticmethod
    def clear():
        ConditionCache.all_cache = {}
        ConditionCache.monotone_cache = {}

    @staticmethod
    def get(key: str | list[str],  monotone: bool = False) -> bool:
        cache = ConditionCache.monotone_cache if monotone else ConditionCache.all_cache

        if isinstance(key, str):
            return cache.get(key, False)
        elif isinstance(key, list):
            return all(cache.get(k, False) for k in key)
        else:
            return False