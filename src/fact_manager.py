class FactManager:
    _facts = set()

    @staticmethod
    def add_fact(fact: str):
        FactManager._facts.add(fact)

    @staticmethod
    def remove_fact(fact: str):
        FactManager._facts.discard(fact)

    @staticmethod
    def reset_facts():
        FactManager._facts = set()

    @staticmethod
    def get_all_facts():
        return "\n".join(FactManager._facts)