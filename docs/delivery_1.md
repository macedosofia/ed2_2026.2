# Primeira entrega — prazo 20/10/2026

Revisão técnica em **20/10/2026**. A aplicação oficial está em
`globalsim/`, com oito países na base inicial e **25 testes aprovados na entrega original**.
Este checklist foi conferido com o código, os testes e a documentação
presente no repositório. O enunciado original continua sendo a referência
para os critérios de avaliação da disciplina.

Após a apresentação, a Tabela Hash manual foi substituída pelo dicionário
nativo (`dict`) do Python, conforme orientação da professora. A versão
refatorada foi validada em **23/10/2026**, com **30 testes aprovados**.

## Implementação e validação

Checklist da entrega original de 20/10/2026:

- [x] Hash, modelo, serviço, persistência, rotas e templates separados.
- [x] Contratos revisados contra a implementação em `contracts.md`.
- [x] Página inicial, cadastro, consulta, listagem, edição e remoção.
- [x] Todos os campos obrigatórios validados; códigos normalizados e únicos.
- [x] Código imutável na edição e tratamento de país inexistente.
- [x] Hash própria com encadeamento separado e instrumentação, utilizada na entrega original.
- [x] Consultas pela Hash, sem leitura direta do JSON.
- [x] Carga inicial e persistência de cadastro, edição e remoção após reinício.
- [x] JSON inválido rejeitado sem sobrescrever o arquivo.
- [x] Falhas de gravação preservam registros, arquivo anterior e métricas.
- [x] Gravação atômica e limpeza dos temporários verificadas.
- [x] Mutações por POST e redirecionamento 303; remoção por GET recusada.
- [x] Uso de request, render_template, redirect, Jinja e formulários HTML.
- [x] Testes separados de modelo, serviço e persistência concluídos.
- [x] Oito países em `globalsim/data/countries.json` e cópia em `globalsim/data/countries.demo.json`.
- [x] Cobertura dos oito países validada nas rotas Web.
- [x] Colisão IT/DE e métricas antes/depois verificadas na implementação original.
- [x] Remoção de DE sem perder IT e reinício com os oito países verificados.

Atualizações posteriores à entrega:

- [x] Substituição da Hash manual pelo `dict` do Python.
- [x] Preservação das operações de inserção, busca, atualização, remoção e listagem.
- [x] Instrumentação adaptada para acompanhar as operações realizadas.
- [x] Testes da Tabela Hash atualizados para a nova implementação.
- [x] Reorganização da aplicação para a pasta `globalsim/`.
- [x] Validação da versão refatorada com 30 testes aprovados.

Para repetir a validação atual, na raiz do repositório, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
```

Atualmente, são 4 testes de modelo, 5 de serviço, 1 de demonstração,
6 de Hash, 5 de persistência e 9 de rotas, totalizando **30 testes**.
As bases de teste são temporárias.

## Documentação e versão

- [x] README com equipe, instalação, execução, rotas e estrutura.
- [x] Diferencial escolhido e integração futura documentados.
- [x] Situação da proposta registrada: aprovada pela professora.
- [x] Dados e roteiro de demonstração prontos.
- [x] Documentação atualizada para a base preenchida e os 25 testes da entrega original.
- [x] Documentação revisada após a refatoração para `dict` e os 30 testes atuais.

A versão final da primeira entrega é identificada por `etapa-1-final`.
A tag anterior `etapa-1` permanece preservada. As refatorações posteriores
são registradas em novos commits, sem alterar o histórico da entrega.

A implementação do recomendador, da Árvore B e do Grafo pertence às
próximas etapas, conforme o escopo documentado.

## Roteiro de apresentação

Roteiro atualizado para a implementação atual com `dict`:

1. Na raiz do repositório, com o ambiente virtual ativo, execute `python -m flask --app globalsim.app:create_app run --debug`.
2. Consulte IT e depois DE: inicialmente, IT tem cobertura e DE não está cadastrado.
3. Em `/instrumentation`, observe os 8 países cadastrados, os registros carregados inicialmente e as métricas de buscas, inserções, atualizações e remoções.
4. Cadastre DE, Alemanha, Europa, Operadora DE, 5G. A quantidade de países passa de 8 para 9 e a instrumentação registra a inserção.
5. Tente cadastrar DE novamente. A duplicata é recusada sem alterar a quantidade de países.
6. Edite a operadora de DE e consulte sua cobertura para conferir a mudança. Observe também a métrica de atualizações.
7. Remova DE com a confirmação do formulário. IT continua disponível e a quantidade de países volta a 8. Observe a métrica de remoções.
8. Reinicie o servidor. IT continua presente e DE continua ausente. Os registros são carregados novamente do JSON e os contadores de operações da nova instância são reinicializados.
9. Explique que a implementação atual utiliza o `dict` do Python, que gerencia internamente as colisões. Por isso, a instrumentação acompanha as operações, sem contabilizar colisões ou ocupação de baldes.
10. Apresente o diferencial aprovado pela professora e sua integração futura com as três estruturas.

Se a base tiver sido modificada, siga [as instruções de restauração](../globalsim/data/README.md)
antes da apresentação, preservando uma cópia dos dados atuais.

## Confirmações externas

- [x] Registrar o retorno da professora sobre o diferencial: proposta aprovada.
- [ ] Confirmar a submissão oficial pelo canal da disciplina: endereço e
  procedimento não constam no repositório. Publicar no GitHub não comprova essa submissão.
- [ ] Confirmar a revisão cruzada por outro integrante e o ensaio de apresentação.