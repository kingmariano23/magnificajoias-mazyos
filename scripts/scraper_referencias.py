#!/usr/bin/env python3
"""
Scraper de referências para Magnífica Joias
Extrai posts de alto desempenho do nicho de semijoias no Instagram
Campo semântico base: autonomia, delicadeza, jornada, essência, pertencimento...
"""

import instaloader
import json
import csv
import os
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

# Diretório de saída
BASE_DIR = Path(__file__).parent.parent / "dados" / "referencias"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Perfis relevantes do nicho (semijoias BR + venda direta + empoderamento feminino)
# Foco: marcas aspiracionais, concorrentes indiretos, criadores de conteúdo do nicho
PERFIS_ALVO = [
    "rommanel",           # maior marca de semijoias do Brasil — benchmark
    "vivara.oficial",     # joia fina — referência de posicionamento aspiracional
    "skgoldoficial",      # semijoias atacado — concorrente direto
    "semijoiasitalia",    # nicho similar
    "jemimajoias",        # nicho similar com venda direta
    "joiasmenina",        # semi-joias com forte presença digital
    "amourette.joias",    # semijoias com estética editorial
    "rommanel_consultoras", # conteúdo de consultoras (espelho da Matriz)
]

# Hashtags para descoberta de conteúdo orgânico de alto engajamento
HASHTAGS_ALVO = [
    "semijoias",
    "semijoia",
    "joiasbrasileiras",
    "consultoradejoias",
    "semijoiasatacado",
    "joiasfemininas",
    "acessoriosfemininos",
    "empreendedorismofeminino",
    "rendaextrademulher",
    "maleta",             # linguagem interna do mercado de venda direta
]

MAX_POSTS_POR_PERFIL = 12   # últimos 12 posts por perfil
MAX_POSTS_POR_HASHTAG = 30  # top 30 por hashtag
MIN_LIKES_HASHTAG = 100     # filtro de engajamento mínimo


def create_loader(username=None):
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
        request_timeout=30,
    )

    # Tenta carregar sessão salva automaticamente
    if username:
        try:
            L.load_session_from_file(username)
            print(f"[✓] Sessão carregada para @{username}")
            return L
        except FileNotFoundError:
            print(f"[!] Sessão não encontrada para @{username}")
            print(f"    Execute no terminal: instaloader --login {username}")
            print(f"    Depois rode este script novamente.\n")
        except Exception as e:
            print(f"[!] Erro ao carregar sessão: {e}")

    # Tenta encontrar qualquer sessão salva em ~/.config/instaloader/
    session_dir = Path.home() / ".config" / "instaloader"
    if session_dir.exists():
        sessions = list(session_dir.glob("session-*"))
        if sessions:
            session_file = sessions[0]
            saved_user = session_file.name.replace("session-", "")
            try:
                L.load_session_from_file(saved_user)
                print(f"[✓] Sessão carregada automaticamente: @{saved_user}")
                return L
            except Exception:
                pass

    print("[!] Nenhuma sessão encontrada. Rodando sem autenticação (dados limitados).")
    return L


def extract_post_data(post):
    return {
        "shortcode": post.shortcode,
        "url": f"https://www.instagram.com/p/{post.shortcode}/",
        "tipo": "video" if post.is_video else "imagem" if not post.typename == "GraphSidecar" else "carrossel",
        "data": post.date_utc.strftime("%Y-%m-%d"),
        "likes": post.likes,
        "comentarios": post.comments,
        "engajamento": post.likes + post.comments,
        "perfil": post.owner_username,
        "seguidores_perfil": post.owner_profile.followers if post.owner_profile else 0,
        "legenda": (post.caption or "")[:500].replace("\n", " "),
        "hashtags": list(post.caption_hashtags) if post.caption else [],
        "mencoes": list(post.caption_mentions) if post.caption else [],
        "acessibilidade": post.accessibility_caption or "",
        "localizacao": str(post.location) if post.location else "",
    }


def scrape_profile(L, username, max_posts=MAX_POSTS_POR_PERFIL):
    posts = []
    print(f"\n→ Perfil: @{username}")
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        print(f"  {profile.followers:,} seguidores | {profile.mediacount} posts")
        count = 0
        for post in profile.get_posts():
            if count >= max_posts:
                break
            try:
                posts.append(extract_post_data(post))
                count += 1
                time.sleep(1.5)  # respeito ao rate limit
            except Exception as e:
                print(f"  [!] Erro no post: {e}")
                continue
        print(f"  [✓] {len(posts)} posts extraídos")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"  [!] Perfil @{username} não encontrado ou privado")
    except instaloader.exceptions.LoginRequiredException:
        print(f"  [!] @{username} requer login — tente com autenticação")
    except Exception as e:
        print(f"  [!] Erro: {e}")
    return posts


