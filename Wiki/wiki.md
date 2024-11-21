Lo scopo di questo progetto e' quello di migrare il codice di un'applicazione esistente in modo da 
renderne possibile il deploy in cloud.

L'applicazione e' composta da due parti, una serie di script che si occupano di fare uno scraping periodico di una api non documentata di una casa d'aste di un videogioco, e una interfaccia web che permette agli utenti di visualizzare gli oggetti in vendita.

Qui vediamo un diagramma generale per mostrare le varie componenti presenti.

![Screenshot 2024-09-10 214438](https://github.com/user-attachments/assets/469ec430-66bb-491d-9fa5-432f2f0a3c39)


# Parte Scraping(backend)

Essendo una API non documentata ed aperta al pubblico dobbiamo usare vari endpoint per riuscire a popolare un database con gli oggetti senza essere bannati dal server di gioco.

## Primo script
Per prima cosa ogni settimana in corrispondenza con gli aggiornamenti del gioco bisogna richiamare una api

`https://api.arsha.io/v2/{region}/pearlItems`

che ci ritorna una lista aggiornata di tutti gli oggetti esistenti che posso essere messi in vendita.
La logica di questa parte si trova sotto scripts/docker-scrape/scw-scrape.py
Questo script originalmente creava questa lista come file json "cleaned_data.json" nella cartella dell'app.

## Secondo script

Una volta ottenuti tutti gli oggetti possiamo andare a richiamare due api

`https://eu-trade.naeu.playblackdesert.com/Trademarket/GetWorldMarketSubList`
`https://eu-trade.naeu.playblackdesert.com/Trademarket/GetBiddingInfoList`

tramite queste riusciamo ad ottenere dati gli ID degli oggetti le informazioni su quante volte ogni oggetto e' stato venduto, quando e' stata l'ultima transazione e il numero di pre-ordini che ogni oggetto ha.
Questi dati vengono inseriti in un database postgres.
La logica di questa parte si trova sotto scripts/docker-main/newmain.py

## Terzo Script

La casa d'aste ha come funzionalita' il fatto di inserire gli oggetti di un certo valore in una coda che annuncia l'oggetto messo in vendita 15 minuti prima dando tempo ai giocatori di piazzare ordini.
Andiamo quindi a chiamare l'api

`https://eu-trade.naeu.playblackdesert.com/Trademarket/GetWorldMarketWaitList`

per avere la lista degli oggetti al momento in waitinglist.
La waiting list viene salvata come JSON `market_data.json`
La logica di questa parte si trova sotto scripts/docker-wlist/waitinglist.py

# Parte Frontend

Il frontend e' composto da una semplice SPA fatta in express e del semplice html+js usando templates ejs.
Per poter fare il login usiamo Discord OAUTH cosi' da poter avere accesso all'id utente e mostrare gli oggetti registrati.

# Notifiche utente

L'ultima funzionalita' del progetto e' quella che un utente puo' registrare un oggetto di interesse e ricevere notifiche quando questo appare nella waitinglist sopracitata.

Per implementare cio' usiamo un bot di discord che troviamo sotto scripts/docker-bot/finalbot.py
Usando la sintassi comune ai bot di discord possiamo andare a usare i comandi !register <id> <level> <email> per registrarsi ad un oggetto richiesto, la email e' facoltativa ma permette di ricevere le notifiche non solo tramite discord ping ma anche via email.
Per salvare le registrazioni usiamo un semplice file JSON.

Per implementare la notifica via email abbia invece un componente kafka in springboot che usa delle semplici credenziali di un qualunque provider email smtp per inviare le email quando la coda kafka si aggiorna e la registrazione di un utente e' presente nella waitinglist.
Il codice si trova sotto la cartella springboot.

Per iniziare la migrazione in cloud per prima cosa ho identificato i servizi di hosting necessari, essendo un progetto universitario abbiamo puntato su servizi che offrivano free tier.
Per l'hosting serverless e di oggetti ho usato scaleways, per il database pgEdge.

Vediamo come abbiamo deciso di scomporre il tutto

![Screenshot 2024-09-10 222825](https://github.com/user-attachments/assets/41f65d0d-dce8-404b-be31-f51cd5f8af80)


# Migrazione degli script Python per scraping

## Migrazione del database

Forse la parte piu' facile, in locale avevo gia' usato la libreria standard psycopg2 sia per python che per node che pgEdge utilizza nella sua documentazione, una volta cambiati gli endpoint e aggiunto un parametro aggiuntivo il database era up and running senza problemi.

## Migrazione degli oggetti JSON

Per migrare da creazione e lettura di file locali ad averli in cloud abbiamo utilizzato il servizio di Object Storage di scaleways, per interfacciarci usiamo la libreria standard di S3 utilizzando gli endpoint di scaleways al posto di aws visto che sono compatibili.

```python
s3_client = boto3.client(s3',
    region_name=SCALEWAY_REGION,
    endpoint_url=f'https://s3.{SCALEWAY_REGION}.scw.cloud',
    aws_access_key_id=SCALEWAY_ACCESS_KEY,
    aws_secret_access_key=SCALEWAY_SECRET_KEY
)
```

Per leggere i dati abbiamo quindi redefinito la funzione
```python
def read_cleaned_data():
    try:
        response = s3_client.get_object(Bucket=SCALEWAY_BUCKET_NAME, Key='cleaned_data.json')
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        logger.error(f"Error reading cleaned data from Scaleway Object Storage: {e}")
        return None
```
mentre per scrivere usiamo
```python
s3_client.put_object(
                Bucket=SCALEWAY_BUCKET_NAME,
                Key='cleaned_data.json',
                Body=json_data`
            )
```

## Migrazione del logging

Avendo un logging puramente locale tra console e file .log dobbiamo andare a portare il loggin su cloud, andiamo quindi a riscrivere la logica del logging per supportare Grafana usando il servizio di Scaleways Cockpit.

Abbiamo quindi usato la libreria standard Loki
```python
#Loki logging handler
handler = logging_loki.LokiHandler(
    url="https://logs.cockpit.fr-par.scw.cloud/loki/api/v1/push",
    tags={"job": "market-id-scraper"},
    auth=(SCALEWAY_SECRET_KEY, COCKPIT_TOKEN_SECRET_KEY),
    version="1",
)

logger = logging.getLogger("market-id-scraper")
print("Logger initialized.")
logger.addHandler(handler)
print("Logger handler added.")
logger.setLevel(logging.INFO)
print("Logger level set.")
```

A questo punto il logging che usavamo precendentemente che gia' usava la sintassi logger.info e logger.error senza bisogno di ulteriori cambiamenti inviera' i log direttamente a Scaleways.

A questo punto i nostri script sono pronti per essere messi in containers e deployati come container serverless su Scaleways, l'ultima cosa mancante era di includere i token come variabili d'ambiente per poter caricare le immagini su dockerhub e facilitare il deploy usando Scaleways secrets per la gestione dei token.

```python
#Scaleway regions
SCALEWAY_REGION = 'fr-par'  # or your preferred region
SCALEWAY_BUCKET_NAME = 'bdo-market-ids'

#Scaleway secrets
SCALEWAY_ACCESS_KEY = os.environ['SCALEWAY_ACCESS_KEY']
SCALEWAY_SECRET_KEY = os.environ['SCALEWAY_SECRET_KEY']
COCKPIT_TOKEN_SECRET_KEY = os.environ['COCKPIT_TOKEN_SECRET_KEY']
```

Una volta creati i dockerfile che troviamo nel repo questa parte e' fatta.

# Migrazione della SPA

Avendo gia' constatato che il database funzionava senza bisogno di ulteriori cambiamenti la parte piu' grande da cambiare per la SPA era il logging, abbiamo quindi dovuto scrivere una componente usando sempre loki per node
```javascript
const winston = require('winston');
const LokiTransport = require('winston-loki');
const config = require('./config');

//console.log('Logger configuration:', config);

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'bdo-market-app' },
  transports: [
    new LokiTransport({
      host: 'https://logs.cockpit.fr-par.scw.cloud',
      basicAuth: `${config.scalewaySecretKey}:${config.cockpitTokenSecretKey}`,
      labels: { job: 'bdo-market-app' },
      json: true,
      format: winston.format.json(),
      replaceTimestamp: true,
      onConnectionError: (err) => console.error(err)
    })
  ]
});

