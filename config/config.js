const dotenv = require('dotenv');
//const logger = require('./logger');


dotenv.config();
//console.log('Environment variables loaded from .env file');
//logger.info('Environment variables loaded from .env file');

//TODO add dev and prod environments
module.exports = {
  port: process.env.PORT,
  sessionSecret: process.env.SESSION_SECRET, 
  dbHost: process.env.DB_HOST,
  dbUser: process.env.DB_USER, 
  dbPassword: process.env.DB_PASSWORD, 
  dbName: process.env.DB_NAME,
  dbDialect: process.env.DB_DIALECT, //Squelize still gives dialect error on migration
  dbPort: process.env.DB_PORT,
  scalewayAccessKey: process.env.SCALEWAY_ACCESS_KEY,
  scalewaySecretKey: process.env.SCALEWAY_SECRET_KEY,
  cockpitTokenSecretKey: process.env.COCKPIT_TOKEN_SECRET_KEY,
  scalewayRegion: process.env.SCALEWAY_REGION,
  discordClientId: process.env.DISCORD_CLIENT_ID, 
  discordClientSecret: process.env.DISCORD_CLIENT_SECRET,
  discordCallbackUrl: process.env.DISCORD_CALLBACK_URL,
  dialect: 'postgres', //Prob useless
  whitelistedUsers: process.env.WHITELISTED_USERS ? process.env.WHITELISTED_USERS.split(',') : [] 
};