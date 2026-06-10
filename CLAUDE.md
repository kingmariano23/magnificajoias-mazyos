# MazyUI — Sistema operacional do negócio

Sua empresa roda em cima desse arquivo. Aqui ficam as regras de operação
do MazyUI — como o Claude lê o contexto, aprende com correções, mantém
tudo atualizado e cria skills novas conforme a operação evolui.

Esse arquivo é editável. Quando o `/instalar` rodar, ele complementa o
final dessa página com as regras específicas do seu negócio.

---

## ⚠️ Regra inviolável — extensões de cliente vão em `local-*`

Quando o usuário pedir uma feature nova que envolve **UI** ou **endpoint
de servidor** (ex: "sincroniza a UI com o CSV", "adiciona painel de
agenda", "cria um endpoint pra exportar dados"), o código novo vai
**SEMPRE** em:

- **Servidor:** `local-routes.mjs` (via `register({ helpers, addRoute })`)
- **UI:** `local-ui.js` (via `window.Sabec.registerPanel(def)`)

**NUNCA edite `mazyui-server.mjs`, `mazyui-ui.html` ou arquivos dentro de
`mazyui-ui/` direto pra adicionar feature de cliente.** Esses arquivos são
reescritos pelo `/atualizar-sistema` — qualquer feature colada neles vira
lixo no próximo update. Esse erro já aconteceu (e já fez cliente perder código).

Antes de mexer em qualquer arquivo de UI/servidor, faça o teste mental:

> "Isso é feature universal pro MazyUI (vai pro repo central) ou é
>  específico desse cliente (vai pra `local-*`)?"

Se é específico do cliente → `local-*`. Se é universal → contribua pro
repo central em `github.com/DiogoSabec/sabec-os` em vez de hackear no
cliente.

Detalhes completos da API dos hooks `local-*` estão na seção
"Extensões locais por cliente" mais abaixo.

---

## Contexto do negócio

No início de toda conversa, ler os seguintes arquivos (quando existirem
e estiverem preenchidos):

1. `_memoria/empresa.md` — quem é o usuário, o que faz, como funciona o negócio
2. `_memoria/preferencias.md` — tom de voz, estilo de escrita, o que evitar
3. `_memoria/estrategia.md` — foco atual, prioridades, prazos

Usar essas informações como base pra qualquer resposta ou decisão. Ao
sugerir prioridades, formatos ou abordagens, considerar o foco atual
descrito em `estrategia.md`.

Pra qualquer tarefa visual (carrossel, post, landing page), consultar
`identidade/design-guide.md` como referência de estilo.

Não é necessário listar o que foi lido nem confirmar a leitura. Apenas
usar o contexto naturalmente.

---

## Fluxo de trabalho

Antes de executar qualquer tarefa, verificar se existe skill relevante
em `.claude/skills/`. Se encontrar, seguir as instruções da skill. Se
não encontrar, executar a tarefa normalmente.

Ao concluir uma tarefa que não tinha skill mas parece repetível (o
usuário provavelmente vai pedir de novo no futuro), perguntar:

> "Isso pode virar uma skill pra próxima vez. Quer que eu crie?"

Não perguntar pra tarefas pontuais ou perguntas simples. Só quando o
padrão de repetição for claro.

---

## Aprender com correções

Quando o usuário corrigir algo, melhorar uma resposta ou dar uma
instrução que parece permanente (frases como "na verdade é assim", "não
faça mais isso", "prefiro assim", "sempre que...", "evita...", "da
próxima vez..."), perguntar:

> "Quer que eu salve isso pra não precisar repetir?"

Se sim, identificar onde faz mais sentido salvar:

- **Sobre o negócio** (clientes, serviços, mercado) → `_memoria/empresa.md`
- **Sobre preferências e estilo** (tom de voz, formato, o que evitar) → `_memoria/preferencias.md`
- **Sobre prioridades e foco** (projetos, metas, prazos) → `_memoria/estrategia.md`
- **Regra de comportamento nessa pasta** → próprio `CLAUDE.md`

Salvar com uma linha nova clara, sem reformatar o arquivo inteiro.
Confirmar mostrando a linha adicionada.

Não perguntar se a correção for óbvia de contexto imediato (ex: "na
verdade o arquivo se chama X"). Só perguntar quando a informação tiver
valor duradouro.

---

## Manter contexto atualizado

Ao terminar uma tarefa que mudou algo relevante (cliente novo, skill
nova, mudança de foco, processo novo, ferramenta instalada, estrutura
alterada), perguntar:

> "Isso mudou algo no teu contexto. Quer que eu atualize a memória?"

Se sim, identificar o que atualizar:

- **Cliente, serviço, ferramenta, equipe** → `_memoria/empresa.md`
- **Mudança de prioridade ou foco** → `_memoria/estrategia.md`
- **Tom ou estilo** → `_memoria/preferencias.md`
- **Pasta, regra de organização, skill criada** → `CLAUDE.md`
- **Visual (cores, fontes, logo)** → `identidade/design-guide.md`

Mostrar o que vai mudar antes de salvar. Não reformatar o arquivo
inteiro, só adicionar ou editar a linha relevante.

**Quando NÃO perguntar:**
- Tarefas pontuais sem impacto no contexto (escrever um email avulso, criar um post)
- Perguntas simples ou conversas sem ação
- Mudanças já salvas pelo bloco "Aprender com correções"

**Dica:** rode `/atualizar` pra uma varredura completa quando houver dúvida.

---

## Criação de skills

Quando o usuário pedir skill nova:

1. Verificar se existe template relevante em `templates/skills/`. Se
   existir, usar como base e adaptar pro contexto
2. Perguntar se é específica desse projeto ou útil em qualquer:
   - Específica → `.claude/skills/nome-da-skill/SKILL.md` (local)
   - Universal → `~/.claude/skills/nome-da-skill/SKILL.md` (global)
3. Ler `_memoria/empresa.md` e `_memoria/preferencias.md` pra calibrar
   o conteúdo da skill ao contexto do negócio
4. Se a skill precisar de arquivos de apoio (templates, exemplos),
   criar dentro da pasta da skill
5. Seguir o fluxo da skill-creator nativa do Claude Code

---

## Atualização do sistema (clientes)

Cada cliente do MazyUI é um clone com brand, dados e memória próprios.
O sistema central evolui em `github.com/DiogoSabec/sabec-os`. Pra puxar
melhorias do sistema central pra dentro de um cliente sem sobrescrever o
que é dele, o cliente roda `/atualizar-sistema`.

A skill `atualizar-sistema` puxa apenas arquivos da whitelist (server,
UI, launchers, skills, templates, partes genéricas de `package.json` e
`CLAUDE.md`) e nunca toca em `brand.config.js`, `_memoria/`,
`identidade/`, `REFERENCIAS/`, `marketing/`, `saidas/`, `dados/`,
`pacientes/`, `clientes/`.

**Convenção do `CLAUDE.md`:** esse arquivo termina com `---` (três
hífens em linha isolada) como marcador de fim do bloco genérico do
sistema. O cliente acrescenta customizações abaixo desse separador.
`/atualizar-sistema` preserva tudo o que estiver depois do último `---`.

---

## Extensões locais por cliente

Cada cliente precisa de coisas próprias: caixa pra clínica, prontuários
pra dentista, agenda pra terapeuta. O contrato é simples:

- **Código de sistema** (`mazyui-server.mjs`, `mazyui-ui.html`, arquivos em
  `mazyui-ui/`) → evolui no repo central, sobrescrito a cada `/atualizar-sistema`.
- **Código do cliente** (`local-routes.mjs`, `local-ui.js`) →
  intocável pelo sync. É onde feature custom mora.

Editar `mazyui-server.mjs` ou `mazyui-ui.html` direto pra adicionar uma
feature do cliente **vira lixo no próximo sync** — é assim que clientes
perdem código. Use os hooks abaixo.

### Servidor: `local-routes.mjs`

Arquivo opcional na raiz do cliente. Se existe, o servidor carrega
antes de escutar e chama `register({ ROOT, helpers, addRoute })`:

```js
// local-routes.mjs
export function register({ ROOT, helpers, addRoute }) {
  addRoute('GET', '/api/caixa', (req, res) => {
    const data = helpers.readSafe('dados/caixa.csv');
    helpers.json(res, 200, { csv: data });
  });
}
```

Helpers disponíveis: `json(res, status, payload)`, `text(res, status,
body, ct?)`, `readBody(req)`, `safeResolve(rel)`, `readSafe(rel)`.

### UI: `local-ui.js`

Arquivo opcional na raiz do cliente. Carregado depois do boot, registra
painéis via `window.Sabec.registerPanel(def)`:

```js
// local-ui.js
window.Sabec.registerPanel({
  id:      'caixa',
  label:   'Caixa',
  crumb:   'Caixa',
  glyph:   'C',
  sidebar: true,
  onMount: async (container, ctx) => {
    const data = await ctx.api.call('GET', '/api/caixa');
    container.innerHTML = `<div class="card"><pre>${data.csv}</pre></div>`;
  },
});
```

### Tema: `local-ui.css`

Arquivo opcional na raiz. Carregado após o CSS do sistema — use pra
sobrescrever paleta/tipografia sem hackear o CSS core:

```css
/* local-ui.css */
:root {
  --ink:   #0A0A0A;
  --paper: #EDE9DF;
}
```

### O que NUNCA fazer

- Editar `mazyui-server.mjs`, `mazyui-ui.html` ou arquivos em `mazyui-ui/`
  pra adicionar feature de cliente — `/atualizar-sistema` vai sobrescrever.
- Persistir dados do cliente fora de `dados/`, `_memoria/` ou pastas custom.

---

## Painéis v2 (opcional, novo)

Além do `window.Sabec.registerPanel()` v1 (preservado), existe o
`window.Sabec.v2.registerPanel()` com lit-html e re-render reativo automático.

Use v2 pra painéis novos quando puder — basta adicionar `v2: true` na def e
declarar uma função `view(ctx)` que retorna um template lit-html. O registry
gerencia o `subscribe`/re-render automaticamente.

Painéis v1 (`local-ui.js` etc.) continuam funcionando exatamente como antes
— não há necessidade de migrar.

Detalhes completos, exemplos e checklist de portagem em `mazyui-ui/README.md`.

---

## O que é este repositório

Este é o workspace da **Magnífica Joias** — empresa brasileira de semijoias
fundada em 2006, com dois braços de operação: a **Matriz** (atacado B2B,
venda direta com rede de +1.000 consultoras) e a **Abel Cabral** (loja
física B2C em Nova Parnamirim/RN). O sistema foi configurado para produzir
legendas, roteiros de vídeo e copy de anúncios para as duas submarcas —
com regras de tom e formatação distintas para cada uma.

O MazyUI é a estrutura de memória, identidade, skills e painel visual que
faz o Claude operar como parte da empresa. O `/instalar` já foi executado
— o sistema está configurado.

---

## Arquitetura

```
_memoria/          → cérebro do sistema (contexto permanente)
  empresa.md       → quem é a empresa, o que faz, equipe, clientes
  preferencias.md  → tom de voz, o que evitar, estilo de escrita
  estrategia.md    → foco atual, gargalos, prioridades

identidade/
  design-guide.md  → cores, tipografia, logo, estilo visual
                     (lido por toda skill que gera conteúdo visual)

.claude/skills/    → skills locais do projeto
templates/
  perfis/          → 4 templates de CLAUDE.md por tipo de negócio
  skills/          → catálogo de skills externas prontas pra instalar
  identidade/      → exemplos de design-guide preenchido
  ferramentas/     → catálogo de APIs, CLIs e MCPs disponíveis

dados/             → inputs do usuário (CSVs, exports, arquivos de análise)
marketing/         → rascunhos e materiais de marketing em produção
saidas/            → outputs gerados pelo sistema (carrosséis, artigos, etc.)
scripts/           → scripts de automação usados pelas skills

mazyui-ui/         → frontend modular do painel (não editar diretamente)
mazyui-ui.html     → entry point do painel (não editar diretamente)
mazyui-server.mjs  → servidor local do painel (não editar diretamente)
brand.config.js    → marca da instância (este cliente)
local-routes.mjs   → rotas customizadas do cliente (opcional)
local-ui.js        → painéis customizados do cliente (opcional)
local-ui.css       → overrides de tema/paleta (opcional)
```

---

## Skills disponíveis

Skills ficam em `.claude/skills/<nome>/SKILL.md`. Antes de executar qualquer tarefa, verificar se existe skill relevante nessa pasta. Se encontrar, seguir as instruções da skill.

| Skill | O que faz |
|---|---|
| `/instalar` | Setup inicial — entrevista, preenche `_memoria/`, adapta `CLAUDE.md` |
| `/abrir` | Carrega contexto no início de cada sessão |
| `/salvar` | Commit + push no GitHub |
| `/atualizar` | Varre o projeto e atualiza a memória |
| `/atualizar-sistema` | Puxa melhorias do sistema central sem tocar nos dados do cliente |
| `/novo-projeto` | Cria pasta isolada pra cliente ou iniciativa |
| `/mapear-rotinas` | Detecta repetições e transforma em skill |
| `/carrossel` | Carrosséis 1080×1350 com identidade da marca |
| `/publicar-tema` | Tema → artigo de blog + carrossel + 3 legendas |
| `/seo` | Fluxo completo de SEO em 8 passos |
| `/responder-avaliacoes` | Respostas humanizadas para reviews do Google |
| `/aprovar-post` | Publica blog + Instagram + Facebook |
| `/anuncio-google` | Campanha Google Ads em CSV pra importar |
| `/relatorio-ads` | Relatório semanal a partir de exports Google + Meta |
| `/analisar-dados` | Resume CSV/XLSX/PDF em relatório executivo |
| `/email-profissional` | Rascunha email a partir de contexto livre |

Skills globais adicionais (catálogo em `templates/skills/catalogo.md`): `/schwartz-copy`, `/yt-transcript`, e skills nativas do Claude Code como `/frontend-design`, `/canvas-design`, `/pdf`, `/docx`, `/pptx`, `/xlsx`.

---

## Ferramentas e integrações

Catálogo completo em `templates/ferramentas/catalogo.md`. Principais:

- **Painel visual:** `Abrir MazyUI.command` (Mac) ou `Abrir MazyUI.bat` (Windows) — inicia o servidor local e abre o painel no browser
- **Visuais:** Playwright CLI (`npx playwright install chromium`) — renderiza HTML em PNG nos tamanhos de carrossel
- **Publicação:** Cloudflare Pages API (requer `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID` no `.env`)
- **Redes sociais:** Post for Me API (requer `POSTFORME_API_KEY` no `.env`)
- **Imagens IA:** Gemini (`GEMINI_API_KEY`) ou DALL-E (`OPENAI_API_KEY`)
- **MCPs:** Notion, Gmail, Google Calendar, Canva, N8N, Supabase, Telegram — instalar com `claude mcp add`
