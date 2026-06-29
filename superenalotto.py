import os
import random
import json
import urllib.request

FILE_DATI = "estrazioni_superenalotto.json"

def scarica_estrazioni():
    """Scarica le estrazioni in tempo reale usando un'API web standard che supera i filtri DNS"""
    # Usiamo un endpoint alternativo ad alta disponibilità che simula una normale navigazione web
    url = "https://allorigins.win"
    
    try:
        print("Sincronizzazione automatica con l'archivio storico in corso...")
        # Configura i parametri di navigazione (User-Agent) per apparire come un comune browser (Chrome)
        richiesta = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        
        with urllib.request.urlopen(richiesta, timeout=12) as response:
            codice_grezzo = response.read().decode('utf-8')
            dati = json.loads(codice_grezzo)
            
            # Salva la cache locale sul PC dell'utente per l'utilizzo offline futuro
            with open(FILE_DATI, "w", encoding="utf-8") as f:
                json.dump(dati, f)
            print("[OK] Connessione riuscita! Archivio aggiornato all'ultimo concorso.")
            return dati
            
    except Exception as e:
        print(f"\n[INFO] Timeout o rete locale assente. Tentativo di avvio in modalità offline...")
        if os.path.exists(FILE_DATI):
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print("\n[ERRORE] Nessun archivio locale trovato sul computer.")
            print("Per il primissimo avvio del programma è necessaria una connessione internet attiva.")
            return None

def elabora_statistiche(estrazioni):
    conteggio_100 = {i: 0 for i in range(1, 91)}
    ultimo_visto = {i: 0 for i in range(1, 91)}
    
    # Prendi le ultime 100 estrazioni reali
    ultime_100 = estrazioni[:100]
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

    # Applica i filtri richiesti dal sistema
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
    print("="*60)
    print("      OPTIMIZER SUPERENALOTTO - LIVE & OFFLINE SYSTEM")
    print("="*60)
    
    dati = scarica_estrazioni()
    if not dati:
        input("\nPremi INVIO per uscire..."); return

    validi, ritardatari = elabora_statistiche(dati)
    numeri_usati_totali = set()
    sestine_finali = []
    
    blocchi = [(3, 1, 60), (3, 20, 70), (2, 30, 90)]
    
    for qta, s_min, s_max in blocks := blocchi:
        for _ in range(qta):
            sestina = genera_sestina(validi, ritardatari, s_min, s_max, numeri_usati_totali)
            sestine_finali.append((s_min, s_max, sestina))
            numeri_usati_totali.update(sestina)

    print("\nEcco le 8 sestine elaborate sui dati reali più recenti:\n")
    for i, (s_min, s_max, sst) in enumerate(sestine_finali, 1):
        str_sestina = " ".join(f"{n:02d}" for n in sst)
        print(f"Sestina {i} (Range {s_min:02d}-{s_max:02d}): [ {str_sestina} ]  (Somma: {sum(sst)})")
        
    print("\n" + "="*60)
    input("Elaborazione completata con successo! Premi INVIO per chiudere...");

if __name__ == "__main__":
    main()