def scrape_hashtag(L, tag, max_posts=MAX_POSTS_POR_HASHTAG, min_likes=MIN_LIKES_HASHTAG):
    posts = []
    print(f"\n→ Hashtag: #{tag}")
    try:
        hashtag = instaloader.Hashtag.from_name(L.context, tag)
        count = 0
        for post in hashtag.get_posts():
            if count >= max_posts * 3:  # itera mais, filtra por engajamento
                break
            try:
                if post.likes >= min_likes:
                    data = extract_post_data(post)
                    posts.append(data)
                    count += 1
                    if count >= max_posts:
                        break
                time.sleep(1.5)
            except Exception as e:
                print(f"  [!] Erro: {e}")
                continue
        posts.sort(key=lambda x: x["engajamento"], reverse=True)
        print(f"  [✓] {len(posts)} posts com >{min_likes} likes extraídos")
    except instaloader.exceptions.LoginRequiredException:
        print(f"  [!] #{tag} requer login para ver posts recentes")
    except Exception as e:
        print(f"  [!] Erro: {e}")
    return posts


def salvar_csv(dados, nome_arquivo):
    path = BASE_DIR / nome_arquivo
    if not dados:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)
    print(f"  [→] Salvo: {path}")


def gerar_relatorio(todos_posts):
    path = BASE_DIR / "relatorio_referencias.md"
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Top posts por engajamento
    top = sorted(todos_posts, key=lambda x: x["engajamento"], reverse=True)[:30]

    # Análise de tipos
    tipos = {}
    for p in todos_posts:
        tipos[p["tipo"]] = tipos.get(p["tipo"], 0) + 1

    # Top hashtags encontrados nos posts
    all_tags = []
    for p in todos_posts:
        all_tags.extend(p["hashtags"])
    tag_freq = {}
    for t in all_tags:
        tag_freq[t.lower()] = tag_freq.get(t.lower(), 0) + 1
    top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:25]

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Referências de Conteúdo — Magnífica Joias\n")
        f.write(f"Extraído em: {agora}\n\n")
        f.write(f"Total de posts analisados: {len(todos_posts)}\n\n")
        f.write(f"## Tipos de conteúdo encontrados\n\n")
        for tipo, qtd in tipos.items():
            f.write(f"- **{tipo}:** {qtd} posts\n")

        f.write(f"\n## Top 25 hashtags do nicho\n\n")
        f.write("Use estas hashtags como referência de distribuição nos seus posts.\n\n")
        for tag, freq in top_tags:
            f.write(f"- `#{tag}` ({freq}x)\n")

        f.write(f"\n## Top 30 posts por engajamento\n\n")
        for i, p in enumerate(top, 1):
            f.write(f"### {i}. @{p['perfil']} — {p['tipo']} | {p['likes']:,} likes | {p['comentarios']:,} comentários\n")
            f.write(f"- **Link:** {p['url']}\n")
            f.write(f"- **Data:** {p['data']}\n")
            f.write(f"- **Legenda:** {p['legenda'][:200]}...\n\n")

    print(f"\n[✓] Relatório salvo: {path}")
    return path


def main():
    print("=" * 60)
    print("SCRAPER DE REFERÊNCIAS — MAGNÍFICA JOIAS")
    print("=" * 60)
    print("\nCampo semântico: autonomia · delicadeza · jornada · essência")
    print("Nicho: semijoias BR + venda direta + empoderamento feminino\n")

    # Usa username passado como argumento: python3 scraper_referencias.py meuusuario
    username = sys.argv[1] if len(sys.argv) > 1 else None

    L = create_loader(username=username)

    todos_posts = []

    # Scrape de perfis
    print("\n## PERFIS DO NICHO ##")
    posts_perfis = []
    for perfil in PERFIS_ALVO:
        posts = scrape_profile(L, perfil)
        posts_perfis.extend(posts)
        todos_posts.extend(posts)
        time.sleep(3)  # pausa entre perfis

    if posts_perfis:
        salvar_csv(posts_perfis, "posts_perfis.csv")

    # Scrape de hashtags
    print("\n## HASHTAGS DO NICHO ##")
    posts_tags = []
    for tag in HASHTAGS_ALVO[:5]:  # limitado sem login — primeiras 5
        posts = scrape_hashtag(L, tag)
        posts_tags.extend(posts)
        todos_posts.extend(posts)
        time.sleep(4)  # pausa maior entre hashtags

    if posts_tags:
        salvar_csv(posts_tags, "posts_hashtags.csv")

    # Relatório final
    if todos_posts:
        relatorio = gerar_relatorio(todos_posts)
        print(f"\n{'='*60}")
        print(f"CONCLUÍDO — {len(todos_posts)} posts analisados")
        print(f"Relatório: {relatorio}")
        print(f"{'='*60}")
    else:
        print("\n[!] Nenhum post extraído. Instagram pode estar bloqueando.")
        print("Tente rodar com: python3 scripts/scraper_referencias.py --login")
        print("(com login a extração é significativamente mais robusta)")


if __name__ == "__main__":
    main()
