# Descrição inicial do diferencial — proposta para discussão



## Checklist de acompanhamento

- [x] Documentar uma proposta inicial: recomendação de pacote a partir de um roteiro de viagem.
- [x] Descrever o problema, as entradas sugeridas e uma estratégia inicial de filtragem.
- [x] Descrever a integração prevista com Hash, Árvore B e Grafo.
- [x] Registrar cenários iniciais para critérios de aceite.
- [ ] Confirmar o diferencial escolhido pela equipe e a alternativa de reserva.
- [ ] Definir cobertura dos pacotes, limites e critério de desempate.
- [ ] Registrar responsáveis e consolidar o escopo para submissão.
- [ ] Submeter a proposta à professora e registrar seu retorno.
- [ ] Incorporar no README a descrição do diferencial escolhido.

Os itens marcados representam a documentação da candidata. A funcionalidade de recomendação será desenvolvida nas próximas etapas após a definição do escopo.

## Etapa 1 — discutir o problema e o escopo

Proposta: ajudar um viajante a escolher um pacote compatível com os destinos e as necessidades de sua viagem. Além de verificar cada país, a aplicação explicaria por que o pacote sugerido atende ao roteiro.

1. Confirmar a escolha com a equipe e definir uma alternativa de reserva.
2. Definir entradas mínimas: destinos, duração e necessidade de dados.
3. Definir explicitamente a cobertura e os limites de cada pacote; o nome de uma região sozinho não substitui os dados necessários para a recomendação.

## Etapa 2 — especificar o algoritmo e a integração

1. Usar a Hash para validar a cobertura de cada destino.
2. Nas próximas etapas, usar a Árvore B para recuperar cliente e pacote atual.
3. Propor um algoritmo de filtragem dos pacotes por cobertura, dados e validade, com critério de desempate documentado; não prometer menor preço sem dados de preço definidos.
4. Na etapa final, avaliar como o Grafo verificará conectividade entre destinos e como explicar destinos inalcançáveis.
5. Separar a recomendação da interface e justificar sua relevância funcional e algorítmica para aprovação da professora.

## Etapa 3 — definir critérios de aceite

1. Planejar um roteiro atendido por um pacote, um roteiro com país sem cobertura e um caso sem pacote compatível.
2. Explicar o resultado usando os critérios definidos, com desempate previsível.
3. Definir exemplos esperados para a integração cliente, Hash e Grafo nas entregas seguintes.

## Etapa 4 — registrar a decisão
