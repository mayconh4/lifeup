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

def main():
    data = {}
    for n in range(1, 13):
        src = find_source(n)
        if not src:
            print(f'Lição {n}: ⚠️  nenhum arquivo encontrado')
            continue
        try:
            paras = extract(src)
            data[str(n)] = {'source': os.path.basename(src), 'paragraphs': paras}
            chars = sum(len(p) for p in paras)
            print(f'Lição {n}: {len(paras):3d} parágrafos · {chars:6d} chars · {os.path.basename(src)}')
        except Exception as e:
            print(f'Lição {n}: ERRO {e} ({src})')
    out = os.path.join(ROOT, 'content', 'licoes.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'\n✅ Gerado: content/licoes.json ({len(data)} lições, {os.path.getsize(out)} bytes)')
    print('   (este arquivo é privado e está no .gitignore — não suba no GitHub)')

if __name__ == '__main__':
    main()
