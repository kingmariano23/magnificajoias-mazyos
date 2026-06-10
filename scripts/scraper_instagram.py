#!/usr/bin/env python3
"""
Scraper Instagram — Magnífica Joias
Usa Playwright (browser real) para extrair referências do nicho de semijoias.

Uso:
  python3 scripts/scraper_instagram.py --login    # Abre browser, faz login, salva sessão
  python3 scripts/scraper_instagram.py            # Usa sessão salva, extrai dados
"""

import sys
import json
import csv
import time
import random
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE_DIR = Path(__file__).parent.parent / "dados" / "referencias"
BASE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = Path(__file__).parent.parent / "dados" / "ig_session.json"

# Perfis do nicho de semijoias BR — verificados via busca manual
PERFIS_ALVO = [
    "rommanel",
    "vivara",
    "prata.fina",
    "skygoldjoias",
    "franciscajoias",
    "joiasmenina",
    "amourette.joias",
    "semijoia.store",
    "semijoias.br",
    "crisjoias",
]

# Hashtags do campo semântico da Magnífica
HASHTAGS_ALVO = [
    "semijoias",
    "semijoia",
    "joiasbrasileiras",
    "consultoradejoias",
    "semijoiasatacado",
    "empreendedorismofeminino",
    "rendaextra",
    "joiasfemininas",
    "maleta",
    "acessoriosfemininos",
]

MAX_POSTS_PERFIL = 9
MAX_POSTS_HASHTAG = 15


def humano(pagina, min_ms=800, max_ms=2200):
    """Pausa aleatória para simular comportamento humano."""
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


def salvar_sessao(context, caminho=SESSION_FILE):
    storage = context.storage_state()
    with open(caminho, "w") as f:
        json.dump(storage, f)
    print(f"[✓] Sessão salva: {caminho}")


def carregar_sessao(playwright, headless=True):
    browser = playwright.chromium.launch(headless=headless)
    if SESSION_FILE.exists():
        context = browser.new_context(
            storage_state=str(SESSION_FILE),
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        print(f"[✓] Sessão carregada de {SESSION_FILE}")
    else:
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
    return browser, context


def login_manual(playwright):
    """Abre browser visível para o usuário fazer login uma vez."""
    print("\n[→] Abrindo browser para login no Instagram...")
    print("    Faça login normalmente. Quando terminar, pressione ENTER aqui.\n")
    browser = playwright.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    )
    page = context.new_page()
    page.goto("https://www.instagram.com/accounts/login/")
    input("    [AGUARDANDO] Faça login no browser e pressione ENTER quando terminar...")
    salvar_sessao(context)
    browser.close()
    print("[✓] Login concluído. Rode o script sem --login para extrair dados.")


def verificar_login(page):
    """Verifica se a sessão ainda está ativa."""
    page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
    humano(page, 2000, 3500)
    # Se aparecer o feed ou ícone de perfil, está logado
    return page.url != "https://www.instagram.com/accounts/login/"


def extrair_posts_perfil(page, username, max_posts=MAX_POSTS_PERFIL):
    posts = []
    url = f"https://www.instagram.com/{username}/"
    print(f"\n  → @{username}")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        humano(page, 2000, 3500)

        # Verifica se perfil existe
        if "Page Not Found" in page.title() or "Sorry" in page.title():
            print(f"    [!] Perfil não encontrado")
            return posts

        # Captura seguidores
        seguidores = ""
        try:
            meta = page.query_selector('meta[name="description"]')
            if meta:
                content = meta.get_attribute("content") or ""
                seguidores = content.split(" Followers")[0].split(" - ")[-1].strip() if "Followers" in content else ""
        except Exception:
            pass

        # Coleta links dos posts
        links_posts = []
        try:
            anchors = page.query_selector_all('a[href*="/p/"]')
            for a in anchors:
                href = a.get_attribute("href")
                if href and "/p/" in href:
                    link = f"https://www.instagram.com{href}" if href.startswith("/") else href
                    if link not in links_posts:
                        links_posts.append(link)
                if len(links_posts) >= max_posts:
                    break
        except Exception:
            pass

        print(f"    {len(links_posts)} posts encontrados | {seguidores} seguidores")

        # Visita cada post para extrair dados
        for link in links_posts[:max_posts]:
            post_data = extrair_dados_post(page, link, username)
            if post_data:
                posts.append(post_data)
            humano(page, 1500, 3000)

    except PlaywrightTimeout:
        print(f"    [!] Timeout ao carregar @{username}")
    except Exception as e:
        print(f"    [!] Erro: {str(e)[:80]}")

    return posts


