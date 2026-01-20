class Statistics:
    llm_calls = 0
    llm_tokens_in = 0
    llm_tokens_out = 0

    solver_calls = 0
    
    cache_hits_monotone = 0
    cache_miss_monotone = 0
    monotone_cache_invalidations = 0

    cache_hits_non_monotone = 0
    cache_miss_non_monotone = 0
    non_monotone_cache_invalidations = 0

    @staticmethod
    def reset():
        Statistics.llm_calls = 0
        Statistics.llm_tokens_in = 0
        Statistics.llm_tokens_out = 0
        Statistics.cache_hits_monotone = 0
        Statistics.cache_miss_monotone = 0
        Statistics.cache_hits_non_monotone = 0
        Statistics.cache_miss_non_monotone = 0
        Statistics.monotone_cache_invalidations = 0
        Statistics.non_monotone_cache_invalidations = 0
        Statistics.solver_calls = 0

    @staticmethod
    def log_solver_call():
        Statistics.solver_calls += 1

    @staticmethod
    def log_llm_call(tokens_in: int, tokens_out: int):
        Statistics.llm_calls += 1
        Statistics.llm_tokens_in += tokens_in
        Statistics.llm_tokens_out += tokens_out

    @staticmethod
    def log_non_monotone_cache_invalidation():
        Statistics.non_monotone_cache_invalidations += 1
    
    @staticmethod
    def log_monotone_cache_invalidation():
        Statistics.monotone_cache_invalidations += 1

    @staticmethod
    def log_cache_hit_monotone():
        Statistics.cache_hits_monotone += 1

    @staticmethod
    def log_cache_miss_monotone():
        Statistics.cache_miss_monotone += 1

    @staticmethod
    def log_cache_hit_non_monotone():
        Statistics.cache_hits_non_monotone += 1

    @staticmethod
    def log_cache_miss_non_monotone():
        Statistics.cache_miss_non_monotone += 1

    @staticmethod
    def get_stats():
        return {
            "llm_calls": Statistics.llm_calls,
            "llm_tokens_in": Statistics.llm_tokens_in,
            "llm_tokens_out": Statistics.llm_tokens_out,
            "solver_calls": Statistics.solver_calls,
            "cache_hits_monotone": Statistics.cache_hits_monotone,
            "cache_miss_monotone": Statistics.cache_miss_monotone,
            "cache_hits_non_monotone": Statistics.cache_hits_non_monotone,
            "cache_miss_non_monotone": Statistics.cache_miss_non_monotone,
            "monotone_cache_invalidations": Statistics.monotone_cache_invalidations,
            "non_monotone_cache_invalidations": Statistics.non_monotone_cache_invalidations
        }
    
    @staticmethod
    def get_statistics_since(previous_stats: dict):
        current_stats = Statistics.get_stats()
        delta_stats = {}
        for key in current_stats:
            delta_stats[key] = current_stats[key] - previous_stats.get(key, 0)
        return delta_stats