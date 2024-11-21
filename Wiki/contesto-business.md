# Contesto ed ambito business

## Diagramma del contesto business per l'AS IS
Il sistema attualmente in esecuzione può essere inquadrato all'interno del seguente contesto business.


![](immagini/contesto-business-as-is.png)

Da una analisi di alto livello e di indagine solamente sulla GUI, unitamente alle interviste interbe condotte in azienda sono emersi i seguenti ruoli d'uso e le rispettive macro funzionalità. 
- __Consumer Finale__: il consumer finale rappresenta il cliente che effettuerà gli ordini per acquistare la merce dal sistema. Tra le operazioni che può fare il cliente finale ci sono:
  - Introduzione di un ordine
  - Introduzione di un'anagrafica
  - Visualizzazione dei prodotti
  - ...
- __Ammnistratore del sistema__: è il ruolo che consente, con massimi privilegi, di modificare i dati del sistema
  - Modifiche di ordini
  - ...
- __Customer Care__: è il ruolo che consente di dare assistenza al cliente, quindi può accedere ai suoi dati ed, eventualmente, modificarli.
  - Visualizzazione dei dati di un cliente
  - Visualizzazione degli ordini del cliente
  - ...
 
Non sono al momento previste integrazioni con altri sistemi esterni.


Il nuovo sistema dovrà fondamentalmente rispettare questo contesto business, ma l'applicazione verrà ristrutturata per essere distribuita ed eseguita su cloud.