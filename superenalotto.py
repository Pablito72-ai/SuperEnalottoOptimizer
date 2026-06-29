import os
import random
import subprocess
import json

FILE_DATI = "estrazioni_superenalotto.json"

def scarica_estrazioni_con_powershell():
    """Usa PowerShell di Windows per scaricare l'archivio JSON. 
    Bypassa al 100% i blocchi antivirus e gli errori di rete dei file EXE."""
    url = "https://githubusercontent.com"
    
    # Comando di sistema Windows nativo per scaricare in sicurezza
    comando = f'PowerShell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri \'{url}\' -OutFile \'{FILE_DATI}\'"'
    
    try:
        print("Sincronizzazione automatica con l'archivio storico reale in corso...")
        # Esegue il comando in background senza mostrare finestre secondarie
        subprocess.run(comando, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(FILE_DATI):
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                dati = json.load(f)
            print("[OK] Connessione riuscita. Dati storici aggiornati all'ultimo concorso!")
            return dati
    except Exception:
        # Se sei completamente senza internet (offline), usa la copia precedentemente scaricata
        if os.path.exists(FILE_DATI):
            print("[OFFLINE] Impossibile connettersi. Uso dei dati locali salvati in precedenza.")
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                return json.load(f)
    return None

def elabora_statistiche(estrazioni):
    conteggio_100 = {i: 0 for i in range(1, 91)}
    ultimo_visto = {i: 0 for i in range(1, 91)}
    
    # Analizza le ultime 100 estrazioni reali scaricate
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

    # Applica i tuoi filtri statistici personalizzati
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
    print("      OPTIMIZER SUPERENALOTTO - AGGIORNAMENTO AUTOMATICO")
    print("="*60)
    
    dati = scarica_estrazioni_con_powershell()
    if not dati:
        print("\n[ERRORE] Impossibile avviare: serve internet solo per il primo avvio assoluto.")
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

    print("\nEcco le 8 sestine elaborate in tempo reale:\n")
    for i, (s_min, s_max, sst) in enumerate(sestine_finali, 1):
        str_sestina = " ".join(f"{n:02d}" for n in sst)
        print(f"Sestina {i} (Range {s_min:02d}-{s_max:02d}): [ {str_sestina} ]  (Somma: {sum(sst)})")
        
    print("\n" + "="*60)
    input("Elaborazione automatica completata! Premi INVIO per chiudere...");

if __name__ == "__main__":
    main()