def extrair_dados_post(page, url, username=""):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        humano(page, 1200, 2500)

        def get_meta(prop):
            try:
                el = page.query_selector(f'meta[property="{prop}"]') or page.query_selector(f'meta[name="{prop}"]')
                return (el.get_attribute("content") or "").strip() if el else ""
            except Exception:
                return ""

        # Username via og:url → https://www.instagram.com/{user}/p/{code}/
        og_url = get_meta("og:url")
        if not username and og_url:
            partes = og_url.rstrip("/").split("/")
            # partes: ['https:', '', 'www.instagram.com', '{user}', 'p', '{code}']
            if len(partes) >= 5 and partes[-2] == "p":
                username = partes[-3]

        # Legenda via og:description — formato: "N likes, M comments - Legenda aqui"
        og_desc = get_meta("og:description")
        legenda = ""
        likes = 0
        if og_desc:
            # Extrai likes da descrição
            import re
            m_likes = re.search(r"([\d,\.]+)\s+likes?", og_desc, re.IGNORECASE)
            if m_likes:
                num = m_likes.group(1).replace(",", "").replace(".", "")
                likes = int(num) if num.isdigit() else 0
            # Texto após o " - " é a legenda
            if " - " in og_desc:
                legenda = og_desc.split(" - ", 1)[-1].strip()[:600]

        # Tipo via og:type + detecção de carrossel
        og_type = get_meta("og:type")
        tipo = "video" if "video" in og_type else "imagem"
        try:
            if page.query_selector('[aria-label="Next"]') or page.query_selector('[aria-label="Próximo"]'):
                tipo = "carrossel"
        except Exception:
            pass

        shortcode = url.rstrip("/").split("/p/")[-1].split("/")[0] if "/p/" in url else ""
        hashtags = [w.lstrip("#") for w in legenda.split() if w.startswith("#")]

        return {
            "shortcode": shortcode,
            "url": url,
            "perfil": username,
            "tipo": tipo,
            "likes": likes,
            "legenda": legenda.replace("\n", " ")[:500],
            "hashtags": ", ".join(hashtags[:20]),
            "data_extracao": datetime.now().strftime("%Y-%m-%d"),
        }
    except Exception as e:
        print(f"      [!] Erro no post {url}: {str(e)[:60]}")
        return None


def extrair_posts_hashtag(page, tag, max_posts=MAX_POSTS_HASHTAG):
    posts = []
    url = f"https://www.instagram.com/explore/tags/{tag}/"
    print(f"\n  → #{tag}")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        humano(page, 2500, 4000)

        # Coleta links de posts
        links_posts = []
        anchors = page.query_selector_all('a[href*="/p/"]')
        for a in anchors:
            href = a.get_attribute("href")
            if href and "/p/" in href:
                link = f"https://www.instagram.com{href}" if href.startswith("/") else href
                if link not in links_posts:
                    links_posts.append(link)
            if len(links_posts) >= max_posts:
                break

        print(f"    {len(links_posts)} posts encontrados")

        for link in links_posts[:max_posts]:
            # Extrai username do link via page visit
            post_data = extrair_dados_post(page, link)
            if post_data:
                # Tenta pegar username do URL da página após redirect
                try:
                    perfil_match = page.url.split("instagram.com/")[-1].split("/")[0]
                    if perfil_match not in ("p", "explore", "accounts", ""):
                        post_data["perfil"] = perfil_match
                except Exception:
                    pass
                post_data["fonte"] = f"#{tag}"
                posts.append(post_data)
            humano(page, 1500, 3000)

    except PlaywrightTimeout:
        print(f"    [!] Timeout em #{tag}")
    except Exception as e:
        print(f"    [!] Erro: {str(e)[:80]}")

    return posts


