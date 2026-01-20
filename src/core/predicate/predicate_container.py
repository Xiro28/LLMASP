from src.core.predicate.condition_cache import ConditionCache

class PredicateContainer:
    _predicates = list()

    @staticmethod
    def add_predicate(predicate: str):
        PredicateContainer._predicates.append(predicate)
        #we have to invalidate non-monotone caches because new facts can affect them
        ConditionCache.invalidate(monotone=False)

    @staticmethod
    def remove_predicate(predicate: str):
        PredicateContainer._predicates.remove(predicate)

        #here instead we invalidate both caches because removing a fact can affect both monotone and non-monotone conditions
        ConditionCache.invalidateAll()
        
    @staticmethod
    def reset_container():
        PredicateContainer._predicates = list()
        ConditionCache.clear()

    @staticmethod
    def get_all_predicates():
        return "\n".join(PredicateContainer._predicates)