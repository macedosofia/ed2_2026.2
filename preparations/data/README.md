# Dados de países — Etapa 1

`countries.json` é a base de uso. A versão final já contém BR/Brasil,
PT/Portugal, ES/Espanha, FR/França, IT/Itália, US/Estados Unidos,
CA/Canadá e JP/Japão. Cada registro inclui `codigo`, `pais`, `regiao`,
`operadora` e `tecnologia`. As operadoras são fictícias.

`countries.demo.json` preserva os mesmos oito registros para restaurar a
demonstração. A aplicação carrega a base de uso na Hash ao iniciar, consulta
a estrutura em memória e persiste as alterações aprovadas. As consultas
não usam a lista JSON como mecanismo de busca.

Para restaurar a demonstração, interrompa o servidor e, dentro de `preparations`,
preserve os dados atuais antes da substituição:

```bash
backup_file=$(mktemp /tmp/globalsim-countries-XXXXXX.json)
cp data/countries.json "$backup_file"
echo "Backup: $backup_file"
cp data/countries.demo.json data/countries.json
python app.py
```

Para recuperar os dados anteriores, pare o servidor e execute, no mesmo terminal:

```bash
cp "$backup_file" data/countries.json
```

Use uma lista JSON válida, códigos únicos com duas letras e UTF-8. Arquivos
inválidos são rejeitados sem sobrescrita. Os testes usam cópias temporárias,
preservando tanto a base de uso quanto o arquivo de demonstração.
