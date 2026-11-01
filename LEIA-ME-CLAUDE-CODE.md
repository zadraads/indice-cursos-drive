# Índice de Cursos do Drive: continuação no Claude Code

> **Atualização 01/11/2026: etapas A a E concluídas** (sessão na nuvem do Claude Code, com o conector do Google Drive).
> - Saídas: `data5.json`, `indice-cursos.html` (modelo `page_head5.html`), `Indice-Cursos-Drive.xlsx` (abas Cursos, Trilhas e Duplicatas).
> - Para regerar tudo: `python3 crawl/aggregate.py && python3 build_final.py`.
> - Varredura (A): dados brutos em `crawl/raw_*.tsv`, agregados em `crawl/out_new.jsonl`. Por decisão do usuário (custo), 172 dos 385 cursos restantes foram varridos em 2 níveis e os demais só no nível 1; o campo 28 (`prof`) marca isso, e nesses cursos a contagem de aulas é um piso ("≥ N aulas") e o volume fica "—". As consultas em lote do conector às vezes perdem itens em pastas com mais de ~60 arquivos, então as contagens são aproximadas.
> - Classificação (B): `cls/out_*.jsonl`. Aulas e volume são calculados pelo script a partir da varredura.
> - Duplicatas (C): 21 grupos (edições de anos diferentes do mesmo curso ficam no mesmo grupo).
> - Trilhas (D): `trilhas.json`, 6 trilhas de 5 a 8 cursos. A de E-commerce termina em Médio porque não há curso avançado atual e sem alerta.
> - Campos novos em `data5.json` (`rows[k]`): 16 ano, 17 base do ano, 18 atualidade, 19 ferramentas, 20 alerta, 21 integridade, 22 aulas, 23 volume, 24 materiais, 25 grupo de duplicata, 26 cópia principal, 27 nº de cópias, 28 profundidade da varredura.

Este pacote tem tudo o que foi feito até 31/10/2026 no claude.ai, para continuar no Claude Code.

## O que já está pronto

- **506 cursos catalogados** (`data4.json`, `Indice-Cursos-Drive.xlsx`). Cada um tem:
  curso, autor, link da pasta, pacote, origem do autor, resumo, tema macro e secundário, tópicos, competências, nível de dificuldade com o motivo, formato e base do perfil.
- **Página publicada** (artifact "Índice de Cursos do Drive", versão 4). O modelo da página é `page_head4.html`, e o marcador `__DATA__` recebe o conteúdo de `data4.json`.

### Formato das linhas em `data4.json` (`rows[k]`)

| Posição | Campo |
|---|---|
| 0 | curso |
| 1 | autor |
| 2 | id da pasta no Drive (link: `https://drive.google.com/drive/folders/<id>`) |
| 3 | pacote |
| 4 | origem do autor (`nome da pasta`, `alta`, `média`, `baixa`, `não encontrado`, `pasta vazia`) |
| 5 | fonte da pesquisa de autor |
| 6 | observação da pesquisa |
| 7 | resumo |
| 8 | tema macro |
| 9 | tema secundário |
| 10 | tópicos (lista) |
| 11 | competências (lista) |
| 12 | nível (`Iniciante`, `Médio`, `Avançado`) |
| 13 | formato |
| 14 | base do perfil (`pasta` ou `só o nome`) |
| 15 | o que precisa saber antes |

## O que falta (itens pedidos: 1, 2, 4, 6, 7, 8)

### Etapa A: varredura em 2 níveis das pastas

- **Instruções:** `crawl/brief.txt`.
- **Feito:** 121 de 506 cursos (lista em `crawl/done_ids.json`, resultados em `crawl/out_*.jsonl`).
- **Falta:** os outros 385. As entradas estão em `crawl/chunk_*.jsonl`; pule os ids que já estão em `done_ids.json`.
- **Atenção:** algumas linhas de `out_0`, `out_4`, `out_7` e `out_8` podem ter ficado pela metade quando a varredura foi parada. Valide cada linha como JSON e refaça as que falharem.

### Etapa B: classificação

- **Instruções:** `cls/brief.txt`. Rode com os dados de `data4.json` mais os da etapa A.
- **Campos que saem daqui:**
  - **1.** ano estimado e atualidade (Atual, Recente, Datado, Atemporal)
  - **2.** ferramentas e plataformas
  - **4.** alerta (black/contingência, adulto, apostas, day trade, dinheiro fácil, sedução, saúde sem respaldo)
  - **6.** volume (aulas, Curto/Médio/Extenso) e materiais de apoio
  - **Extra:** integridade (Completo, Parcial, Só bônus, Vazio)

### Etapa C: duplicatas (item 7)

- Agrupe pelo curso e autor normalizados (há cerca de 18 grupos).
- Em cada grupo, marque a cópia "principal" pela ordem: mais aulas, depois integridade Completo, depois ano mais recente.

### Etapa D: trilhas (item 8)

- Monte sequências por tema, indo de Iniciante a Médio a Avançado, só com cópias principais e sem itens com alerta.
- Prioridade para os temas com mais cursos: Tráfego pago, Afiliados e negócios digitais, Conteúdo e redes sociais, IA e automação, E-commerce e marketplaces, Copywriting.
- Cada trilha deve ter 4 a 8 cursos e uma frase explicando por que cada um vem naquela ordem.

### Etapa E: saída

- **Planilha:** atualize `Indice-Cursos-Drive.xlsx` com as colunas novas.
- **Página** (`page_head4.html`):
  - filtros de atualidade, ferramenta e alerta, com os cursos com alerta escondidos por padrão e um botão "mostrar todos";
  - selo de "cópia principal" nas duplicatas;
  - uma seção "Trilhas".

## Regras definidas pelo Lucas

- Todo material do **Doug Demarco** é nível **Avançado**. O "Drop na Prática 2.0" é do Douglas Souza, não do Doug.
- O nível mede o que o aluno precisa já saber para tirar proveito do curso, não o que a página de vendas promete.
- **Não invente autores.** Se não houver evidência, deixe o campo em branco.

## Acesso ao Drive no Claude Code

O Claude Code na sua máquina não usa o conector do Google Drive do claude.ai. Para as etapas A a E, ele precisa de um destes caminhos:

1. Um servidor MCP do Google Drive configurado no Claude Code.
2. Um script Python com a API do Google Drive (OAuth, escopo `drive.readonly`), escrito pelo próprio Claude Code. A conta logada precisa ter acesso às pastas compartilhadas.

Pastas dos pacotes (pai de cada curso): estão em `packs.json` (id → nome do pacote). Os ids de cada curso estão em `data4.json`.

## Prompt sugerido para abrir no Claude Code

> Leia LEIA-ME-CLAUDE-CODE.md e continue o projeto a partir da Etapa A. Antes de varrer o Drive, me mostre como vai acessar as pastas (MCP ou script com API) e confirme comigo.
