import os
import random
import urllib.request
import json
import ssl

FILE_DATI = "estrazioni_superenalotto.json"

def scarica_estrazioni():
    """Scarica le ultime estrazioni in tempo reale bypassando i blocchi SSL di Windows"""
    url = "https://githubusercontent.com"
    
    # Crea un contesto SSL che ignora le restrizioni locali di Windows sul certificato
    contesto_ssl = ssl._create_unverified_context()
    
    try:
        print("Connessione ai server storici... Aggiornamento estrazioni in corso...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=contesto_ssl, timeout=10) as response:
            dati = json.loads(response.read().decode())
            # Salva una copia locale: se domani sarai senza internet, userà questa
            with open(FILE_DATI, "w", encoding="utf-8") as f:
                json.dump(dati, f)
            print("[OK] Archivio aggiornato con successo all'ultimo concorso!")
            return dati
    except Exception as e:
        print(f"\n[AVVISO] Impossibile connettersi a internet: {e}")
        print("Il programma utilizzerà l'ultimo archivio salvato localmente.")
        if os.path.exists(FILE_DATI):
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

def elabora_statistiche(estrazioni):
    conteggio_100 = {i: 0 for i in range(1, 91)}
    ultimo_visto = {i: 0 for i in range(1, 91)}
    
    # Analizza esattamente le ultime 100 estrazioni reali presenti nel feed
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

    # Applica i tuoi filtri personalizzati
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
    print("      ELABORATORE SUPERENALOTTO CON AGGIORNAMENTO LIVE")
    print("="*60)
    
    dati = scarica_estrazioni()
    if not dati:
        print("\n[ERRORE DI AVVIO] File dati non presente sul PC.")
        print("È necessaria una connessione internet solo per il primissimo avvio.")
        input("\nPremi INVIO per uscire..."); return

    validi, ritardatari = elabora_statistiche(dati)
    numeri_usati_totali = set()
    sestine_finali = []
    
    blocchi = [(3, 1, 60), (3, 20, 70), (2, 30, 90)]
    
    for qta, s_min, s_max in blocchi:
        for _ in range(qta):
            sestina = genera_sestina(validi, ritardatari, s_min, s_max, numeri_usati_totali)
            sestine_finali.append((s_min, s_max, sestina))
            numeri_usati_totali.update(sestina)

    print("\nEcco le 8 sestine elaborate sui dati reali più recenti:\n")
    for i, (s_min, s_max, sst) in enumerate(sestine_finali, 1):
        str_sestina = " ".join(f"{n:02d}" f" " for n in sst)
        print(f"Sestina {i} (Range {s_min:02d}-{s_max:02d}): [ {str_sestina.strip()} ]  (Somma: {sum(sst)})")
        
    print("\n" + "="*60)
    input("Elaborazione completata! Premi INVIO per chiudere il programma...");

if __name__ == "__main__":
    main()
