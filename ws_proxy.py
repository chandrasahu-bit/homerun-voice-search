#!/usr/bin/env python3
"""Browser <-> Sarvam realtime STT bridge.

The browser cannot talk to Sarvam directly: the realtime socket authenticates by
HTTP header only (query-string keys are rejected), and browsers cannot set
headers on a WebSocket. So this proxy holds the key and relays frames.

Browser sends : raw 16kHz mono PCM16 binary frames
Browser gets  : {"event":"transcript.partial"|"transcript.final","text":...,"language":...}
"""
import asyncio, json, sys, urllib.parse, pathlib
import websockets

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))
import server                       # reuse the .env loader

KEY  = server.ENV.get("SARVAM_API_KEY", "")
PORT = 8788
SARVAM = "wss://api.sarvam.ai/speech-to-text-realtime/ws"

# NOTE: do NOT pass brand names via ?prompt= - measured, it truncates and
# hallucinates ('Ashir', 'A couple of hours later'). It is an instruction
# prompt, not a phrase-bias list. keyterms (below) is the real mechanism -
# saaras:v4 only, up to 50 terms / 64 chars each, biases without forcing.
# The list itself is a backend control lever (data/keyterms.txt, owned and
# hot-reloaded by server.get_keyterms()) - edit that file, no restart here.
PARAMS = {"model": "saaras:v4", "language_code": "auto",
          "endpointing": "vad", "mode": "transcribe"}

async def bridge(browser):
    if not KEY:
        await browser.send(json.dumps({"event": "error", "message": "no SARVAM_API_KEY"}))
        return
    params = dict(PARAMS)
    terms = server.get_keyterms()
    if terms:
        params["keyterms"] = json.dumps(terms)
    url = SARVAM + "?" + urllib.parse.urlencode(params)
    try:
        up = await websockets.connect(url, additional_headers={"api-subscription-key": KEY},
                                      open_timeout=20, max_queue=64)
    except Exception as e:
        await browser.send(json.dumps({"event": "error", "message": f"sarvam: {e}"}))
        return

    async def to_sarvam():
        try:
            async for msg in browser:
                if isinstance(msg, bytes):
                    await up.send(msg)                  # raw PCM straight through
                else:
                    await up.send(msg)                  # control frames e.g. {"event":"stop"}
        except Exception:
            pass
        finally:
            try: await up.send(json.dumps({"event": "stop"}))
            except Exception: pass

    async def to_browser():
        try:
            async for msg in up:
                await browser.send(msg)                 # relay events verbatim
        except Exception:
            pass

    try:
        await asyncio.gather(to_sarvam(), to_browser())
    finally:
        await up.close()

async def main():
    print(f"Sarvam realtime STT proxy -> ws://127.0.0.1:{PORT}")
    print(f"  key {'present' if KEY else 'MISSING'} | model {PARAMS['model']} "
          f"| {len(server.get_keyterms())} keyterms")
    async with websockets.serve(bridge, "127.0.0.1", PORT, max_size=None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
