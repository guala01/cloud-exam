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

/*if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
      format: winston.format.simple(),
    }));
  }*/
  
module.exports = logger;
