"""
LifeUp TTS — serviço de voz neural do Edge (edge-tts) para o app LifeUp.

Expõe um endpoint HTTP que recebe texto e devolve áudio MP3 sintetizado com as
vozes neurais do Microsoft Edge (as mesmas "Online (Natural)"). É o mesmo motor
gratuito usado pelo claude-code-tts, porém hospedado para que o app web possa
chamá-lo de qualquer navegador/dispositivo.

Endpoints:
  GET /            -> healthcheck
  GET /voices      -> lista de vozes pt-BR disponíveis
  GET /tts?text=...&voice=pt-BR-ThalitaNeural&rate=+0%&pitch=+0Hz -> audio/mpeg
"""
import io
import edge_tts
from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LifeUp TTS", docs_url="/docs")

# CORS liberado para o app poder chamar de qualquer origem (GitHub Pages etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

DEFAULT_VOICE = "pt-BR-ThalitaNeural"  # feminina, fluida


@app.get("/")
def health():
    return {"ok": True, "service": "lifeup-tts", "engine": "edge-tts"}


@app.get("/voices")
async def voices():
    vs = await edge_tts.list_voices()
    ptbr = [
        {"name": v["ShortName"], "gender": v["Gender"]}
        for v in vs
        if v["Locale"].lower() == "pt-br"
    ]
    return {"voices": ptbr}


@app.get("/tts")
async def tts(
    text: str = Query(..., min_length=1, max_length=4000),
    voice: str = Query(DEFAULT_VOICE),
    rate: str = Query("+0%"),    # ex.: "+15%", "-10%"
    pitch: str = Query("+0Hz"),  # ex.: "+2Hz"
):
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        data = buf.getvalue()
        if not data:
            raise HTTPException(status_code=502, detail="Sem áudio gerado")
        return Response(
            content=data,
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=86400"},
        )
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))
