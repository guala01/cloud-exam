# Architettura


## Architettura logica
Qui di seguto si riporta il diagramma architetturale della soluzione target

![](immagini/architettura.png)

__NOTA__: il presente diagramma è da considerarsi a titolo di esempio e non riporta il diagramma completo della soluzione. Per sistemi molto complessi potrebbero essere necessari più di un diagramma con visualizzazioni di approfondimento su singoli blocchi.

## Elenco delle componenti

| Componente | Descrizione | Dipendenze |
|------------|-------------|------------|
| Database Anagrafiche | È il database che conterrà i dati delle anagrafiche | _Nessuna_ |
| Anagrafica Base | .... | Database Anagrafiche, Broker eventi, ... |
| ... | ... |... |


## Tecnologie e servizi
Di seguito si descrivono brevemente le tecnologie utilizzate indicando per ogni componente come sono utilizzate.

| Tecnologia | Descrizione | Componenti |
|------------|-------------|------------|
| Springboot | Framework Java per lo sviluppo di microservizi | Ordini, Orchestratore ordini | 
| Amazon S3      | Object Storage utilizzato per il salvattaggio delle immagini | Immagini Prodotti, Immagini Anagrafiche |
| Minio          | Object Storage compatibile con Amazon S3, ma utilizzato per gli ambienti di sviluppo in locale | Immagini Prodotti in DEV, Immagini Anagrafiche in DEV |
| .... |.... |...| 



