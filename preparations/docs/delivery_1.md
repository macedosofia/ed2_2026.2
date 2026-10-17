# Roteiro da entrega 1 — prazo 20/10/2026

O enunciado define os requisitos; o cronograma distribui o trabalho. O núcleo de países já foi implementado e possui testes automatizados. Este checklist permanece como roteiro de aceite da equipe, incluindo preparação dos dados, revisão e demonstração ainda pendentes.

Atualização em 07/10/2026: os seis testes automatizados passaram. Itens marcados correspondem à implementação e às verificações técnicas; apresentação e revisão por integrantes permanecem pendentes.

## Etapa 1 — alinhar módulos

- [x] Modularizar Hash, modelo, serviço, persistência, Flask e templates.
- [x] Implementar os módulos e documentar seus contratos em `contracts.md`.
- [ ] Executar revisões cruzadas previstas no README.

## Etapa 2 — integrar e instrumentar

- [x] Integrar o fluxo JSON → Hash → serviço → rotas → templates.
- [x] Verificar operações de países, gravação e reinício por testes automatizados.
- [x] Implementar a página de instrumentação e testar colisões e remoção na Hash.
- [x] Testar arquivo inválido, falha de gravação e consultas sem leitura direta do JSON.
- [ ] Completar os testes separados de modelo, serviço e persistência, cujos arquivos estão vazios.
- [ ] Demonstrar na interface uma colisão e as métricas antes e depois das operações.

## Etapa 3 — conferir critérios de aceite

- [x] Página inicial disponível.
- [x] Cadastro, consulta por código, listagem, alteração e remoção funcionando.
- [x] Campos do país validados e códigos duplicados/inexistentes tratados.
- [x] Tabela Hash própria utilizada efetivamente, com colisões tratadas.
- [x] Instrumentação básica implementada na interface e descrita no README.
- [x] Carga dos registros JSON na Hash ao iniciar, verificada nos testes.
- [ ] JSON preenchido com os oito países de demonstração; atualmente contém uma lista vazia.
- [x] Persistência verificada após recriar a aplicação nos testes.
- [x] Alterações por POST e fluxo Post/Redirect/Get verificado.
- [x] Uso de request, render_template, redirect, Jinja e formulários HTML implementado.
- [x] Estrutura separada das rotas e consultas sem busca direta no JSON.
- [x] README com instalação, execução, rotas e descrição da estrutura.
- [ ] README com identificação da equipe e diferencial escolhido.
- [x] Proposta inicial de diferencial e integração futura documentada.
- [ ] Descrição inicial do diferencial definida e situação da aprovação registrada.
- [x] Seis testes automatizados executados com sucesso.
- [ ] Cenários de testes revisados por outro integrante.
- [ ] Todos conseguem explicar a Hash, a aplicação e a persistência.

## Etapa 4 — demonstrar

1. Iniciar com a base dos oito países e abrir a página inicial e a listagem.
2. Consultar IT e um código válido ainda não cadastrado; mostrar os diferentes resultados.
3. Cadastrar um novo país, tentar duplicá-lo, alterar seus dados e conferir a cobertura.
4. Demonstrar duas chaves que colidem na função implementada e remover uma sem perder a outra.
5. Mostrar as métricas antes e depois das operações.
6. Reiniciar, conferir os dados persistidos e explicar a carga na Hash.
7. Apresentar a descrição do diferencial e sua integração planejada.
