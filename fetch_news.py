import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import datetime

# ----------------------------------------------------------------------
# Para adicionar/editar categorias, mude a lista abaixo.
# "query" = termos de busca separados por vírgula (combinados com "OU")
# ----------------------------------------------------------------------
CATEGORIES = [
    {
        "id": "normas",
        "label": "Normas e regulação",
        "query": "resolução ANP, Diário Oficial combustíveis, ASTM nova norma, ASTM norma atualizada",
    },
    {
        "id": "petroleo",
        "label": "Petróleo",
        "query": (
            "petróleo Brasil, produção de petróleo Petrobras, exportação de petróleo, "
            "BSW petróleo, densidade API petróleo, salinidade petróleo"
        ),
    },
    {
        "id": "claros",
        "label": "Combustíveis claros",
        "query": "diesel S10 Brasil, gasolina Brasil ANP, querosene de aviação, nafta petroquímica",
    },
    {
        "id": "escuros",
        "label": "Produtos escuros e especiais",
        "query": "óleo combustível Brasil, lubrificantes Petrobras, benzeno indústria, hexano indústria",
    },
    {
        "id": "mercado",
        "label": "Mercado e preços",
        "query": "preço do petróleo Brent, petróleo WTI cotação, câmbio dólar hoje",
    },
    {
        "id": "setor",
        "label": "Setor e negócios",
        "query": "Petrobras comunicado, IBP petróleo e gás, leilão ANP, epbr petróleo",
    },
]


def google_news_url(query):
    terms = [t.strip() for t in query.split(",") if t.strip()]
    q = " OR ".join(terms)
    params = {"q": q, "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-BR"}
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)


def fetch_items(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    items = []
    for item in root.findall(".//item")[:10]:
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub_date = item.findtext("pubDate") or ""
        source_el = item.find("source")
        source = source_el.text if source_el is not None and source_el.text else ""
        items.append({"title": title, "link": link, "pubDate": pub_date, "source": source})
    return items


def main():
    result = {
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "categories": [],
    }
    for cat in CATEGORIES:
        try:
            items = fetch_items(google_news_url(cat["query"]))
            ok = True
        except Exception:
            items = []
            ok = False
        result["categories"].append(
            {"id": cat["id"], "label": cat["label"], "ok": ok, "items": items}
        )

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