module.exports = logger;
```
che con la stessa logica di prima ha rimpiazzato i nostri logging direttamente senza bisogno di cambiare la sintassi per ogni file.
La nostra SPA era gia' configurata per usare le variabili d'ambiente quindi senza ulteriori cambiamenti e' stato possibile creare il dockerfile e caricare l'immagine su dockerhub.

# Migrazione della componente notifiche

Per migrare il bot di discord che consente la registrazione e notifiche abbiamo seguito gli stessi passi di prima cambiando il codice per consentire l'accesso a logging e Object Storage e creato il container allo stesso modo degli script di scraping.

Per migrare la componente kafka-springboot per il servizio di email abbiamo seguito la stessa strada generando un'immagine con gradle e creando il dockerfile dell'app.

Manca ora solo integrare lo script che esegue l'update della  waitinglist con kafka in modo che mandi la notifica quando avviene un push sul bucket.
```python
#Kafka configuration
KAFKA_BROKER = os.environ['KAFKA_BROKER']
KAFKA_TOPIC = 'waitinglist-updates'
producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])

producer.send(KAFKA_TOPIC, json.dumps(message).encode('utf-8'))
producer.flush()
```

## Migrazione db

Registriamo un account su pgedge e creiamo il db 
Usando 
```sql
pg_dump -U dbusername dbname > dbexport.pgsql
```
esportiamo il db dall'installazione locale poi usando le credenziali da pgedge migriamo il tutto
```sql
psql -h specially-nice-sponge.a1.pgedge.io -p 5432 -U app -d bdo_market_data < dbexport.pgsql
```

## Migrazione Kafka

Per kafka abbiamo bisogno di tenere su un container con coda kafka, un container con zookeeper per collegare il tutto con il nostro email service.
Per come funziona Scaleways non ho trovato modo una volta caricate le immagini di collegarle tra loro, la soluzione e' quindi quella di o usare un servizio kafka come confluent.io, ma richiedendo iscrizione con carta di credito ho optato per creare un docker compose ed hostarlo su macchina virtuale.

Per fare cio'
```yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  app:
    image: lolzyy/bdo-market-kafka-app
    depends_on:
      - kafka
    environment:
      SPRING_KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SCALEWAY_ACCESS_KEY: 
      SCALEWAY_SECRET_KEY: 
      SCALEWAY_REGION: 
      SCALEWAY_BUCKET_NAME: 
      MAIL_HOST: smtp.gmail.com
      MAIL_PORT: 587
      MAIL_USERNAME: 
      MAIL_PASSWORD: 
