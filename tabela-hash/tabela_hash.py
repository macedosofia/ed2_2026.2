class TabelaHash:
    def __init__(self, tamanho=11):
        self.tamanho = tamanho
        self.baldes = [[] for _ in range(tamanho)]
        self.quantidade = 0

    @staticmethod
    def normalizar(codigo):
        return codigo.strip().upper()

    def _indice(self, codigo):
        h = 0
        for c in codigo:
            h = (h * 31 + ord(c)) % self.tamanho
        return h

    def inserir(self, codigo, dados):
        codigo = self.normalizar(codigo)
        balde = self.baldes[self._indice(codigo)]
        for par in balde:
            if par[0] == codigo:
                raise KeyError("Código duplicado")
        balde.append([codigo, dados])
        self.quantidade += 1
        

    def buscar(self, codigo):
        codigo = self.normalizar(codigo)
        for chave, dados in self.baldes[self._indice(codigo)]:
            if chave == codigo:
                return dados
        return None

    def atualizar(self, codigo, novos_dados):
        codigo = self.normalizar(codigo)
        for par in self.baldes[self._indice(codigo)]:
            if par[0] == codigo:
                par[1] = novos_dados
                return True
        return False

    def remover(self, codigo):
        codigo = self.normalizar(codigo)
        balde = self.baldes[self._indice(codigo)]
        for i, (chave, _) in enumerate(balde):
            if chave == codigo:
                balde.pop(i)
                self.quantidade -= 1
                return True
        return False

    def listar(self):
        return [(c, d) for balde in self.baldes for c, d in balde]

    def fator_de_carga(self):
        return self.quantidade / self.tamanho

    def colisoes(self):
        return sum(max(0, len(b) - 1) for b in self.baldes)

    def ocupacao(self):
        return [len(b) for b in self.baldes]