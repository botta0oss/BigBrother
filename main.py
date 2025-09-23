import scraper as sc
import traduttore as trad
import Analysis as An
import clustering as cl
import os, json, subprocess


#Inserimento di chiavi API e altri dati con json
def api_config():
    try:
        with open("config.json") as f:
            config = json.load(f)
            api_id = config['api_id']
            api_hash = config['api_hash']
            phone = config['phone'] 
            auth_key = config['auth_key']
            ollama = config['ollama']
            modello = config['modello']
    except FileNotFoundError:
        print("File 'paths.json' non trovato.")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
    return api_id,api_hash,phone,auth_key,ollama,modello

api_id,api_hash,phone,auth_key,ollama,modello = api_config()

'''
print("inizio scraping...")
#path_csv, nome_chat = sc.starter(api_id,api_hash,phone)
print("scraping concluso")

path_csv = "C:/Users/Utente/Desktop/BigBrother/BigBrother/data/TestBullismo/1.85T.csv"
nome_chat = "Test"


print("inizio traduzione...")
path_traduzione = trad.starter(path_csv,auth_key, nome_chat)
print("fine traduzione")
print(f"file salvato in: {path_traduzione}")



print("inizio analisi... ")
analisi_csv, parole_csv, csv_parole_utenti, utenti_msg_csv, path_date_csv, emoji_utente_csv, polarizzazione, utente_s_csv, s_periodo_csv = An.starter(path_traduzione)
path_cartella_csv = os.path.split(analisi_csv)[0]
print("analisi completate...")



print("inizio clustering... ")
clustering_csv, cluster_labels_csv = cl.starter(analisi_csv, path_cartella_csv, ollama, modello)
print("clustering completato...")

print(f"file csv salvati in: {path_cartella_csv} \n")

map_paths = {
    'nome_chat': nome_chat,
    'sentiment_csv': analisi_csv,
    'parole_csv': parole_csv, 
    'parole_utenti_csv': csv_parole_utenti,
    'messaggi_utenti_csv': utenti_msg_csv,
    'date': path_date_csv,
    'sentiment_per_utente_csv': utente_s_csv,
    'emoji_per_utente_csv': emoji_utente_csv,
    'avg_sentiment_per_periodo_csv': s_periodo_csv,
    'polarizzazione': list(polarizzazione),
    'database': clustering_csv,
    'cluster_label_csv': cluster_labels_csv
}
path_cartella = os.path.split(path_cartella_csv)[0]
nome = os.path.split(path_cartella)[1]
path_json = os.path.join(path_cartella,nome + '.json')
'''


if __name__ == "__main__":
    '''
    with open(path_json, "w") as f:
        json.dump(map_paths, f)
    '''
    path_json = "C:/Users/Utente/Desktop/BigBrother/BigBrother/data/TestBullismo/TestBullismo.json"  # per analisi, da cancellare
    
    command = ["streamlit", "run", "dashboard.py", "--", path_json]
    subprocess.run(command)


