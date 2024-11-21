@startuml
!theme aws-orange
actor User
actor DiscordUser as Discord
actor DiscordOAUTH


    rectangle SPA
    rectangle ScrapingScripts
    rectangle DiscordBot
    rectangle EmailService
    rectangle ObjectStorage


User --> SPA : Login
Discord --> DiscordBot : Registers for items
ScrapingScripts --> ObjectStorage : Saves Items
ScrapingScripts --> PostgreSQL : Stores Market Data
ScrapingScripts --> Kafka : Sends Updates
DiscordBot --> ObjectStorage : Reads/Writes Registrations
Kafka --> EmailService : Sends Messages
Kafka --> ObjectStorage : Reads Registrations
SPA --> DiscordOAUTH : Authenticates User
SPA --> PostgreSQL : Reads Data
DiscordOAUTH --> SPA : Authenticates User
@enduml


@startuml
!theme aws-orange
!define RECTANGLE class

actor User
actor DiscordUser as Discord

package BDMarket {
    package SPA {
        [Express]
        [Discord OAuth]
    }
    package ScrapingScripts {
        [Python Scripts]
    }
    package DiscordBot {
        [Python + Discord.py]
    }
    package EmailService {
        [SpringBoot]
        [Kafka]
    }
    package PostgreSQL {
        [Database]
    }
    package ObjectStorage {
        [Scaleway S3]
    }
    package Logging {
        [Grafana Loki]
    }
}


@enduml



@startuml
!theme aws-orange
!define RECTANGLE class

package SPA {
    [Express App]
    [Frontend (HTML, JS, EJS)]
    [Discord OAuth]
    [Logger]
}

package ScrapingScripts {
    [scw-scrape.py]
    [newmain.py]
    [waitinglist.py]
    [Logger (Python + Loki)]
}

package DiscordBot {
    [finalbot.py]
    [Logger]
}

package EmailService {
    [Spring Boot App]
    [Kafka Consumer]
    [SpringBoot Email Sender]
}


@enduml


//diragrammi nuovi
@startuml Deployment Diagram
!theme aws-orange

cloud "Scaleway" {
    [Serverless Jobs] as SJ
    [Serverless Container] as SC
    [Object Storage] as OS
    [Secrets Management] as SM
}

cloud "pgEdge" {
    database "PostgreSQL" as PG
}

node "Virtual Machine" {
    [Kafka] as KF
    [Zookeeper] as ZK
    [Email Service] as ES
    [Discord Bot] as DB
}

SJ --> OS : updates
SJ --> KF : sends updates
SC --> OS : reads from
SJ --> PG : writes to
SC --> PG : reads from
ES --> KF : consumes from
DB --> KF : consumes from
ZK --> KF : manages
@enduml


@startuml Scraping Process
!theme aws-orange

participant "Scraping Script" as SS
participant "BDO API" as API
participant "PostgreSQL" as PG
participant "Object Storage" as OS

SS -> API : Request market data
API --> SS : Return market data
SS -> PG : Insert market data
SS -> OS : Store JSON files
@enduml


@startuml Notification Process
!theme aws-orange

participant "Waiting List Script" as WL
participant "Kafka" as KF
participant "Discord Bot" as DB
participant "Object Storage" as OS
participant "Email Service" as ES
participant "User" as U

WL -> KF : Publish new item in waiting list
DB -> OS : Add user registration
KF -> ES : Consume message
ES -> OS : Check user registrations
ES -> U : Send email notification if registered
U -> DB : Receive Discord command
DB -> U : Respond to command
@enduml

//sequence diagrams

@startuml
!theme aws-orange

actor User
participant "Discord Bot" as DB
participant "Object Storage" as OS

User -> DB: Send registration command
DB -> DB: Validate command
DB -> OS: Store registration
OS --> DB: Confirm storage
DB --> User: Confirm registration
@enduml


@startuml Notification Process
!theme aws-orange

participant "Kafka" as KF
participant "Email Service" as ES
participant "Object Storage" as OS
participant "User" as U

KF -> ES: New item in waiting list
ES -> OS: Check user registrations
OS --> ES: Return matching registrations
ES -> ES: Generate notifications
ES -> U: Send email notifications

@enduml

//parte 3
@startuml BDMarket Architecture
!theme aws-orange
skinparam linetype ortho
skinparam rectangleBorderStyle plain
skinparam nodesep 300
skinparam ranksep 300

rectangle "Scaleway Cloud" {
    rectangle "SPA\n(Express + Frontend)" as SPA
    rectangle "Scraping Scripts" as Scripts
    rectangle "Object Storage" as S3
    database "PostgreSQL" as DB
}

rectangle "Virtual Machine" {
    rectangle "Kafka" as Kafka
    rectangle "Discord Bot" as Bot
    rectangle "Email Service" as Email
}

actor User
actor "BDO API" as API

User --> SPA : Accesses
SPA --> DB : Reads data
Scripts --> API : Scrapes data
Scripts --> DB : Writes data
Scripts --> S3 : Stores JSON
Scripts --> Kafka : Sends updates
Bot --> S3 : Manages registrations
Email --> Kafka : Consumes messages
Email --> S3 : Checks registrations
Email --> User : Sends notifications
Bot --> User : Sends notifications
@enduml