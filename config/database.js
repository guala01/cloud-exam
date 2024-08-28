const { Sequelize } = require('sequelize');
const config = require('./config');
const logger = require('./logger'); 

process.env.PGSSLMODE = 'require';

//logger.info('Database configuration:', config);

const sequelize = new Sequelize(
  config.dbName, 
  config.dbUser, 
  config.dbPassword, 
  {
    host: config.dbHost,
    port: config.dbPort,
    dialect: 'postgres',
    logging: false, // Ensure logger is correctly used (msg) => logger.info(msg)
    dialectOptions: {
      ssl: {
        require: true,
        rejectUnauthorized: false
      }
    }
  }
);

sequelize.authenticate()
  .then(() => {
    logger.info('Connection to the PostgreSQL database has been established successfully.');
  })
  .catch(err => {
    logger.error('Unable to connect to the database:', err);
  });

module.exports = sequelize;
