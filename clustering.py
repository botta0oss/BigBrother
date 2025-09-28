import pandas as pd
#from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS # da non usare se non si preprocessa
from bertopic import BERTopic
import umap.umap_ as umap
from sentence_transformers import SentenceTransformer
import re, subprocess, ollama, os



# controlla se il modello e llama sono setuppati correttamente
def gestore_llm(modello):
    comando = ["ollama", "list"]
    risultato = subprocess.run(comando, capture_output=True, check=True, text=True)
    modelli = risultato.stdout
    print(f"Modelli disponibili: \n{modelli}")
    # controlla se il modello è installato o nel caso lo installa
    if modello in modelli:
        print(f"il modello: {modello} è installato")
    else:
        processo = subprocess.Popen(["ollama", "pull", modello],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
        for line in processo.stdout:
            print(line, end="") 
        processo.wait()
        if processo.returncode == 0:
            print(f"Il modello {modello} è stato scaricato")
        else:
            print(f"Errore durante il download di: {modello}")

    return 

# esegue la richiesta al modello ollama
def llm_query(prompt, modello,i):
    risposta = ollama.generate(model= modello,prompt=prompt, options={'num_predict': 40, "temperature": 0.4,'stop': ['\n'] } )
    print(f" cluster {i} con etichetta:\n{risposta['response']}\n")
    label = risposta['response']
    return  label


# fa la richiesta per la creazione dell'ettichetta dei cluster
def descrizione_topic(df, modello, path_analisi):
    with open("clustering_prompt.txt", "r", encoding="utf-8") as file: 
        template_prompt = file.read()
    topic_labels = []
    clusters = []
    for c in df['cluster'].unique():
        if c != -1:
            clusters.append(c)
    clusters = sorted(clusters)
    for i in clusters: 
        # prendo tutte le righe con il n di cluster uguale a quello dell'iterazione in corso 
        cluster_corrente = df[df['cluster'] == i]
        # creo un campione di messaggi 
        dimensione_campione= min(10, len(cluster_corrente))
        campioni = cluster_corrente['message'].sample(n=dimensione_campione, random_state=42).tolist() 
        frasi = "\n- ".join(campioni)
        
        prompt_finale = template_prompt.replace("[messages]", frasi)
    
        label = llm_query(prompt_finale, modello,i)
        topic_labels.append({
            "cluster": i,
            "cluster_label": label
        })
    df_label = pd.DataFrame(topic_labels, columns=['cluster','cluster_label'])
    path = os.path.join(path_analisi, "cluster_label.csv")
    df_label.to_csv(path, index=False)

    return path 

# funzione per preprocessing dei messaggi (non in uso perchè deteriora la capacità di BERTopic in questo caso)
def preprocessing_testo(df):
    stop_words = set(ENGLISH_STOP_WORDS)
    parole_sicure_per_regex = []
    for parola in stop_words:
        parola_trasformata = re.escape(parola)
        parole_sicure_per_regex.append(parola_trasformata)
    pattern_delle_parole = '|'.join(parole_sicure_per_regex)
    regex_finale = r'\b(' + pattern_delle_parole + r')\b'
    df['message_pulito'] = (df['message'].fillna('').str.lower().str.replace(regex_finale, '', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip())

    df['message_pulito'] = df['message_pulito'].astype(str)
    return df




def starter(database, path_analisi, ollama_attivo, modello):
    df = pd.read_csv(database)
    # in questo caso non si fa preprocessing aggressivo dei messaggi in quanto eseguendo una regex sulle stopwords e modificando i 
    # messaggi si va a perdere tutto il contento semantico che però BERTopic comprende e duqnque si andrebbe a creare una clusterizzazione sbagliata
    # df = preprocessing_testo(df)

    # modello per gli embedding
    embedding_model = SentenceTransformer("paraphrase-MiniLM-L12-v2")
    
    # salvo gli embeddings che crerebbe Bert per poi usarli nella rappresentazione con grafico
    embeddings = embedding_model.encode(df['message'].tolist(),show_progress_bar=True)
    # creao un modello umap standard per rendere la dimensionalità sempre uguale (random_state= 42)
    umap_model = umap.UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine', random_state=42)
    # Uso BERTopic per eseguire il clustering 
    #topic_model = BERTopic(embedding_model = embedding_model, umap_model=umap_model)
    topic_model = BERTopic(umap_model=umap_model)
    topics, probs = topic_model.fit_transform(df['message'].tolist(), embeddings)
    df['cluster'] = topics
    
    ### da mantenere per grafico su dashboard
    # uso gli embeddings creati prima per ricevere da BERT solo la dimensionalità ridotta da inserire nel csv per poi plottare
    reduced_embeddings = topic_model.umap_model.transform(embeddings)
    df['plot_x'] = reduced_embeddings[:, 0]
    df['plot_y'] = reduced_embeddings[:, 1]

    cluster_csv = os.path.join(path_analisi, "cluster.csv")
    df.to_csv(cluster_csv, index=False, encoding='utf-8')
    print(f"CSV salvato in: {cluster_csv}")

    if ollama_attivo:
        gestore_llm(modello) # check che il modello sia scaricato, in caso contrario scarica
        label_csv = descrizione_topic(df, modello, path_analisi)
        return cluster_csv, label_csv
    else:
        return cluster_csv, None
    
    

    
    


database = None

if __name__ == "__main__":
    
    starter(database, path_analisi, ollama_attivo, modello)
  
   
    
    



