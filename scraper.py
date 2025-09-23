import os, csv, re
from telethon import TelegramClient
from telethon.tl.types import MessageService, Channel, Chat, PeerUser, PeerChannel, PeerChat
from tqdm import tqdm


# funzione per recuperare i messaggi 
async def raccogli_messagi (channel, limite): 
	message_data = {}
	i = 0
	# creo una progress bar 
	pbar = tqdm(desc="Scaricamento messaggi", unit=" messaggi", total=limite)
	# recupera tutti i messaggi del canale 
	async for msg in client.iter_messages(entity=channel, limit = limite):   
		pbar.update(1)
		# controllo che non stia scaricando messaggi di sistema -> nel caso passa al prossimo messaggio
		if not isinstance(msg, MessageService):
			if msg.message: # salvo solo messaggi di tipo testuale per scopi di ricerca (nel caso di software finale bisognerebbe codificarli come msg con media e salvare il media)
				try:
							# devo estrarre l'id numerico dall'ogetto che riceve usando .from_id tenendo conto che possano esserci classi diverse di oggetti
					if isinstance(msg.from_id, PeerUser):
						id = msg.from_id.user_id
					elif isinstance(msg.from_id, PeerChannel):
						id = msg.from_id.channel_id
					elif isinstance(msg.from_id, PeerChat):
						id = msg.from_id.chat_id
					else:
						id = None

					if msg.reply_to:
						risposta = msg.reply_to_msg_id
					else: 
						risposta = None

					message_data[i] = {
							"message": msg.message,
							"sender_id": id,
							"nome" : msg.sender.username,
							"cognome" : msg.sender.last_name,
							"nome_vero" : msg.sender.first_name, 
							"date": msg.date.isoformat(sep=' '),
							"message_id": msg.id, 
							"risposta": risposta, # l'id del messaggio originale a cui questo risponde
							}		
									
				except Exception as e:
					print(f"Errore nel messaggio {i}: {e}")
					continue
				i = i+1
	pbar.close()
	return message_data
		 
# funzione per gestire i canali a cui l'utente è iscritto, crea un dizionario da usare per permettere all'utente di 
# selezionare il canale su cui fare scraping 
async def lista_conversazioni() : 
	channels_index = {}
	i = 0
	async for dialog in client.iter_dialogs():
		bot = False
		entity = dialog.entity
		partecipanti = None 

		# per capire quanti partecipanti ci sono devo estrarre l'attributo dall'entity channel e chat 
		if isinstance(entity, Channel) or isinstance(entity, Chat):
				partecipanti = getattr(entity, "participants_count", None)

		# voglio che i bot non vengano mostrati funzione sottostante
		try:
			if dialog.entity.bot == True:
				bot = True
		except AttributeError:
			bot = False

		channels_index[i] = {
				"nome": dialog.name,
				"bot" : bot, 
				"id_grezzo" : dialog.id,
				"partecipanti" : partecipanti,  
			}
		i = i + 1
	return channels_index


# funzione che pulisce il nome del csv prima di passarlo per evitare errori con caratteri strani
def name_cleaner(nome):
	# espressione regolare per sostituire con un underscore i caratteri invalidi in windows 
	nome_pulito = re.sub(r'[<>:"/\\|?*]', '_', nome)        # \\ -> escape per \
	# trasforma gli spazi in underscore (.strip() elimina gli spazi all'inizio e alla fine per evitare underscore inutili)
	nome_pulito = re.sub(r'\s+', '_', nome_pulito.strip()) 
	return nome_pulito

#creazione cartella di lavoro 
def creazione_cartella(cartella):
	path_completo = os.path.join("C:/Users/Utente/Desktop/BigBrother/BigBrother/data", cartella)
	try:
		os.mkdir(path_completo)
	except FileExistsError:
		print(f"la cartella '{cartella}' esiste già")
	except PermissionError:
		print(f"Non è possibile creare la cartella '{cartella}', mancano privilegi")
	except Exception as e:
		print(f"Errore: '{e}'")
	return path_completo

