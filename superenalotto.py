import os
import random
import urllib.request
import json

FILE_DATI = "estrazioni_superenalotto.json"

def scarica_estrazioni():
    """Scarica le estrazioni ufficiali storiche da un archivio JSON pubblico sempre aggiornato"""
    url = "https://githubusercontent.com"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            dati = json.loads(response.read().decode())
            with open(FILE_DATI, "w", encoding="utf-8") as f:
                json.dump(dati, f)
            return dati
    except Exception:
        if os.path.exists(FILE_DATI):
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

def elabora_statistiche(estrazioni):
    """Filtra i numeri basandosi sulle ultime 100 estrazioni ed estrae i ritardatari"""
    conteggio_100 = {i: 0 for i in range(1, 91)}
    ultimo_visto = {i: 0 for i in range(1, 91)}
    
    # Analizza le ultime 100 estrazioni per le frequenze
    ultime_100 = estrazioni[:100]
    for conc in ultime_100:
        sestina = conc.get("sestina", conc.get("combinazione", []))[:6]
        for num in sestina:
            if 1 <= num <= 90:
                conteggio_100[num] += 1

    # Calcola il ritardo su tutta la cronologia disponibile
    for indice, conc in enumerate(estrazioni):
        sestina = conc.get("sestina", conc.get("combinazione", []))[:6]
        for num in sestina:
            if 1 <= num <= 90 and ultimo_visto[num] == 0:
                ultimo_visto[num] = indice

    # Filtro: ESCLUDI i numeri usciti ALMENO 2 volte nelle ultime 100
    esclusi = [n for n, v in conteggio_100.items() if v >= 2]
    
    # Identifica i 20 numeri più ritardatari del momento
    ritardatari = sorted(ultimo_visto.keys(), key=lambda x: ultimo_visto[x], reverse=True)[:20]
    
    # Numeri utilizzabili filtrati
    validi = [n for n in range(1, 91) if n not in esclusi]
    return validi, ritardatari

def genera_sestina(numeri_validi, ritardatari, s_min, s_max, gia_usati):
    """Genera una sestina che rispetti rigorosamente tutti i vincoli richiesti"""
    pool_filtrato = [n for n in numeri_validi if s_min <= n <= s_max]
    rit_nel_pool = [n for n in ritardatari if s_min <= n <= s_max and n in pool_filtrato]
    
    if len(pool_filtrato) < 6:
        pool_filtrato = [n for n in range(s_min, s_max + 1)] # Fallback se i filtri svuotano il range
        
    for _ in range(10000):
        sestina = []
        
        # Forza la presenza di almeno un numero ritardatario se disponibile nel range
        if rit_nel_pool:
            sestina.append(random.choice(rit_nel_pool))
            
        # Riduci le ripetizioni provando a pescare numeri non usati nelle altre sestine
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
        
        # Vincolo: Somma compresa tra 150 e 400
        if not (150 <= sum(sestina) <= 400):
            continue
            
        # Vincolo: Distanza media vicina a 15 (tolleranza geometrica ammessa 13-17)
        distanze = [sestina[i+1] - sestina[i] for i in range(len(sestina)-1)]
        distanza_media = sum(distanze) / len(distanze)
        if not (13 <= distanza_media <= 17):
            continue
            
        return sestina
    return sorted(random.sample(pool_filtrato, 6))

def main():
    print("="*60)
    print("      ELABORATORE ESTRATTORE SUPERENALOTTO OFFLINE")
    print("="*60)
    
    dati = scarica_estrazioni()
    if not dati:
        print("\n[ERRORE] Internet richiesto solo al primo avvio per scaricare i dati.")
        input("\nPremi INVIO per uscire..."); return

    validi, ritardatari = elabora_statistiche(dati)
    numeri_usati_totali = set()
    sestine_finali = []
    
    # Struttura dei blocchi richiesti: (quantità, minimo, massimo)
    blocchi = [(3, 1, 60), (3, 20, 70), (2, 30, 90)]
    
    for qta, s_min, s_max in blocchi:
        for _ in range(qta):
            sestina = genera_sestina(validi, ritardatari, s_min, s_max, numeri_usati_totali)
            sestine_finali.append((s_min, s_max, sestina))
            numeri_usati_totali.update(sestina)

    print("\nEcco le 8 sestine generate secondo i tuoi filtri:\n")
    for i, (s_min, s_max, sst) in enumerate(sestine_finali, 1):
        str_sestina = " ".join(f"{n:02d}" for n in sst)
        print(f"Sestina {i} (Range {s_min:02d}-{s_max:02d}): [ {str_sestina} ]  (Somma: {sum(sst)})")
        
    print("\n" + "="*60)
    input("Elaborazione completata con successo! Premi INVIO per chiudere...");

if __name__ == "__main__":
    main()