def salvar_csv(dados, nome):
    if not dados:
        return
    path = BASE_DIR / nome
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)
    print(f"  [→] {path.name} — {len(dados)} registros")


def gerar_relatorio(posts_perfis, posts_hashtags):
    todos = posts_perfis + posts_hashtags
    path = BASE_DIR / "relatorio_referencias.md"
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Top hashtags encontrados
    tag_freq = {}
    for p in todos:
        for t in (p.get("hashtags") or "").split(", "):
            t = t.strip().lower()
            if t:
                tag_freq[t] = tag_freq.get(t, 0) + 1
    top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:30]

    # Posts com mais engajamento (por likes)
    com_likes = [p for p in todos if p.get("likes", 0) > 0]
    top_posts = sorted(com_likes, key=lambda x: x["likes"], reverse=True)[:20]

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Referências de Conteúdo — Magnífica Joias\n")
        f.write(f"Extraído em: {agora} | Total: {len(todos)} posts\n\n")

        f.write("## Top 30 hashtags do nicho\n\n")
        f.write("Use como referência para distribuição nos posts:\n\n")
        for tag, freq in top_tags:
            f.write(f"- `#{tag}` ({freq}x)\n")

        f.write("\n## Posts de maior engajamento\n\n")
        for i, p in enumerate(top_posts, 1):
            f.write(f"### {i}. @{p.get('perfil','?')} — {p.get('tipo','?')} | {p.get('likes',0):,} likes\n")
            f.write(f"- Link: {p['url']}\n")
            legenda = p.get("legenda", "")[:200]
            if legenda:
                f.write(f"- Legenda: {legenda}...\n")
            f.write("\n")

        f.write("## Todos os posts extraídos\n\n")
        for p in todos:
            f.write(f"- [@{p.get('perfil','?')}]({p['url']}) — {p.get('tipo','?')} | {p.get('likes',0)} likes\n")

    print(f"\n[✓] Relatório: {path}")
    return path


def main():
    modo_login = "--login" in sys.argv

    with sync_playwright() as playwright:
        if modo_login:
            login_manual(playwright)
            return

        if not SESSION_FILE.exists():
            print("[!] Sessão não encontrada.")
            print("    Execute primeiro: python3 scripts/scraper_instagram.py --login")
            return

        print("=" * 60)
        print("SCRAPER INSTAGRAM — MAGNÍFICA JOIAS (Playwright)")
        print("=" * 60)

        browser, context = carregar_sessao(playwright, headless=True)
        page = context.new_page()

        # Verifica login
        print("\nVerificando sessão...")
        if not verificar_login(page):
            print("[!] Sessão expirada. Rode com --login para renovar.")
            browser.close()
            return
        print("[✓] Sessão ativa\n")

        # Scrape de perfis
        print("## PERFIS DO NICHO ##")
        posts_perfis = []
        for username in PERFIS_ALVO:
            posts = extrair_posts_perfil(page, username)
            posts_perfis.extend(posts)
            humano(page, 3000, 6000)

        salvar_csv(posts_perfis, "posts_perfis.csv")

        # Scrape de hashtags
        print("\n## HASHTAGS DO NICHO ##")
        posts_hashtags = []
        for tag in HASHTAGS_ALVO[:6]:
            posts = extrair_posts_hashtag(page, tag)
            posts_hashtags.extend(posts)
            humano(page, 4000, 7000)

        salvar_csv(posts_hashtags, "posts_hashtags.csv")

        browser.close()

        # Relatório
        relatorio = gerar_relatorio(posts_perfis, posts_hashtags)

        total = len(posts_perfis) + len(posts_hashtags)
        print(f"\n{'='*60}")
        print(f"CONCLUÍDO — {total} posts extraídos")
        print(f"Saídas: dados/referencias/")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
