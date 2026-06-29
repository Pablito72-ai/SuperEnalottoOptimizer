import random

def ottieni_archivio_incorporato():
    """Archivio storico recente integrato direttamente nel codice per il funzionamento 100% offline"""
    # Struttura dati fissa: contiene le ultime estrazioni storiche necessarie ai calcoli dei filtri
    return [
        {"combinazione": [2, 14, 33, 45, 71, 88]}, {"combinazione": [7, 18, 24, 49, 62, 81]},
        {"combinazione": [11, 22, 38, 52, 75, 84]}, {"combinazione": [4, 15, 29, 53, 60, 86]},
        {"combinazione": [1, 5, 19, 36, 47, 90]}, {"combinazione": [3, 16, 27, 42, 54, 57]},
        {"combinazione": [20, 31, 43, 56, 62, 69]}, {"combinazione": [21, 34, 46, 58, 61, 67]},
        {"combinazione": [23, 35, 48, 50, 65, 70]}, {"combinazione": [32, 44, 58, 71, 84, 88]},
        {"combinazione": [37, 49, 62, 75, 81, 86]}, {"combinazione": [5, 12, 28, 41, 63, 79]},
        {"combinazione": [9, 17, 30, 55, 66, 82]}, {"combinazione": [13, 25, 39, 47, 68, 89]},
        {"combinazione": [6, 26, 40, 51, 73, 85]}, {"combinazione": [8, 19, 33, 59, 74, 87]},
        {"combinazione": [10, 21, 35, 64, 77, 83]}, {"combinazione": [15, 22, 45, 60, 72, 90]},
        {"combinazione": [2, 11, 31, 52, 61, 80]}, {"combinazione": [4, 18, 38, 53, 67, 81]},
        {"combinazione": [7, 14, 24, 49, 75, 84]}, {"combinations": [3, 27, 36, 56, 70, 86]},
        {"combinazione": [1, 16, 29, 42, 62, 88]}, {"combinazione": [23, 34, 46, 58, 69, 85]},
        {"combinazione": [20, 32, 44, 50, 65, 68]}, {"combinazione": [9, 13, 25, 47, 54, 77]},
        {"combinazione": [6, 17, 39, 51, 63, 79]}, {"combinazione": [8, 26, 40, 55, 66, 82]},
        {"combinazione": [10, 12, 28, 41, 73, 89]}, {"combinazione": [5, 15, 30, 59, 74, 87]}
    ]

def elabora_statistiche(estrazioni):
    """Esegue lo screening statistico escludendo i frequenti ed estraendo i ritardatari prioritari"""
    conteggio_100 = {i: 0 for i in range(1, 91)}
    ultimo_visto = {i: 0 for i in range(1, 91)}
    
    for conc in estrazioni:
        sestina = conc.get("combinazione", conc.get("sestina", []))[:6]
        for num in sestina:
            if 1 <= num <= 90:
                conteggio_100[num] += 1

    for indice, conc in enumerate(estrazioni):
        sestina = conc.get("combinazione", conc.get("sestina", []))[:6]
        for num in sestina:
            if 1 <= num <= 90 and ultimo_visto[num] == 0:
                ultimo_visto[num] = indice + 1

    # Filtro: rimuove i numeri estratti almeno 2 volte nel periodo
    esclusi = [n for n, v in conteggio_100.items() if v >= 2]
    
    # 20 Numeri più ritardatari inseriti come opzione vincolante
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
        
        # Filtro Somma (150 - 400)
        if not (150 <= sum(sestina) <= 400):
            continue
            
        # Filtro Distanza geometrica media (Tolleranza 13-17 per adattarsi ai range ridotti)
        distanze = [sestina[i+1] - sestina[i] for i in range(len(sestina)-1)]
        distanza_media = sum(distanze) / len(distanze)
        if not (13 <= distanza_media <= 17):
            continue
            
        return sestina
    return sorted(random.sample(pool_filtrato, 6))

def main():
    print("="*60)
    print("      ELABORATORE ESTRATTORE SUPERENALOTTO 100% OFFLINE")
    print("="*60)
    
    dati = ottieni_archivio_incorporato()
    validi, ritardatari = elabora_statistiche(dati)
    numeri_usati_totali = set()
    sestine_finali = []
    
    blocchi = [(3, 1, 60), (3, 20, 70), (2, 30, 90)]
    
    for qta, s_min, s_max in blocchi:
        for _ in range(qta):
            sestina = genera_sestina(validi, ritardatari, s_min, s_max, numeri_usati_totali)
            sestine_finali.append((s_min, s_max, sestina))
            numeri_usati_totali.update(sestina)

    print("\nEcco le 8 sestine generate in modalità offline nativa:\n")
    for i, (s_min, s_max, sst) in enumerate(sestine_finali, 1):
        str_sestina = " ".join(f"{n:02d}" for n in sst)
        print(f"Sestina {i} (Range {s_min:02d}-{s_max:02d}): [ {str_sestina} ]  (Somma: {sum(sst)})")
        
    print("\n" + "="*60)
    input("Elaborazione offline completata! Premi INVIO per chiudere...");

if __name__ == "__main__":
    main()
