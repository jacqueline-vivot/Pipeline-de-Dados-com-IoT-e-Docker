# Validação real com Docker — 14/10/2026

O projeto foi construído e executado no Docker Desktop para Windows, com contêineres Linux e PostgreSQL 17. Não foi necessário corrigir o código, o Dockerfile ou o Compose.

## Resultados

- `docker compose config --quiet`: aprovado.
- `docker compose up --build -d`: imagens construídas e serviços iniciados; banco saudável, pipeline encerrado com código 0 e dashboard ativo em `http://localhost:8501`.
- `pip check` dentro do contêiner: nenhuma dependência incompatível.
- Suíte completa: **18 testes aprovados em 18,94 segundos**, sem falhas, erros ou testes ignorados. Evidência: [test-results-docker.xml](test-results-docker.xml).
- Base pública baixada pelo script do projeto: 97.606 linhas de origem, nenhuma inválida, um ID duplicado e **97.605 registros** no PostgreSQL.
- Reexecução da carga: a contagem permanece em 97.605.
- As três views foram comparadas com agregações independentes em pandas, incluindo contagens, médias, mínimos e máximos.
- Atualização de registros, reversão de transação após erro e mensagens do dashboard para banco vazio ou indisponível: aprovadas.
- Dashboard testado também com a base completa via Streamlit AppTest: três gráficos, indicadores, filtros In/Out, seleção vazia e atualização aprovados. Indicadores gerais: 97.605 leituras, média 35,1 °C e faixa de 21 a 51 °C.
- Navegador do Codex: dashboard carregado, três gráficos presentes e renderização inicial conferida visualmente.
- Persistência: após `docker compose down` sem remover volumes e recriação apenas do banco, foram confirmados 97.605 registros **antes de executar novamente o pipeline**.
- Nenhum schema temporário de teste permaneceu no banco.
- Projeto completo iniciado novamente; endpoint `/_stcore/health` respondeu HTTP 200 com `ok`.

Os testes rodaram em um contêiner temporário da imagem do pipeline, com `pytest==9.1.1` e os diretórios `tests`, `scripts` e `tmp` montados. A conexão `TEST_DATABASE_URL` foi construída a partir das credenciais locais, sem registrar a senha. Os testes de integração usam schemas temporários isolados, removidos ao final. O executor local está em `tmp/run_docker_validation.py` (ignorado pelo Git).

O arquivo `.env` com senha local e o CSV foram criados para executar o projeto e são ignorados pelo Git. Os arquivos de auditoria `qualidade.json` e `integracao.json` foram regenerados pelos scripts. Banco e dashboard foram deixados em execução. Nenhum commit ou push foi realizado.

Esta rodada resolve a pendência de execução Docker mencionada no README e na validação anterior. O PDF e a documentação anterior não foram reconstruídos ou reescritos nesta rodada.
