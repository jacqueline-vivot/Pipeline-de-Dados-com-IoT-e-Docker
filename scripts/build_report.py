"""Gera o relatório acadêmico com resultados e evidências disponíveis."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf"
OUT.mkdir(parents=True, exist_ok=True)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Cover", fontSize=29, leading=35, textColor=colors.HexColor("#123052"), spaceAfter=25))
styles["Normal"].fontSize = 10.5
styles["Normal"].leading = 16
styles["Normal"].spaceAfter = 10
styles["Heading1"].textColor = colors.HexColor("#123052")
story = []


def p(value, style="Normal"):
    story.append(Paragraph(value, styles[style]))


def page(title):
    story.append(PageBreak())
    p(title, "Heading1")


p("DISRUPTIVE ARCHITECTURES<br/>IoT, Big Data e IA")
story.append(Spacer(1, 65))
p("Pipeline de Dados<br/>com IoT e Docker", "Cover")
p("Leituras de temperatura: da ingestão à visualização")
story.append(Spacer(1, 55))
p("<b>Jacqueline dos Santos Vivot</b><br/>RA 125866")
p("Projeto acadêmico • Outubro de 2026")
story.append(Spacer(1, 55))
p("Python / pandas / SQLAlchemy<br/>PostgreSQL / Docker Compose<br/>Streamlit / Plotly")
p("Fonte: Temperature Readings: IoT Devices, disponibilizada por Atul Anand Jha no Kaggle.")

page("1. Contextualização e proposta")
p("Dispositivos de Internet das Coisas geram observações que precisam ser organizadas para apoiar decisões. Arquivos brutos, isoladamente, dificultam consultas, comparação de ambientes e identificação de variações. O projeto implementa um pipeline em lote para validar leituras históricas de temperatura, armazená-las em um banco relacional e apresentá-las em gráficos interativos.")
p("<b>Fluxo:</b> CSV do Kaggle → tratamento com pandas → carga via SQLAlchemy → PostgreSQL → três views SQL → dashboard Streamlit com Plotly.")
p("O Docker Compose descreve três serviços: banco, processamento e dashboard. Uma verificação de saúde permite iniciar o processamento somente quando o PostgreSQL está pronto; o dashboard depende da conclusão bem-sucedida da carga. Um volume preserva os dados entre reinicializações.")
p("O escopo é descritivo e usa um arquivo histórico. Não existe sensor conectado ao vivo nem modelo treinado de inteligência artificial. Embora a arquitetura seja uma introdução a pipelines de dados, o volume da base não caracteriza, por si só, uma solução distribuída de Big Data.")
p("2. Fonte e modelo de dados", "Heading1")
p("A base possui as colunas id, room_id/id, noted_date, temp e out/in. O identificador original da leitura se torna a chave primária reading_id; room_id/id é mapeado para device_id; noted_date se torna observed_at; temp, temperature; e out/in, location.")
p("O nome device_id é usado para compatibilidade com o exemplo da disciplina, mas a fonte contém apenas o valor Room Admin. Não é possível inferir quantos sensores físicos foram utilizados. In e Out distinguem ambientes internos e externos.")
p("As datas são interpretadas explicitamente como dia-mês-ano, hora e minuto, sem fuso informado. A análise mantém os horários da fonte. A tabela registra temperaturas numéricas e restringe o ambiente aos valores In e Out.")

page("3. Implementação e reprodução")
for title, body in [
    ("Preparação", "Foi criado um ambiente Python isolado e instaladas as dependências. A base real foi baixada do Kaggle. As versões diretas utilizadas estão registradas em requirements.txt."),
    ("Validação", "O pipeline verifica as colunas, normaliza espaços nos identificadores, converte datas e temperaturas e rejeita campos ausentes, temperaturas não finitas e categorias desconhecidas. Valores extremos válidos são preservados para análise."),
    ("Duplicidade", "Uma repetição idêntica de ID foi removida. IDs repetidos com informações divergentes interrompem a carga para evitar escolha silenciosa de uma versão. Leituras diferentes feitas no mesmo minuto são preservadas."),
    ("Persistência", "A carga usa tabela temporária e uma transação PostgreSQL. INSERT ON CONFLICT atualiza IDs existentes e insere novos. Um bloqueio serializa cargas concorrentes. A reexecução do mesmo arquivo não deve aumentar o total de registros."),
    ("Visualização", "O Streamlit consulta as três views. Há filtro de ambiente, indicadores de quantidade e temperatura, gráficos interativos e exportação do resumo diário. As médias gerais são ponderadas pelo número de leituras."),
    ("Docker", "Para reproduzir, instale Docker Desktop com WSL 2, salve o CSV em data/IOT-temp.csv, copie .env.example para .env e defina a senha. Execute docker compose up --build -d e acesse http://localhost:8501. Os detalhes e comandos de verificação estão no README.")]:
    p(f"<b>{title}.</b> {body}")
p("A configuração Docker foi preparada, mas sua execução neste computador aguarda instalação do Docker Desktop e WSL, adiada por decisão da usuária. A validação local de PostgreSQL, quando registrada, não equivale a um teste em contêiner.")

page("4. Views SQL e finalidade")
for name, body in [
    ("avg_temp_por_dispositivo", "Agrupa por device_id e location. Calcula AVG(temperature) e COUNT(*). Permite comparar as médias dos ambientes interno e externo, além de verificar o número de observações que sustenta cada média. Não compara diferentes sensores físicos nesta base."),
    ("leituras_por_hora", "Extrai a hora de observed_at e agrupa por hora e location. COUNT(*) mostra o volume acumulado em cada uma das 24 horas ao longo de todo o período. É útil para examinar a concentração da coleta; não mede temperatura nem representa 24 horas consecutivas."),
    ("temp_max_min_por_dia", "Converte observed_at para DATE e agrupa por data e location. Calcula MAX, MIN e AVG da temperatura. Permite observar amplitudes diárias e investigar dias com extremos. Dias sem registros não devem ser tratados como temperatura zero.")]:
    p(name, "Heading2")
    p(body)
p("As views são consultas armazenadas, calculadas sobre os registros disponíveis a cada consulta. Não duplicam fisicamente a base como uma tabela materializada. As definições completas ficam em sql/views.sql.")
p("<b>Exemplo de conferência:</b><br/><font face='Courier' size='9'>SELECT COUNT(*) FROM temperature_readings;<br/>SELECT * FROM avg_temp_por_dispositivo;</font>")

page("5. Resultados e interpretação")
p("A versão analisada contém 97.606 linhas de origem, nenhuma linha inválida e um ID duplicado. Após a limpeza, restam <b>97.605 leituras</b>, entre <b>28/07/2018 07:06 e 08/12/2018 09:30</b>.")
table = Table([["Ambiente", "Leituras", "Média", "Mínima", "Máxima"],
    ["Interno", "20.345", "30,45 °C", "21 °C", "41 °C"],
    ["Externo", "77.260", "36,27 °C", "24 °C", "51 °C"]], colWidths=[100, 85, 85, 85, 85])
table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123052")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("BOTTOMPADDING", (0,0), (-1,-1), 12),
    ("TOPPADDING", (0,0), (-1,-1), 12), ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#edf3f8"))]))
story.append(table)
story.append(Spacer(1, 18))
p("<b>Diferença de médias:</b> o ambiente externo apresenta média aproximadamente 5,81 °C superior à do interno. As amostras possuem tamanhos diferentes e não necessariamente correspondem aos mesmos instantes. A comparação não demonstra causalidade nem eficiência de climatização.")
p("<b>Extremos:</b> a leitura máxima externa é 51 °C; a interna, 41 °C. Em uma aplicação real, esses valores justificariam investigação sobre ambiente, instalação e calibração do sensor. Não são automaticamente erros ou evidência de risco operacional.")
p("<b>Aplicações:</b> acompanhamento de condições de armazenamento, apoio à climatização e alertas com limites definidos por especialistas do contexto. A contagem por hora ajuda a avaliar a distribuição da coleta; a variação diária apoia a investigação de eventos.")
p("<b>Evoluções:</b> coletar via MQTT, incluir identificação física e calibração dos sensores, padronizar fuso horário, monitorar qualidade e testar modelos de anomalias com separação temporal de treino e avaliação. Para volumes maiores, avaliar ingestão em blocos e particionamento do banco.")

page("6. Evidências e validação")
p("Os testes automatizados de transformação verificam formato de datas, descarte de valores não finitos, remoção de duplicatas, rejeição de IDs conflitantes e ausência de colunas obrigatórias. O processamento real confirmou os totais apresentados neste relatório.")
integration = ROOT / "docs/integracao.json"
if integration.exists():
    p("A integração com PostgreSQL local foi executada: duas cargas mantiveram 97.605 registros; as somas das views de média e hora conferiram com a tabela; e as mínimas diárias não excederam as máximas. Detalhes em docs/integracao.json.")
else:
    p("A validação completa da carga no PostgreSQL ainda está pendente. Os resultados descritivos foram calculados diretamente sobre o CSV tratado.")
shots = sorted((ROOT / "docs").glob("dashboard-*.png"))
if not shots:
    p("Capturas reais do dashboard ainda precisam ser acrescentadas após a execução do banco. Este documento não deve ser considerado a entrega final enquanto essa evidência estiver pendente.")
for shot in shots:
    page("Dashboard: " + shot.stem.replace("dashboard-", ""))
    im = Image(str(shot))
    ratio = min(475/im.imageWidth, 630/im.imageHeight)
    im.drawWidth = im.imageWidth * ratio
    im.drawHeight = im.imageHeight * ratio
    story.append(im)
    p("Captura real do Streamlit consultando as views em PostgreSQL local. Execução em Docker pendente neste PC.")

page("7. Referências e entrega")
for label, url in [
    ("Atul Anand Jha. Temperature Readings: IoT Devices. Kaggle", "https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices"),
    ("Docker. Instalação do Docker Desktop no Windows", "https://docs.docker.com/desktop/setup/install/windows-install/"),
    ("PostgreSQL. Documentação", "https://www.postgresql.org/docs/"),
    ("pandas. Documentação", "https://pandas.pydata.org/docs/"),
    ("SQLAlchemy. Documentação", "https://docs.sqlalchemy.org/"),
    ("Streamlit. Documentação", "https://docs.streamlit.io/"),
    ("Plotly. Gráficos em Python", "https://plotly.com/python/")]:
    p(f"<b>{label}</b><br/><link href='{url}' color='#2563eb'>{url}</link>")
p("Material orientador: enunciado da disciplina fornecido pela estudante, 'Pipeline de Dados com IoT e Docker'.")
p("<b>Repositório:</b> github.com/jacqueline-vivot/Pipeline-de-Dados-com-IoT-e-Docker")
p("<b>Pendências para envio:</b> executar e conferir a versão Docker; confirmar publicação e acesso público do repositório; gravar e publicar o vídeo de até quatro minutos. O roteiro está em docs/roteiro-video.md.")


def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor("#dbe5ed"))
    canvas.line(48, 43, 547, 43)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#53677a"))
    canvas.drawString(48, 30, "Jacqueline dos Santos Vivot | RA 125866")
    canvas.drawRightString(547, 30, str(doc.page))


SimpleDocTemplate(str(OUT / "Relatorio-Pipeline-IoT-Jacqueline.pdf"), pagesize=A4,
    rightMargin=50, leftMargin=50, topMargin=48, bottomMargin=60,
    title="Pipeline de Dados com IoT e Docker", author="Jacqueline dos Santos Vivot").build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT / "Relatorio-Pipeline-IoT-Jacqueline.pdf")