# funzione che crea il csv database
def creatore_csv(nome_csv, message_data, campi):
	print("creando il database csv...")
	
	# pulisco il nome del canale 
	nome_csv = name_cleaner(nome_csv)
	# creo il path dove inserire il csv
	path_cartella = creazione_cartella(nome_csv)
	controllo_csv = nome_csv + ".csv"
	path_csv = os.path.join(path_cartella, controllo_csv)
	if os.path.exists(controllo_csv):
		print(f"Il file '{controllo_csv}' esiste già \n")
		nome_csv = input("Inserire nuovo nome per il file: ")
		nome_csv = name_cleaner(nome_csv)
		path_cartella = creazione_cartella(nome_csv)
		path_csv = os.path.join(path_cartella, nome_csv+".csv")
		print(f"salvando il csv in: {path_cartella}...")
	else:
		print(f"salvando il csv in: {path_cartella}...")
	# scrivo il csv nel path dato
	with open (path_csv+".csv", 'x', encoding='utf-8') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=campi)
		writer.writeheader()
		righe_csv = list(message_data.values())
		writer.writerows(righe_csv)
	print("file csv salvato")
	return path_csv, nome_csv
	



async def main(phone):
	await client.start(phone)
	print("Client pronto")
	canale_valido = False
	while not canale_valido:
		conversazioni = await lista_conversazioni()
		# mostrare in terminale le chat a disposizione 
		for i, info in conversazioni.items():
			print(f"{i}: {info['nome']}")
			print(f"numero di partecipanti: {info['partecipanti']}")
		# faccio scegliere all'utente il canale che vuole analizzare 
		try: 
			numero_canale = int(input("quale canale vuoi analizzare? "))
			# recupero l'id del canale scelto 
			id_entità = await client.get_entity(conversazioni[numero_canale]['id_grezzo'])
		except (KeyError, ValueError):
			print("\n Inserisci il numero relativo al canale da analizzare")
			continue
		# voglio che l'utente possa scegliere quanti messsaggi scaricare
		limite_messaggi = str(input("quanti messaggi vuoi analizzare? (scrivere None se non si vogliono limiti): "))
		if limite_messaggi.lower() == "none":
			limite_messaggi = None
		else: 
			try: 
				limite_messaggi = int(limite_messaggi)
			except ValueError:
				print("\n limite non valido, saranno scaricati tutti i messaggi")
				limite_messaggi = None
		# chiamo la funzione retrieve_msg per scaricare i messaggi 
		message_data = await raccogli_messagi(id_entità, limite_messaggi)
		# creo una condizione per la quale se il canale è vuoto il programma si chiude
		if len(message_data) > 0:
			print(f"\n scaricati {len(message_data)} messaggi")
			canale_valido = True
		else: 
			return print("il canale è vuoto, scegliere un altro canale\n")
	
	await client.disconnect()
	print("client disconnesso")	
	# creo il nome del csv tramite il nome del canale analizzato 
	nome_csv_temp = conversazioni[numero_canale]['nome'] 
	# creo lista con chiavi del primo messaggio per estrare gli header del csv
	campi_csv = list(message_data[0].keys())
	path_csv, nome_csv = creatore_csv(nome_csv_temp, message_data, campi_csv)
	print(f"Il file è stato salvato in: {path_csv}.csv")
	path_csv = path_csv+".csv"
	return path_csv, nome_csv 


		
def starter(api_id, api_hash,phone):
	# gestione della sessione, permette di usare diverse sessioni già presenti (nel caso di sessione con diversi numeri di telefono va cambiato nel file api)
	
	global client
	cartella = os.getcwd()
	sessioni_presenti = []
	for f in os.listdir(cartella):
		if f.endswith(".session"):
			sessioni_presenti.append(f)
	for i in range(0,len(sessioni_presenti)):
			print("sessioni presenti nella cartella: \n")
			print(sessioni_presenti[i].strip(".session"),"\n")
	sessione = str(input("scegli il nome della sessione, questa potrà essere usata per salvare l'accesso a telegram: "))
	#inizializzazione client e loop
	client = TelegramClient(sessione, api_id, api_hash)
	path_csv, nome_csv = client.loop.run_until_complete(main(phone))
	return path_csv, nome_csv

if __name__ == "__main__":
    starter(api_id, api_hash, phone)  