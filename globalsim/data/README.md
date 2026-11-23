# Dados de países — Etapa 1

`countries.json` é a base de uso. A versão final já contém BR/Brasil,
PT/Portugal, ES/Espanha, FR/França, IT/Itália, US/Estados Unidos,
CA/Canadá e JP/Japão. Cada registro inclui `codigo`, `pais`, `regiao`,
`operadora` e `tecnologia`. As operadoras são fictícias.

`countries.demo.json` preserva os mesmos oito registros para restaurar a demonstração. A aplicação carrega a base de uso na Hash ao iniciar, consulta a estrutura em memória e persiste as alterações aprovadas. As consultas não usam a lista JSON como mecanismo de busca.

Para restaurar a demonstração, interrompa o servidor e, na raiz do repositório (`ed2_2026.2/`), com o ambiente virtual ativado, preserve os dados atuais antes da substituição:

```bash
backup_file=$(mktemp /tmp/globalsim-countries-XXXXXX.json)
cp globalsim/data/countries.json "$backup_file"
echo "Backup: $backup_file"
cp globalsim/data/countries.demo.json globalsim/data/countries.json
env -u PYTHONPATH python -m flask --app globalsim.app:create_app run --debug
```

Para recuperar os dados anteriores, pare o servidor e execute, no mesmo terminal:

```bash
cp "$backup_file" data/countries.json
```

Use uma lista JSON válida, códigos únicos com duas letras e UTF-8. Arquivos
inválidos são rejeitados sem sobrescrita. Os testes usam cópias temporárias,
preservando tanto a base de uso quanto o arquivo de demonstração.
