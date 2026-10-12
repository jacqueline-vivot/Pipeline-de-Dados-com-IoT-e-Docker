# Validação e pendências

## Concluído

### Rodada ampliada sem Docker - 12/10/2026

**Resultado: 18 testes aprovados em 25,92 segundos, sem falhas ou testes ignorados.** Evidência automatizada: [test-results.xml](test-results.xml).

| Área | Verificação | Resultado |
|---|---|---|
| Transformação | Datas dia/mês, campos ausentes, espaços, categorias desconhecidas, temperaturas textuais e infinitas, arquivo sem leituras válidas | Aprovado |
| Identidade | Duplicatas idênticas removidas; IDs conflitantes rejeitados; IDs distintos no mesmo instante preservados | Aprovado |
| Carga real | 97.605 registros após a primeira carga e após a repetição | Aprovado |
| Atualização | Nova temperatura para um ID existente atualiza o registro sem aumentar a contagem | Aprovado |
| Transação | Erro SQL provocado após inserção reverte a alteração e mantém a temperatura original | Aprovado |
| Views | Todas as linhas, grupos, contagens, médias e extremos das três views comparados a agregações independentes em pandas | Aprovado |
| Dashboard | Três gráficos; filtros In, Out e seleção vazia; indicadores e botão de atualização | Aprovado |
| Falhas do dashboard | Banco indisponível e tabela vazia mostram mensagens apropriadas sem exceção não tratada | Aprovado |
| Dependências | `pip check`, importações e compilação dos arquivos Python | Aprovado |
| Compose | YAML validado contra o esquema JSON oficial de compose-spec; referências e serviços conferidos | Aprovado estaticamente |
| Proteção de arquivos | `.env`, senha temporária, CSV e ambiente virtual ignorados pelo Git | Aprovado |
| Isolamento | Dados originais preservados em 97.605 linhas e nenhum schema temporário restante | Aprovado |

Os testes de PostgreSQL usam schemas temporários com nomes únicos, removidos ao final. A validação de erro usa dados sintéticos nesse espaço isolado. O dashboard foi testado nesta rodada com Streamlit AppTest; as capturas e a revisão visual no navegador foram feitas na rodada anterior.

O esquema oficial utilizado para a validação está em https://raw.githubusercontent.com/compose-spec/compose-spec/main/schema/compose-spec.json. A validação estática não executa nem constrói imagens, não resolve dependências Linux e não comprova comportamento de rede, volumes ou inicialização dos contêineres.

### Como repetir a suíte ampliada

Instale `requirements-dev.txt` e defina `TEST_DATABASE_URL` com uma conexão PostgreSQL de teste cujo usuário possa criar schemas. Execute:

```powershell
.venv\Scripts\python -m pytest -q --junitxml=docs/test-results.xml
```

Sem `TEST_DATABASE_URL`, os seis testes de integração são ignorados e apenas os 12 testes de transformação rodam. Não utilize credenciais de produção. A rodada documentada acima executou todos os 18 testes contra o PostgreSQL portátil já disponível neste PC.

### Verificações anteriores

- Base real do Kaggle baixada e tratada: 97.606 linhas de origem, uma repetição de ID, 97.605 registros válidos.
- A suíte inicial de quatro testes de transformação passou e foi ampliada na rodada descrita acima.
- Código Python, três views SQL, Dockerfile, Compose, README e roteiro de vídeo implementados.
- Integração real com PostgreSQL 17 portátil local aprovada: duas cargas mantiveram 97.605 registros, as contagens das views conferiram e as mínimas diárias não ultrapassaram as máximas.
- Dashboard aberto no navegador e três gráficos revisados. O filtro interno exibiu 20.345 leituras, média 30,5 °C e faixa de 21 a 41 °C; ao restaurar os dois ambientes, retornou a 97.605 leituras. Capturas reais em `docs/dashboard-*.png`.

## Como verificar a integração

`scripts/validate_database.py` executa duas cargas contra o PostgreSQL configurado, verifica que o total permanece em 97.605 e confere as agregações. O resultado de uma execução bem-sucedida fica em `docs/integracao.json`.

## Limitação do ambiente

Docker Desktop e WSL não estão instalados neste computador. Por opção da usuária, a instalação foi adiada. A execução em contêiner permanece pendente mesmo que os testes com PostgreSQL portátil local passem.

## Antes da entrega

1. Instalar Docker Desktop/WSL e executar as instruções do README.
2. Confirmar que os serviços de banco e dashboard estão ativos e a carga terminou com código zero.
3. Conferir os gráficos e os registros no banco; atualizar o relatório com evidências da execução Docker.
4. Publicar os arquivos no repositório público e confirmar o acesso.
5. Gravar, publicar e testar o link do vídeo de até quatro minutos.

Para reconstruir o PDF, instale `requirements-dev.txt` e execute `python scripts/build_report.py`. As capturas em `docs/dashboard-*.png` são incluídas automaticamente.
