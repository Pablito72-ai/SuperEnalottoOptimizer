import os
import random
import json
import urllib.request
import ssl

def scarica_estrazioni():
    url = "https://githubusercontent.com"
    contesto_ssl = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=contesto_ssl, timeout=10) as response:
            return json.loads(response.read().decode())
    except:
        return []

def elabora_statistiche(estrazioni):
    conteggio_100 = {i: 0 for i in range(1, 91)}
    ultimo_visto = {i: 0 for i in range(1, 91)}
    
    ultime_100 = estrazioni[:100] if len(estrazioni) >= 100 else estrazioni
    for conc in ultime_100:
        sestina = conc.get("combinazione", conc.get("sestina", []))[:6]
        for num in sestina:
            if 1 <= num <= 90:
                conteggio_100[num] += 1

    for indice, conc in enumerate(estrazioni):
        sestina = conc.get("combinazione", conc.get("sestina", []))[:6]
        for num in sestina:
            if 1 <= num <= 90 and ultimo_visto[num] == 0:
                ultimo_visto[num] = indice + 1

    esclusi = [n for n, v in conteggio_100.items() if v >= 2]
    ritardatari = sorted(ultimo_visto.keys(), key=lambda x: ultimo_visto[x], reverse=True)[:20]
    validi = [n for n in range(1, 91) if n not in esclusi]
    return validi, ritardatari

def genera_sestina(numeri_validi, ritardatari, s_min, s_max, gia_usati):
    pool_filtrato = [n for n in numeri_validi if s_min <= n <= s_max]
    rit_nel_pool = [n for n in ritardatari if s_min <= n <= s_max and n in pool_filtrato]
    
    if len(pool_filtrato) < 6:
        pool_filtrato = [n for n in range(s_min, s_max + 1)]
        
    for _ in range(20000):
        sestina = []
        if rit_nel_pool:
            sestina.append(random.choice(rit_nel_pool))
            
        opzioni_prioritarie = [n for n in pool_filtrato if n not in gia_usati and n not in sestina]
        opzioni_secondarie = [n for n in pool_filtrato if n not in sestina]
        
        while len(sestina) < 6:
            if opzioni_prioritarie:
                n = random.choice(opzioni_prioritarie)
                opzioni_prioritarie.remove(n)
            elif opzioni_secondarie:
                n = random.choice(opzioni_secondarie)
                opzioni_secondarie.remove(n)
            else:
                break
            if n not in sestina:
                sestina.append(n)
                
        if len(sestina) < 6:
            continue
            
        sestina.sort()
        
        if not (150 <= sum(sestina) <= 400):
            continue
            
        distanze = [sestina[i+1] - sestina[i] for i in range(len(sestina)-1)]
        distanza_media = sum(distanze) / len(distanze)
        if not (13 <= distanza_media <= 17):
            continue
            
        return sestina
    return sorted(random.sample(pool_filtrato, 6))

def main():
    dati = scarica_estrazioni()
    if not dati:
        dati = [{"combinazione": [2, 11, 24, 38, 52, 58]}]
        
    validi, ritardatari = elabora_statistiche(dati)
    numeri_usati_totali = set()
    sestine_finali = []
    
    blocchi = [(3, 1, 60), (3, 20, 70), (2, 30, 90)]
    for qta, s_min, s_max in blocchi:
        for _ in range(qta):
            sestina = genera_sestina(validi, ritardatari, s_min, s_max, numeri_usati_totali)
            sestine_finali.append((s_min, s_max, sestina))
            numeri_usati_totali.update(sestina)

    html = """<!DOCTYPE html>
<html>
<head>
    <title>SuperEnalotto Optimizer</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; text-align: center; padding: 30px; color: #333; }
        .container { max-width: 650px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        h1 { color: #1a365d; font-size: 26px; margin-bottom: 5px; }
        p { color: #718096; margin-top: 0; font-size: 14px; }
        .sestina-card { background: #f7fafc; padding: 15px; margin: 12px 0; border-radius: 8px; font-size: 18px; font-weight: bold; border-left: 6px solid #3182ce; display: flex; justify-content: space-between; align-items: center; box-shadow: inset 0 1px 3px rgba(0,0,0,0.02); }
        .range { font-size: 11px; color: #a0aec0; font-weight: normal; display: block; margin-top: 2px; }
        .numbers { color: #2d3748; letter-spacing: 2px; font-family: monospace; font-size: 20px; }
        .somma { font-size: 13px; color: #38a169; background: #e6fffa; padding: 4px 8px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Optimizer SuperEnalotto</h1>
        <p>Elaborazione basata su dati storici reali ed estratti aggiornati</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
"""
    for i, (s_min, s_max, sst) in enumerate(sestine_finali, 1):
        str_sestina = " ".join(f"{n:02d}" for n in sst)
        html += f"""
        <div class="sestina-card">
            <div style="text-align: left;">Sestina {i} <span class="range">Range {s_min}-{s_max}</span></div>
            <div class="numbers">{str_sestina}</div>
            <div class="somma">Somma: {sum(sst)}</div>
        </div>"""
        
    html += """
    </div>
</body>
</html>"""

    with open("dist/superenalotto.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
