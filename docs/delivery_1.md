# Primeira entrega — prazo 20/10/2026

Revisão técnica em **20/10/2026**. A aplicação oficial está em
`globalsim/`, com oito países na base inicial e **25 testes aprovados**.
Este checklist foi conferido com o código, os testes e a documentação
presente no repositório. O enunciado original continua sendo a referência
para os critérios de avaliação da disciplina.

## Implementação e validação

- [x] Hash, modelo, serviço, persistência, rotas e templates separados.
- [x] Contratos revisados contra a implementação em `contracts.md`.
- [x] Página inicial, cadastro, consulta, listagem, edição e remoção.
- [x] Todos os campos obrigatórios validados; códigos normalizados e únicos.
- [x] Código imutável na edição e tratamento de país inexistente.
- [x] Hash própria com encadeamento separado e instrumentação.
- [x] Consultas pela Hash, sem leitura direta do JSON.
- [x] Carga inicial e persistência de cadastro, edição e remoção após reinício.
- [x] JSON inválido rejeitado sem sobrescrever o arquivo.
- [x] Falhas de gravação preservam registros, arquivo anterior e métricas.
- [x] Gravação atômica e limpeza dos temporários verificadas.
- [x] Mutações por POST e redirecionamento 303; remoção por GET recusada.
- [x] Uso de request, render_template, redirect, Jinja e formulários HTML.
- [x] Testes separados de modelo, serviço e persistência concluídos.
- [x] Oito países em `data/countries.json` e cópia em `countries.demo.json`.
- [x] Cobertura dos oito países validada nas rotas Web.
- [x] Colisão IT/DE e métricas antes/depois verificadas nas páginas renderizadas.
- [x] Remoção de DE sem perder IT e reinício com os oito países verificados.

Para repetir a validação, dentro de `preparations`, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
```

São 4 testes de modelo, 5 de serviço, 1 de demonstração, 1 de Hash,
5 de persistência e 9 de rotas. As bases de teste são temporárias.

## Documentação e versão

- [x] README com equipe, instalação, execução, rotas e estrutura.
- [x] Diferencial escolhido e integração futura documentados.
- [x] Situação da proposta registrada: submetida, aguardando retorno.
- [x] Dados e roteiro de demonstração prontos.
- [x] Documentação atualizada para a base preenchida e os 25 testes.

A versão final é identificada por `etapa-1-final`. A tag anterior `etapa-1`
permanece preservada. A implementação do recomendador, da Árvore B e do
Grafo pertence às próximas etapas, conforme o escopo documentado.

## Roteiro de apresentação

1. Dentro de `preparations`, execute `python app.py`. Abra a página inicial
   e `/countries`; a base inicial apresenta BR, PT, ES, FR, IT, US, CA e JP.
2. Consulte IT e depois DE: inicialmente, IT tem cobertura e DE não está cadastrado.
3. Em `/instrumentation`, observe 8 países, fator de carga `8/17` e zero
   colisões nas inserções posteriores à carga. A ocupação é o estado atual;
   os contadores de colisões acumulam eventos.
4. Cadastre DE, Alemanha, Europa, Operadora DE, 5G. IT e DE usam o balde 1.
   A quantidade passa a 9, o fator a `9/17` e surge uma colisão de operação.
5. Tente cadastrar DE novamente. A duplicata é recusada sem alterar a quantidade.
6. Edite a operadora de DE e consulte sua cobertura para conferir a mudança.
7. Remova DE com a confirmação do formulário. IT continua disponível; a
   quantidade volta a 8. A contagem acumulada de colisões não diminui.
8. Reinicie o servidor. IT continua presente e DE continua ausente. Os
   contadores de eventos são reinicializados e as colisões de carga recalculadas.
9. Apresente o diferencial documentado e sua integração futura com as três estruturas.

Se a base tiver sido modificada, siga [as instruções de restauração](../data/README.md)
antes da apresentação, preservando uma cópia dos dados atuais.

## Confirmações externas

- [ ] Registrar o retorno da professora sobre o diferencial.
- [ ] Confirmar a submissão oficial pelo canal da disciplina: endereço e
  procedimento não constam no repositório. Publicar no GitHub não comprova essa submissão.
- [ ] Confirmar a revisão cruzada por outro integrante e o ensaio de apresentação.

A revisão técnica e os testes acima foram executados. A participação de
outro integrante e o domínio oral de cada pessoa não podem ser atestados
pela execução automatizada. Para o ensaio, todos devem conseguir explicar
a função Hash, as colisões, as métricas, o fluxo HTTP, a persistência e a
recuperação em caso de falha.
