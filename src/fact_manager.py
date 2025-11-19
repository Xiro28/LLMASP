class FactManager:
    _facts = set()

    @classmethod
    def add_fact(cls, fact: str):
        cls._facts.add(fact)

    @classmethod
    def remove_fact(cls, fact: str):
        cls._facts.discard(fact)

    @classmethod
    def reset_facts(cls):
        cls._facts = set()

    @classmethod
    def get_all_facts(cls):
        return "\n".join(cls._facts)