---
title: LifeUp TTS
emoji: 🎧
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# LifeUp TTS — voz neural do Edge (edge-tts)

Serviço que transforma texto em fala usando as **vozes neurais do Microsoft Edge**
(as "Online (Natural)") — o mesmo motor gratuito do `claude-code-tts`, porém
**hospedado** para que o app LifeUp possa usá-lo em qualquer navegador/celular.

## Como publicar no Hugging Face Spaces (grátis)

1. Acesse <https://huggingface.co/new-space>.
2. **Owner:** sua conta · **Space name:** `lifeup-tts` · **SDK:** `Docker` · **Public**.
3. Faça upload dos 3 arquivos desta pasta: `app.py`, `requirements.txt`, `Dockerfile`
   (e este `README.md`, que já tem o cabeçalho do Space).
4. Aguarde o build (1–3 min). A URL pública será algo como:
   `https://SEU-USUARIO-lifeup-tts.hf.space`

## Como conectar no app LifeUp

No app: **Perfil → Voz do mentor (edge-tts)** → cole a URL do Space (sem `/` no fim).
Pronto: o botão 🎧 **Ouvir** passa a usar a voz neural. Se o serviço cair, o app
volta sozinho para a voz do navegador.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | healthcheck |
| GET | `/voices` | lista as vozes pt-BR |
| GET | `/tts?text=Olá&voice=pt-BR-ThalitaNeural&rate=+0%` | retorna `audio/mpeg` |

## Vozes pt-BR recomendadas

- `pt-BR-ThalitaNeural` — feminina, fluida (**padrão**)
- `pt-BR-FranciscaNeural` — feminina
- `pt-BR-AntonioNeural` — masculina

## Rodar localmente (opcional)

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
# teste: http://localhost:7860/tts?text=Olá%20mundo
```
