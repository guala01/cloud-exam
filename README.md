# BDMarket

BDMarket is a single-page application (SPA) designed to display Pearl Items (Real money value items) transaction data from the Black Desert Online marketplace. The application fetches data from a PostgreSQL database and is accessible only to whitelisted users through Discord OAuth authentication.

The second goal is to provide access to the marketplace registration queue that happens when items of value over 10b silvers are registered on the market. Using a discord bot users can register for an item and get notified ahead when the item is registered so they have 10~ minutes to place an order on it. The registration data can be added and removed via the discord bot and viewed on the SPA dashboard.

## Overview

The project employs a modern tech stack to deliver a responsive and secure user experience. Below are the primary technologies and architecture components used:

- **Backend**: Node.js with Express framework, Python for API scraping
- **Database**: PostgreSQL
- **Frontend**: Vanilla JavaScript with Bootstrap
- **Authentication**: Discord OAuth
- **Messaging**: Kafka
- **Email**: Springboot
- **Logging**: Grafana

The project uses 4 python scripts to scrape data from the marketplace and store it in the database. These scripts are to be run on a schedule to keep the data up to date.

scripts/docker-bot is a discord bot that is used to manage the registration queue. It is used to add and remove items from the queue and to view the queue.

scripts/docker-main is a python script that is used to scrape data from the marketplace and store it in the database. This is to be  run on a schedule to keep the data up to date but at the same time without getting rate limited by the game.

scripts/docker-scrape is a python script that is used to do populate a file with all the id's of the items on the market. This is to be called whenever the game is updated and new items are added to the market. (Which is usually every Thursday but may vary depending on the game update schedule).

scripts/docker-wlist is a python scripts that is used to fetch the waitinglist of the items on the market. This is to be called quite often so the player can be notified when an item is registered in real time.

sprinboot docker-compose.yml is used to run the kafka messaging that allows for the user to also be notified via email when an item hes registered to is posted on the waiting list.

db/query.sql contains the database schema and the query to fetch the data from the database.
db/importscript.py is a python script I used to import the data from the previous local Json file to the database.

Dockerfile in root folder is used to build the docker image for the SPA.

The goal of the project is to move the SPA to the cloud to a serverless infrastructure where possible. As such the project requires Scaleways token keys to handle logs and storage.

The database is a generic PostgreSQL database and is not specific to the project.

## Getting started with the SPA

### Requirements

Docker is required to run the project.
Scaleways token keys are required to run the project.

### Quickstart


1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd bdmarket
   ```

2. **Build all the docker files**

Using the provided docker files build the images under scripts/dcoker-* directories for the scraping.
Same for the SPA docker using Dockerfile in root folder.
Run the docker-compose.yml under springboot/ folder to build and ruin the springboot application.

3. **Set up the environment variables:**

The environment variables needed to run everything are
   For the SPA:
   ```plaintext
   PORT=3000
   SESSION_SECRET=your_session_secret
   DB_HOST=localhost
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=market_data_db
   DB_DIALECT=postgres
   DB_PORT=5432
   DISCORD_CLIENT_ID=your_discord_client_id
   DISCORD_CLIENT_SECRET=your_discord_client_secret
   DISCORD_CALLBACK_URL=http://localhost:3000/auth/callback
   WHITELISTED_USERS=comma_separated_list_of_discord_user_ids
   NODE_ENV=development
   COCKPIT_TOKEN_SECRET_KEY=your_cockpit_token_secret_key
   SCALEWAY_ACCESS_KEY=your_scaleway_access_key
   SCALEWAY_REGION=your_scaleway_region
   SCALEWAY_SECRET_KEY=your_scaleway_secret_key
   SESSION_SECRET=your_session_secret
   ```

For the scraping python scripts:
   ```plaintext
   COCKPIT_TOKEN_SECRET_KEY=your_cockpit_token_secret_key
   KAFKA_BROKER=your_kafka_broker_url
   SCALEWAY_ACCESS_KEY=your_scaleway_access_key
   SCALEWAY_SECRET_KEY=your_scaleway_secret_key
   PGPASSWORD=your_postgres_password
   TOKEN=your_discord_token
   ```

For the springboot application they are defined under springboot/docker-compose.yml


4. **Create the PostgreSQL database:**
To create the database locally run the following commands:
   ```bash
   sudo -u postgres psql -c
   CREATE DATABASE market_data_db;
   \c market_data_db;
   ```
   
   Use the query provided in `db/query.sql` to create the required tables.

Otherwise run the query after connecting to whatever cloud provider of choice.

5. **Run the project:**

Running the Docker under main folder will handle the SPA. Remember to add your discord id to the whitelisted users list.

