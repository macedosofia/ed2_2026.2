# Preparação de countries.json

1. Manter o documento como uma lista JSON. A lista vazia atual é apenas uma reserva, não a base de demonstração concluída.
2. Preparar um registro por país com os campos textuais obrigatórios `codigo`, `pais`, `regiao`, `operadora` e `tecnologia`.
3. Incluir os países do enunciado: BR/Brasil, PT/Portugal, ES/Espanha, FR/França, IT/Itália, US/Estados Unidos, CA/Canadá e JP/Japão.
4. Preencher regiões, operadoras fictícias e tecnologias de forma coerente. Para o exemplo IT, o enunciado usa Itália, Europa, Operadora IT e 5G. Os demais dados de operadora/tecnologia serão definidos pela equipe.
5. Usar códigos únicos normalizados e UTF-8 para preservar acentos. Não incluir comentários no JSON: o formato não os admite.
6. Validar o arquivo e carregar cada registro na Hash ao iniciar. Não usar a lista JSON como mecanismo de consulta.
7. Após cadastro, alteração ou remoção, salvar a listagem obtida da Hash; nunca regravar após uma operação recusada.
8. Demonstrar persistência encerrando e iniciando novamente a aplicação. Usar cópias temporárias nos testes para preservar esta base.

Responsável: Pessoa 3. Revisão: Pessoa 1. As instruções deste documento são os comentários associados ao arquivo JSON.
