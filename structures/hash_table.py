class HashTable:
    def __init__(self, capacity=17):
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("A capacidade deve ser positiva.")
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0
        self.collisions = 0
        self.load_collisions = 0
        self.last_index = None

    def _index(self, code):
        value = 0
        for character in code:
            value = (value * 31 + ord(character)) % len(self.buckets)
        self.last_index = value
        return value

    def find(self, code):
        for record in self.buckets[self._index(code)]:
            if record["codigo"] == code:
                return record.copy()
        return None

    def insert(self, record):
        bucket = self.buckets[self._index(record["codigo"])]
        if any(item["codigo"] == record["codigo"] for item in bucket):
            raise ValueError("Já existe um país com esse código.")
        self.collisions += bool(bucket)
        bucket.append(record.copy())
        self.size += 1

    def update(self, code, record):
        if record["codigo"] != code:
            raise ValueError("O código do país não pode ser alterado.")
        bucket = self.buckets[self._index(code)]
        for index, item in enumerate(bucket):
            if item["codigo"] == code:
                bucket[index] = record.copy()
                return
        raise LookupError("País não encontrado.")

    def remove(self, code):
        bucket = self.buckets[self._index(code)]
        for index, item in enumerate(bucket):
            if item["codigo"] == code:
                self.size -= 1
                return bucket.pop(index).copy()
        raise LookupError("País não encontrado.")

    def list_all(self):
        return [record.copy() for bucket in self.buckets for record in bucket]

    def statistics(self):
        return {"capacity": len(self.buckets), "size": self.size,
                "load_factor": self.size / len(self.buckets),
                "collisions": self.collisions,
                "load_collisions": self.load_collisions,
                "operation_collisions": self.collisions - self.load_collisions,
                "occupancy": [len(bucket) for bucket in self.buckets],
                "last_index": self.last_index}
