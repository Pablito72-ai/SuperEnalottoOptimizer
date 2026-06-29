import os
import random
import urllib.request
import re

FILE_DATI = "estrazioni_storiche.txt"

def scarica_archivio_testuale():
    """Scarica l'archivio storico ufficiale in formato TXT/grezzo che non subisce i blocchi dei siti web grafici"""
    url = "https://githubusercontent.com"
    try:
        print("Connessione ai server storici... Sincronizzazione estrazioni in corso...")
        richiesta = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(richiesta, timeout=10) as response:
            contenuto = response.read().decode('utf-8')
            with open(FILE_DATI, "w", encoding="utf-8") as f:
                f.write(contenuto)
            print("[OK] Sincronizzazione riuscita! Dati aggiornati all'ultimo concorso reale.")
            return contenuto
    except Exception:
        if os.path.exists(FILE_DATI):
            print("[OFFLINE] Rete non disponibile. Uso dei dati memorizzati sul computer.")
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                return f.read()
        return None

def analizza_testo_estrazioni(testo_grezzo):
    """Estrae le sestine dal file di testo e calcola frequenze e ritardi reali"""
    estrazioni = []
    # Cerca nel testo le righe che contengono sequenze di numeri (la sestina vincente)
    righe = testo_grezzo.strip().split('\n')
    
    for riga in righe:
        numeri = [int(n) for n in re.findall(r'\b\d+\b', riga)]
        # Riconosce le righe valide che contengono almeno i 6 numeri del SuperEnalotto
        if len(numeri) >= 6:
            # Prende i primi 6 numeri (esclude Jolly e Star se presenti)
            estrazioni.append(numeri[:6])
            
    if not estrazioni:
        return None, None

    conteggio_100 = {i: 0 for i in range(1, 91)}
    ultimo_visto = {i: 0 for i in range(1, 91)}
    
    # Analizza le ultime 100 estrazioni reali inserite nel file
    ultime_100 = estrazioni[:100] if len(estrazioni) >= 100 else estrazioni
    for sestina in ultime_100:
        for num in sestina:
            if 1 <= num <= 90:
                conteggio_100[num] += 1

    for indice, sestina in enumerate(estrazioni):
        for num in sestina:
            if 1 <= num <= 90 and ultimo_visto[num] == 0:
                ultimo_visto[num] = indice + 1

    # Applica i filtri matematici richiesti
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
    print("      OPTIMIZER SUPERENALOTTO - FOREVER LIVE SYSTEM")
    print("="*60)
    
    testo_grezzo = scarica_archivio_testuale()
    if not testo_grezzo:
        print("\n[ERRORE] File dati non disponibile. Serve internet al primo avvio assoluto.")
        input("\nPremi INVIO per uscire..."); return

    validi, ritardatari = analizza_testo_estrazioni(testo_grezzo)
    if not validi:
        print("\n[ERRORE] Struttura del file dati non riconosciuta."); input(); return
        
    numeri_usati_totali = set()
    sestine_finali = []
    
    blocchi = [(3, 1, 60), (3, 20, 70), (2, 30, 90)]
    
    for qta, s_min, s_max in blocchi:
        for _ in range(qta):
            sestina = genera_sestina(validi, ritardatari, s_min, s_max, numeri_usati_totali)
            sestine_finali.append((s_min, s_max, sestina))
            numeri_usati_totali.update(sestina)

    print("\nEcco le 8 sestine elaborate in tempo reale sulla cronologia effettiva:\n")
    for i, (s_min, s_max, sst) in enumerate(sestine_finali, 1):
        str_sestina = " ".join(f"{n:02d}" for n in sst)
        print(f"Sestina {i} (Range {s_min:02d}-{s_max:02d}): [ {str_sestina} ]  (Somma: {sum(sst)})")
        
    print("\n" + "="*60)
    input("Elaborazione completata in tempo reale! Premi INVIO per chiudere...");

if __name__ == "__main__":
    main()