```
creiamo un compose del genere e una volta riempiti i campi con le varie key abbiamo la nostra app funzionante ed in attesa di ricevere updates

## Migrazione Scripts

Abbiamo selezionato scaleway quindi per prima cosa muoviamo i container docker degli script di scraping che abbiamo caricato su dockerhub su scaleways come Serverless Jobs

![image](https://github.com/user-attachments/assets/bde9fe9d-1811-420a-a2dd-a64917f20b46)

Vediamo i singoli job impostati:

**bdo-ids-scraper** esegue lo scrape degli id degli oggetti, questo richiede pochi secondi e puo' essere lanciato anche una sola volta al giorno, ci serve solo per avere sempre la lista degli oggetti aggiornata, impostiamo quindi 0 0 * * * come cron e assegnamo le key necessarie ed e' pronto.

![image](https://github.com/user-attachments/assets/cb65e643-1176-44a8-859d-b9e56185f74b)


**bdo-main-scraper** e' lo scraping principale, prende gli id dallo script precedente, esegue lo scraping del marketplace e carica i dati su postgres, questo lo vogliamo avviare una volta all'ora cosi' da avere piu' dati possibili, data la natura della api abbiamo un delay notevole tra le call per evitare di essere bannati, questo porta lo script a richiedere 15min circa per terminare il lavoro. Il costo medio di questa operazione porta circa a 4-5 euro mensili di costo.
Impostiamo come prima e lo script gira senza problemi.

**bdo-wlist-scraper** e' lo script che esegue lo scrape della waitilinglist ed informa la coda kafka, l'operazione in se richiede pochi secondi ma deve essere avviata ogni 7 minuti circa in modo da informare i giocatori in tempo. Impostiamo un cron */7 * * * * 

## Migrazione SPA

Come per il resto creiamo un container e lo deployamo su Scaleways come Serverless Container, impostiamo le env e possiamo fare il deploy, a questo punto avremo un endpoint fornito da scaleways funzionante.

![image](https://github.com/user-attachments/assets/33990033-d6c6-49a9-9c39-34d374d4fb43)


## Migrazione Bot

Il bot di Discord a causa della sua libreria di python non puo' funzionare in ambiente Serverless quindi una volta creato il suo container lo possiamo caricare nella macchina virtuale con il dockercompose di kafka.

## Aggiungere un Dominio all'app

Registriamo un dominio su un qualche servizio poi impostiamo un Record CNAME a root che punti al nostro endpoint fornito da Scaleways

![image](https://github.com/user-attachments/assets/8166203d-cf9d-4a90-b557-fc066e843f71)

poi da Scaleways ci rechiamo sul nostro container > Endpoints e aggiungiamo il nostro sito

![image](https://github.com/user-attachments/assets/8efc616c-b11b-4021-8c49-1183768898ca)

A questo punto se navighiamo su bdomarket.xyz visualizzeremo l'app correttamente