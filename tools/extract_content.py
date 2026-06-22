#!/usr/bin/env python3
"""
LifeUp — Extrator de conteúdo (uso LOCAL / PRIVADO)
===================================================
Converte os seus arquivos das lições (DOCX/PDF) em `content/licoes.json`,
no formato que o app LifeUp lê para mostrar e narrar o conteúdo completo.

⚠️  Este JSON NÃO deve ser publicado (material protegido). Ele é ignorado
    pelo Git (.gitignore) e fica apenas no seu dispositivo.

Uso:
    pip install pymupdf        # só necessário para PDFs (ex.: Lição 1)
    python tools/extract_content.py
"""
import json, os, re, zipfile, html, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Linhas de cabeçalho/rodapé repetidas que devem ser removidas (boilerplate)
BOILER = [
    'life success', 'pensando em resultados', 'pensando nos resultados',
    'para lideres', 'para líderes', 'guia do participante',
    'não está permitida a duplicação', 'nao esta permitida a duplicacao',
    'todos os direitos reservados', 'proctor', 'gallagher',
]

def clean_lines(raw):
    out, seen_blank = [], False
    for ln in raw.split('\n'):
        ln = re.sub(r'[ \t ]+', ' ', ln).strip()
        low = ln.lower()
        if not ln:
            seen_blank = True
            continue
        if any(b in low for b in BOILER):      # remove boilerplate
            continue
        if re.fullmatch(r'[\d\.\-–—\s]+', ln):  # linhas só com números/traços
            continue
        if len(ln) <= 2:
            continue
        if seen_blank and out:
            out.append('')                       # preserva quebra de parágrafo
        seen_blank = False
        out.append(ln)
    # junta e re-separa em parágrafos
    text = '\n'.join(out)
    paras = [p.strip().replace('\n', ' ') for p in re.split(r'\n\s*\n', text)]
    return [p for p in paras if len(p) > 2]

def from_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    xml = xml.replace('</w:p>', '\n').replace('<w:br/>', '\n').replace('<w:tab/>', ' ')
    txt = html.unescape(re.sub(r'<[^>]+>', '', xml))
    return clean_lines(txt)

def from_pdf(path):
    import fitz  # pymupdf
    d = fitz.open(path)
    txt = '\n'.join(p.get_text() for p in d)
    return clean_lines(txt)

def extract(path):
    return from_docx(path) if path.lower().endswith('.docx') else from_pdf(path)

# Encontra a melhor fonte por lição (prefere DOCX limpo; fallback PDF)
def find_source(n):
    pats = [f'LICAO {n}/*.docx', f'LICAO {n}/*.pdf',
            f'PDF LIÇÕES TIR PARA CLIENTES/Lic*o {n} *.pdf',
            f'PDF LIÇÕES TIR PARA CLIENTES/Lic*o {n}-*.pdf']
    for pat in pats:
        hits = sorted(glob.glob(os.path.join(ROOT, pat)))
        # evita arquivos auxiliares (persistencia, responsabilidade, etc.) preferindo o que tem o número no início do nome base
        hits = [h for h in hits if re.search(rf'lic[aã]o\s*{n}\b', os.path.basename(h).lower())]
        if hits:
            # prefere "rev final" / "corrigido" se existir
            for kw in ['rev final', 'corrigido', 'revisado']:
                for h in hits:
                    if kw in h.lower():
                        return h
            return hits[0]
    return None

TITLES = {
    1:'Um Ideal que Vale a Pena', 2:'A Distância entre Saber e Fazer',
    3:'A Sua Mente Infinita', 4:'O Gênio Secreto',
    5:'O Truque para Manter-se no Comando', 6:'O Ambiente é o Espelho de Nós Mesmos',
    7:'Demolindo a Barreira do Terror', 8:'O Poder da Prática',
    9:'A Palavra Mágica', 10:'A Pessoa Mais Valiosa: o Líder',
    11:'Deixando Todos com a Sensação de Acréscimo', 12:'Aumentando a Mente',
}

def looks_like_heading(p):
    if len(p) > 70 or len(p) < 3:
        return False
    if p.endswith(('.', '!', '?', ':', ',', ';')):
        return False
    letters = [c for c in p if c.isalpha()]
    if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.6:
        return True   # MAIÚSCULAS = título
    return p.istitle() and len(p.split()) <= 8

def to_sections(paras, default_heading):
    sections, cur = [], {'heading': default_heading, 'text': ''}
    for p in paras:
        if looks_like_heading(p):
            if cur['text'].strip():
                sections.append(cur)
            cur = {'heading': p, 'text': ''}
        else:
            cur['text'] = (cur['text'] + '\n\n' + p).strip() if cur['text'] else p
    if cur['text'].strip():
        sections.append(cur)
    return sections

def main():
    import datetime
    data, items = {}, []
    for n in range(1, 13):
        src = find_source(n)
        if not src:
            print(f'Lição {n}: ⚠️  nenhum arquivo encontrado')
            continue
        try:
            paras = extract(src)
            data[str(n)] = {'source': os.path.basename(src), 'paragraphs': paras}
            chars = sum(len(p) for p in paras)
            title = TITLES.get(n, f'Lição {n}')
            sections = to_sections(paras, title)
            items.append({
                'id': f'licao-{n:02d}', 'number': n, 'title': f'Lição {n} — {title}',
                'content': '\n\n'.join(paras), 'sections': sections,
            })
            print(f'Lição {n}: {len(paras):3d} parágrafos · {len(sections):2d} seções · {chars:6d} chars · {os.path.basename(src)}')
        except Exception as e:
            print(f'Lição {n}: ERRO {e} ({src})')

    os.makedirs(os.path.join(ROOT, 'content'), exist_ok=True)
    # licoes.json (formato simples, usado pelo import por aparelho)
    out1 = os.path.join(ROOT, 'content', 'licoes.json')
    with open(out1, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    # curso.json (formato do guia: modules/items/sections + contentVersion)
    curso = {
        'contentVersion': datetime.date.today().isoformat(),
        'course': 'Pensando em Resultados',
        'modules': [{'id': 'licoes', 'title': 'Lições', 'items': items}],
    }
    out2 = os.path.join(ROOT, 'content', 'curso.json')
    with open(out2, 'w', encoding='utf-8') as f:
        json.dump(curso, f, ensure_ascii=False)

    print(f'\n✅ content/licoes.json ({len(data)} lições, {os.path.getsize(out1)} bytes)')
    print(f'✅ content/curso.json  ({len(items)} itens, {os.path.getsize(out2)} bytes, versão {curso["contentVersion"]})')
    print('   (privados, no .gitignore — não suba no GitHub)')

if __name__ == '__main__':
    main()
