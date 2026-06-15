# Conteúdo completo (privado)

Esta pasta guarda o conteúdo **completo** das lições para uso **privado/local**.

⚠️ **Não publique este conteúdo.** O material das lições é protegido por direitos
autorais e não pode ser redistribuído publicamente. Por isso `licoes.json` está no
`.gitignore` e **não vai para o GitHub** — ele fica somente no seu dispositivo.

## Como gerar e usar (privado)

1. Tenha seus arquivos das lições (DOCX/PDF) nas pastas do projeto, como você já
   organizou (`LICAO 2/…`, `PDF LIÇÕES TIR PARA CLIENTES/…`).
2. Gere o arquivo de conteúdo no seu computador:
   ```bash
   pip install pymupdf        # necessário apenas para PDFs (ex.: Lição 1)
   python tools/extract_content.py
   ```
   Isso cria `content/licoes.json` (apenas localmente).
3. Abra o app **LifeUp** no seu aparelho → **Perfil → Importar conteúdo completo**
   → selecione o `licoes.json`.
4. Pronto: cada lição passa a mostrar o texto completo e o botão 🎧 **Ouvir**
   lê a sessão **na íntegra**. O conteúdo fica salvo só no seu aparelho.

> Para remover do aparelho depois, basta limpar os dados do app (Perfil →
> Reiniciar Progresso) ou importar um arquivo vazio.
