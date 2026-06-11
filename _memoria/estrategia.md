# Estratégia

## Fase

Operação consolidada (20 anos de mercado, +1.000 consultoras). Foco em crescimento qualificado — não só volume, mas conversão melhor e expansão da presença física e digital.

## Prioridade principal

**Matriz:** aumentar a conversão de potenciais consultoras. O maior gatilho de conversão é ver mulheres iguais a elas conquistando resultados reais — cases reais, depoimentos, histórias de transformação.

**Abel Cabral:** expandir a operação da loja (ainda pequena para o potencial da marca) e estruturar presença digital mais robusta, incluindo e-commerce.

## Repositório GitHub

Repositório exclusivo da Magnífica: https://github.com/kingmariano23/magnificajoias-mazyos
Remote configurado localmente. Autenticação (token) pendente para habilitar o push.

## Sistema MazyUI

Painel MazyUI instalado e operacional localmente (sessão mai/2026). Abre com `Abrir MazyUI.command`. Tema da marca aplicado via `local-ui.css` (paleta dourada `#C4912B`, creme `#FAF6F0`). Logo em `identidade/logo.svg`. Assets da marca em `identidade/assets/`.

**Deploy no Vercel (pendente):** o `mazyui-server.mjs` (Node.js) não roda no Vercel Free — frontend estático abre mas as rotas de leitura de arquivo não funcionam. Exige reescrita como API Routes do Vercel pra funcionar completo.

**Direção SaaS explorada (mai/2026):** interesse em transformar o MazyUI numa aplicação cloud — dados no Supabase (substituindo leituras de arquivo local), painel hospedado via URL, auth via Supabase Auth, skills chamando a API do Claude no backend. Cada cliente teria seu próprio espaço no banco. Ainda é ideia exploratória, sem prazo ou decisão.

## Infraestrutura de scraping (jun/2026)

Playwright + Chromium instalados. Sessão do Instagram salva em `dados/ig_session.json` (usuário: lucasmarianofc).
- Re-scraper: `python3 scripts/scraper_instagram.py`
- Sessão expira periodicamente — renovar com: `python3 scripts/scraper_instagram.py --login`
- Outputs em `dados/referencias/` — CSVs + relatório de referências do nicho
- Instaloader instalado mas não funciona sem sessão ativa (API bloqueada pelo Instagram desde 2024)

## O que pode esperar

- E-commerce — identificado como oportunidade, ainda não implementado
- Campanha de indicação estruturada (Matriz e Abel)
- Agente de IA para atendimento no WhatsApp
- Agente de voz para atendimento em ligações fora do horário

## Contexto com prazo

A Magnífica está em seu 20º aniversário — momento com força comunicacional relevante para campanhas de reconhecimento, prova de autoridade e celebração da comunidade.

## O que mais é pedido ao sistema

Legendas para posts e reels, roteiros de vídeo, copy de anúncios (tráfego pago Google e Meta) — para as duas submarcas. Separar sempre claramente se o conteúdo é para Matriz ou Abel Cabral, pois as regras de formatação e tom são distintas.

## Campanhas Meta Ads ativas (jun/2026)

Duas campanhas rodando em paralelo:

**Força de Mulher, Amor de Mãe [Recon]** — objetivo: alcance/awareness
Conjuntos: Noivas/Força da Mulher, Mulher, Dia dos Namorados, Junino, Copa.

**Seja uma Consultora [Engajamento] [CBO]** — objetivo: conversas via WhatsApp (recrutamento de consultoras)
Conjuntos: Novo conjunto de Engajamento, Copa, Depoimentos, Dia dos Namorados, Junino.

**Benchmark período 06/05–09/06/2026:**
R$ 1.225,55 investidos → 305.994 pessoas alcançadas, 581.402 impressões, 2.192 cliques, CPC R$ 0,56, CPM R$ 1,01–1,16. 382 conversas iniciadas via WhatsApp. Junino = melhor eficiência de custo (R$ 1,02 CPM). Dia dos Namorados = maior CTR e menor CPC na campanha de awareness.
