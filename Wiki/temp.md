# BDMarket - Solution Design

## 1. Introduzione e contesto business

### 1.1 Obiettivi del progetto

L'obiettivo principale del progetto è migrare un'applicazione esistente ([bdo-market-app](https://github.com/guala01/bdo-market-app)) per il monitoraggio del mercato di Black Desert Online in un'architettura distribuita eseguibile su cloud. Le richieste chiave dei committenti:

- __RC1__ Trasformare l'applicativo monolitico esistente in un'applicazione distribuita su cloud
- __RC2__ Replicare le funzionalità esistenti nella prima fase di migrazione ed integrarle in secondo luogo
- __RC3__ Garantire che l'applicazione sia in grado di scalare in base al carico
- __RC4__ Implementare un sistema di notifica in tempo reale per gli oggetti di alto valore

### 1.2 Contesto business

BDMarket opera nel contesto del mercato virtuale di Black Desert Online, un gioco multiplayer online. Il sistema si interfaccia con diversi componenti:

Ruoli e funzionalità principali:
- Giocatori di Black Desert Online:
  - Visualizzazione dei dati di transazione degli oggetti a valuta reale
  - Registrazione per notifiche su oggetti specifici
  - Accesso alla dashboard personale delle registrazioni
- API non ufficiali del mercato di Black Desert Online:
  - Fonte primaria dei dati sulle transazioni e gli oggetti
- Amministratori del sistema:
  - Gestione degli script di scraping
  - Monitoraggio delle performance del sistema
- Bot Discord:
  - Gestione delle registrazioni degli utenti per le notifiche
  - Invio di notifiche agli utenti

Integrazioni esterne:
- Discord OAuth: Per l'autenticazione degli utenti
- Servizio email: Per l'invio di notifiche alternative

L'idea e' che il nuovo sistema distribuito su cloud manterrà le sue funzionalità, migliorando la scalabilità e l'efficienza delle operazioni di scraping e notifica.

## 2. Requisiti

### 2.1 Requisiti Funzionali

- __RF1__: Visualizzazione dati di mercato
  - Il sistema deve mostrare i dati delle transazioni degli oggetti a valuta reale del mercato di Black Desert Online.
  - Gli utenti devono poter visualizzare statistiche come il numero di vendite ed il tempo medio per vincere un preorder.
- __RF2__: Autenticazione utenti
  - Gli utenti devono autenticarsi tramite Discord OAuth.
  - Solo gli utenti whitelistati possono avere accesso al sistema.
- __RF3__: Registrazione per notifiche
  - Gli utenti devono poter registrarsi per ricevere notifiche su oggetti specifici.
  - La registrazione deve essere possibile tramite comandi del bot Discord.
- __RF4__: Sistema di notifiche
  - Il sistema deve inviare notifiche agli utenti quando un oggetto registrato appare nella lista d'attesa del mercato.
  - Le notifiche devono essere inviate sia tramite Discord che via email (se fornita dall'utente).
- __RF5__: Scraping dati di mercato
  - Il sistema deve eseguire regolarmente lo scraping dei dati dal mercato di Black Desert Online.
  - I dati raccolti devono essere salvati nel database PostgreSQL.

### 2.2 Requisiti Non Funzionali

- __NFR1__: Architettura cloud
  - Il sistema deve essere eseguito interamente su infrastruttura cloud.
- __NFR2__: Scalabilità
  - L'applicazione deve essere in grado di scalare in base al carico di lavoro.
- __NFR3__: Disponibilità
  - Il sistema deve avere una disponibilità 24/7.
- __NFR4__: Sicurezza
  - L'accesso ai dati deve essere limitato agli utenti autorizzati.
- __NFR5__: Performance
  - Le notifiche devono essere inviate entro 5 minuti dall'apparizione di un oggetto nella lista d'attesa.
  - Il database deve essere aggiornato quanto piu' di frequente possibile per avere maggior precisione nei dati.
- __NFR6__: Logging e monitoraggio
  - Il sistema deve implementare logging completo utilizzando Grafana.
  - Deve essere possibile monitorare le performance e lo stato del sistema in tempo reale.

### 2.3 Vincoli

- __V1__: Il sistema deve replicare le funzionalità esistenti dell'applicazione monolitica.
- __V2__: Lo scraping dei dati deve rispettare i limiti di rate dell'API di Black Desert Online per evitare il ban.

### 2.4 Assunzioni

- __A1__: Si assume che il carico di lavoro iniziale sarà simile a quello dell'applicazione esistente.
- __A2__: L'API di Black Desert Online manterrà la sua struttura attuale.
- __A3__: Discord continuerà a supportare l'OAuth per l'autenticazione.

Questi sono i vincoli, restrizioni e requisiti che il nostro progetto deve seguire.

# 3. Contesto Tecnico

## 3.1 Architettura di Riferimento

![Architettura](https://github.com/user-attachments/assets/66dcb8ee-f6f9-45f6-9671-dbd762029a4f)


## 3.2 Building Blocks

### SPA (Single Page Application)
- **Express App**: Server Node.js gestisce le richieste HTTP e serve l'applicazione frontend.
- **Frontend**: Implementato con HTML, JavaScript e EJS per il rendering lato server.
- **Discord OAuth**: Gestisce l'autenticazione degli utenti tramite Discord.
- **Logger(JS)**: Implementa il logging per la SPA utilizzando Grafana Loki.

### Scraping Scripts
- **scw-scrape.py**: Script Python per lo scraping iniziale degli ID degli oggetti dal marketplace.
- **newmain.py**: Script principale per lo scraping dei dati di mercato e l'inserimento nel database.
- **waitinglist.py**: Script per il monitoraggio della lista d'attesa del mercato.
- **Logger (Python)**: Implementa il logging per la SPA utilizzando Grafana Loki.

![Scraping Sequence Diagram](https://github.com/user-attachments/assets/81a969da-7227-4a95-9188-79bebcc19352)

### Discord Bot
- **finalbot.py**: Bot Discord per la gestione delle registrazioni e l'invio di notifiche agli utenti.
- **Logger**: Sistema di logging specifico per il bot Discord.

![Registrations Sequence Diagram](https://github.com/user-attachments/assets/48252c15-5abb-4b0b-a987-3eea27353fd4)

### Email Service
- **Spring Boot App**: Applicazione Java per la gestione del servizio email.
- **Kafka Consumer**: Consumatore Kafka per la ricezione degli aggiornamenti della lista d'attesa.
- **SpringBoot Email Sender**: Componente per l'invio di email agli utenti registrati.

![Notification Sequence Diagram](https://github.com/user-attachments/assets/bd83ddd7-3758-4c6a-bd2a-9b59a2a9206d)

### Database
- **PostgreSQL**: Database relazionale per la memorizzazione dei dati di mercato e delle informazioni degli utenti.

### Object Storage
- **Scaleway S3**: Servizio di object storage compatibile con S3 per la memorizzazione di file JSON e altri dati non strutturati.

### Message Broker
- **Kafka**: Sistema di messaggistica distribuito per la gestione degli eventi e la comunicazione tra componenti.

### Logging e Monitoring
- **Grafana Loki**: Piattaforma per la raccolta e l'analisi dei log da tutti i componenti del sistema.

# 4. Deployment Model

Il modello di deployment di BDMarket sfrutta una combinazione di servizi cloud e container per garantire scalabilità, flessibilità e facilità di gestione. Di seguito sono descritti i principali componenti e la loro distribuzione:

![Deployment diagram](https://github.com/user-attachments/assets/56ae77b1-31a8-45ad-bb71-880bdf093c6d)

## 4.1 Servizi Cloud

### Scaleway
- **Serverless Jobs**: Utilizzati per gli script di scraping.
  - bdo-ids-scraper: Esegue lo scrape degli ID degli oggetti (cron: 0 0 * * *).
  - bdo-main-scraper: Esegue lo scraping principale del marketplace (cron: 0 * * * *).
  - bdo-wlist-scraper: Esegue lo scrape della waitinglist (cron: */7 * * * *).
- **Serverless Container**: Ospita la SPA.
- **Object Storage**: Utilizzato per la memorizzazione di file JSON e altri dati.
- **Secrets Management**: Gestisce le chiavi e i token necessari per l'accesso ai vari servizi.

### pgEdge
- Hosting del database PostgreSQL.
- Replicato in 3 nodi.

## 4.2 Macchina Virtuale

Una macchina virtuale ospita i seguenti servizi:
- **Kafka**: Message broker per la gestione degli eventi.
- **Zookeeper**: Necessario per il funzionamento di Kafka.
- **Email Service**: Container Spring Boot per l'invio di email.
- **Discord Bot**: Container Python per il bot Discord.

## 4.3 Docker Compose

Un file docker-compose.yml gestisce i servizi sulla macchina virtuale, includendo Zookeeper, Kafka, e l'applicazione email.

## 4.4 Dominio e DNS

- Dominio registrato: bdomarket.xyz
- Configurazione DNS: Record CNAME a root che punta all'endpoint Scaleways della SPA.

## 4.5 Deployment Workflow

1. Gli script di scraping vengono deployati come Serverless Jobs su Scaleway.
2. La SPA viene deployata come Serverless Container su Scaleway.
3. Il database viene creato e popolato su pgEdge.
4. I servizi Kafka, Email e Discord Bot vengono avviati sulla macchina virtuale tramite Docker Compose.
5. Il dominio viene configurato per puntare al Serverless Container della SPA.
