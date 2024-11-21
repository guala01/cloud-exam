# BDMarket - Solution Design

## 1. Introduzione e contesto business

### 1.1 Obiettivi del progetto

L'obiettivo principale di BDMarket è migrare un'applicazione esistente per il monitoraggio del mercato di Black Desert Online in un'architettura distribuita eseguibile su cloud. Le richieste chiave del committente includono:

- __RC1__ Trasformare l'applicativo monolitico esistente in un'applicazione distribuita su cloud
- __RC2__ Replicare le funzionalità esistenti nella prima fase di migrazione
- __RC3__ Garantire che l'applicazione sia in grado di scalare in base al carico
- __RC4__ Implementare un sistema di notifica in tempo reale per gli oggetti di alto valore

### 1.2 Contesto business

BDMarket opera nel contesto del mercato virtuale di Black Desert Online, un gioco multiplayer online. Il sistema si interfaccia con diversi attori e sistemi:

Ruoli e funzionalità principali:
- Giocatori di Black Desert Online:
  - Visualizzazione dei dati di transazione degli oggetti Pearl
  - Registrazione per notifiche su oggetti specifici
  - Accesso alla dashboard personale
- API del mercato di Black Desert Online:
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

Il nuovo sistema distribuito su cloud manterrà queste relazioni di business, migliorando la scalabilità e l'efficienza delle operazioni di scraping e notifica.

## 2. Requisiti

### 2.1 Requisiti Funzionali

- __RF1__: Visualizzazione dati di mercato
  - Il sistema deve mostrare i dati delle transazioni degli oggetti Pearl del mercato di Black Desert Online.
  - Gli utenti devono poter visualizzare statistiche come il numero di vendite, l'ultima transazione e il numero di pre-ordini per ogni oggetto.
- __RF2__: Autenticazione utenti
  - Gli utenti devono autenticarsi tramite Discord OAuth.
  - Solo gli utenti whitelistati devono avere accesso al sistema.
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
  - Tutte le comunicazioni devono essere crittografate.
  - L'accesso ai dati sensibili deve essere limitato agli utenti autorizzati.
- __NFR5__: Performance
  - Le notifiche devono essere inviate entro 5 minuti dall'apparizione di un oggetto nella lista d'attesa.
  - La dashboard deve caricarsi entro 3 secondi.
- __NFR6__: Logging e monitoraggio
  - Il sistema deve implementare logging completo utilizzando Grafana Loki.
  - Deve essere possibile monitorare le performance e lo stato del sistema in tempo reale.

### 2.3 Vincoli

- __V1__: Il sistema deve replicare le funzionalità esistenti dell'applicazione monolitica.
- __V2__: Lo scraping dei dati deve rispettare i limiti di rate dell'API di Black Desert Online per evitare il ban.

### 2.4 Assunzioni

- __A1__: Si assume che il carico di lavoro iniziale sarà simile a quello dell'applicazione esistente.
- __A2__: L'API di Black Desert Online manterrà la sua struttura attuale.
- __A3__: Discord continuerà a supportare l'OAuth per l'autenticazione.

Questa struttura dei requisiti fornisce una panoramica completa delle funzionalità, delle prestazioni e dei vincoli del sistema BDMarket, allineandosi con gli obiettivi del progetto e il contesto di business precedentemente definiti.

# 3. Contesto Tecnico

## 3.1 Architettura di Riferimento

![Architettura di Riferimento](immagini/architettura.png)

L'architettura di BDMarket è progettata per essere distribuita e scalabile, sfruttando servizi cloud per garantire alta disponibilità e performance. 

## 3.2 Building Blocks

### SPA (Single Page Application)
- **Express App**: Server Node.js che gestisce le richieste HTTP e serve l'applicazione frontend.
- **Frontend**: Implementato con HTML, JavaScript e EJS per il rendering lato server.
- **Discord OAuth**: Gestisce l'autenticazione degli utenti tramite Discord.
- **Logger**: Implementa il logging per la SPA utilizzando Grafana Loki.

### Scraping Scripts
- **scw-scrape.py**: Script Python per lo scraping iniziale degli ID degli oggetti dal marketplace.
- **newmain.py**: Script principale per lo scraping dei dati di mercato e l'inserimento nel database.
- **waitinglist.py**: Script per il monitoraggio della lista d'attesa del mercato.
- **Logger (Python + Loki)**: Sistema di logging per gli script di scraping.

### Discord Bot
- **finalbot.py**: Bot Discord per la gestione delle registrazioni e l'invio di notifiche agli utenti.
- **Logger**: Sistema di logging specifico per il bot Discord.

### Email Service
- **Spring Boot App**: Applicazione Java per la gestione del servizio email.
- **Kafka Consumer**: Consumatore Kafka per la ricezione degli aggiornamenti della lista d'attesa.
- **SpringBoot Email Sender**: Componente per l'invio di email agli utenti registrati.

### Database
- **PostgreSQL**: Database relazionale per la memorizzazione dei dati di mercato e delle informazioni degli utenti.

### Object Storage
- **Scaleway S3**: Servizio di object storage compatibile con S3 per la memorizzazione di file JSON e altri dati non strutturati.

### Message Broker
- **Kafka**: Sistema di messaggistica distribuito per la gestione degli eventi e la comunicazione tra componenti.

### Logging e Monitoring
- **Grafana Loki**: Piattaforma per la raccolta e l'analisi dei log da tutti i componenti del sistema.

Questa architettura permette a BDMarket di operare in modo distribuito, scalabile e resiliente, soddisfacendo i requisiti di performance e disponibilità richiesti dal progetto.

# 4. Deployment Model

Il modello di deployment di BDMarket sfrutta una combinazione di servizi cloud e container per garantire scalabilità, flessibilità e facilità di gestione. Di seguito sono descritti i principali componenti e la loro distribuzione:

## 4.1 Servizi Cloud

### Scaleway
- **Serverless Jobs**: Utilizzati per gli script di scraping.
  - bdo-ids-scraper: Esegue lo scrape degli ID degli oggetti (cron: 0 0 * * *).
  - bdo-main-scraper: Esegue lo scraping principale del marketplace (cron: ogni ora).
  - bdo-wlist-scraper: Esegue lo scrape della waitinglist (cron: */7 * * * *).
- **Serverless Container**: Ospita la SPA.
- **Object Storage**: Utilizzato per la memorizzazione di file JSON e altri dati.
- **Secrets Management**: Gestisce le chiavi e i token necessari per l'accesso ai vari servizi.

### pgEdge
- Hosting del database PostgreSQL.

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
- Configurazione DNS: Record CNAME a root che punta all'endpoint Scaleway della SPA.

## 4.5 Deployment Workflow

1. Gli script di scraping vengono deployati come Serverless Jobs su Scaleway.
2. La SPA viene deployata come Serverless Container su Scaleway.
3. Il database viene creato e popolato su pgEdge.
4. I servizi Kafka, Email e Discord Bot vengono avviati sulla macchina virtuale tramite Docker Compose.
5. Il dominio viene configurato per puntare al Serverless Container della SPA.

Questo modello di deployment permette a BDMarket di sfruttare i vantaggi del cloud computing, mantenendo al contempo il controllo su componenti critici come il message broker e il bot Discord.

