# Roteiro do vídeo (aproximadamente 3min30s)

Autora: Jacqueline dos Santos Vivot · RA 125866. Leia, entenda e adapte as falas antes da gravação. Só declare a execução em Docker depois de realizá-la.

## 0:00-0:30 · Apresentação

“Olá, sou Jacqueline dos Santos Vivot, RA 125866. Este projeto organiza leituras históricas de temperatura de dispositivos IoT. O objetivo é transformar um arquivo de dados em informações consultáveis, usando Python, PostgreSQL, Docker e um dashboard interativo.”

## 0:30-1:10 · Arquitetura e tratamento

Mostre o README e a estrutura de pastas.

“A fonte é o conjunto Temperature Readings: IoT Devices, do Kaggle. O pandas verifica as colunas, converte as datas no formato dia, mês e ano e valida as temperaturas e os ambientes. Um ID duplicado foi removido, restando 97.605 leituras. O SQLAlchemy envia os dados ao PostgreSQL. A chave primária evita duplicação quando o pipeline é executado novamente.”

## 1:10-1:40 · Execução

Após instalar Docker, mostre `docker compose ps -a`, o log do pipeline e a consulta `SELECT COUNT(*) FROM temperature_readings;`.

“O Compose coordena três serviços: banco, processamento e dashboard. O banco precisa estar saudável antes da carga, e o dashboard inicia depois que ela termina. Os dados ficam preservados em um volume.”

## 1:40-2:50 · Demonstração

Abra o dashboard e alterne o filtro de ambiente.

“A primeira view calcula a média por identificador e ambiente. A base traz apenas Room Admin, sem identificar sensores físicos individualmente. A segunda view conta leituras por hora do dia, acumulando o período inteiro. A terceira mostra temperaturas mínimas e máximas por dia. Posso comparar ambientes internos e externos e baixar o resumo diário.”

## 2:50-3:30 · Conclusões e limites

“A média interna é 30,45 graus, e a externa é 36,27: uma diferença de cerca de 5,81 graus. Como as coletas têm frequências distintas, isso não comprova uma causa. Em uma aplicação real, o painel poderia apoiar alertas e decisões de climatização. Esta versão faz análise descritiva de dados históricos. Como evolução, seria possível adicionar coleta ao vivo e um modelo validado de detecção de anomalias.”

Encerre mostrando o repositório. Não exiba o arquivo `.env` nem credenciais. Confira áudio, duração e acesso ao link publicado.
