class HashTable:
    def __init__(self):
        self._records = {}

        self._loaded_records = 0
        self._lookups = 0
        self._hits = 0
        self._misses = 0
        self._insertions = 0
        self._updates = 0
        self._removals = 0

    @property
    def size(self):
        return len(self._records)

    def mark_loaded(self):
        self._loaded_records = len(self._records)
        self._insertions = 0
        self._updates = 0
        self._removals = 0

    def find(self, code):
        self._lookups += 1

        record = self._records.get(code)

        if record is None:
            self._misses += 1
            return None

        self._hits += 1
        return record.copy()

    def insert(self, record):
        code = record["codigo"]

        if code in self._records:
            raise ValueError("Já existe um país com esse código.")

        self._records[code] = record.copy()
        self._insertions += 1

    def update(self, code, record):
        if record["codigo"] != code:
            raise ValueError("O código do país não pode ser alterado.")

        if code not in self._records:
            raise LookupError("País não encontrado.")

        self._records[code] = record.copy()
        self._updates += 1

    def remove(self, code):
        if code not in self._records:
            raise LookupError("País não encontrado.")

        removed = self._records.pop(code)

        self._removals += 1

        return removed.copy()

    def list_all(self):
        return [record.copy() for record in self._records.values()]

    def statistics(self):
        return {
            "size": self.size,
            "keys": sorted(self._records),
            "loaded_records": self._loaded_records,
            "lookups": self._lookups,
            "hits": self._hits,
            "misses": self._misses,
            "insertions": self._insertions,
            "updates": self._updates,
            "removals": self._removals,
        }