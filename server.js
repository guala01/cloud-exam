const express = require('express');
const session = require('express-session');
const path = require('path');
const passport = require('./config/auth'); 
const config = require('./config/config'); 
const sequelize = require('./config/database'); 
const authRoutes = require('./routes/authRoutes'); 
const dashboardRoutes = require('./routes/dashboardRoutes'); 
const apiRoutes = require('./routes/apiRoutes'); 
const loadRegistrations = require('./config/registrationMiddleware'); 
const logger = require('./config/logger');

const app = express();
const PORT = config.port;

logger.info('Starting server initialization');

logger.info('Configuring Express session');
app.use(session({
  secret: config.sessionSecret,
  resave: false,
  saveUninitialized: true,
}));

//logger.info('Initializing Passport');
app.use(passport.initialize());
app.use(passport.session());

//logger.info('Setting view engine and views directory');
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

//logger.info('Adding middleware');
app.use(loadRegistrations);

app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).send('An unexpected error occurred');
});

//logger.info('Setting up routes');
app.get('/', (req, res) => {
  logger.info('Rendering index page');
  res.render('index');
});

app.use('/', authRoutes);
app.use('/', dashboardRoutes);
app.use('/api', apiRoutes);

const { Item, MarketSnapshot, ItemTrade } = require('./models');

const syncAndStartServer = async (port, retries = 5) => {
  logger.info('Starting database synchronization and server startup');
  try {
    logger.info('Attempting to sync database');
    await Promise.race([
      sequelize.sync({ force: false }),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Database sync timeout')), 30000))
    ]);
    logger.info('Database synchronized successfully');
    
    app.listen(port, () => {
      console.log(`Server is running on port ${port}`);
      logger.info(`Server is running on port ${port}`);
    });
  } catch (err) {
    logger.error('Error during sync and start:', err);
    logger.error('Error details:', {
      message: err.message,
      stack: err.stack,
      code: err.code,
      name: err.name
    });
    if (err.code === 'EADDRINUSE' && retries > 0) {
      logger.warn(`Port ${port} is already in use. Trying another port...`);
      syncAndStartServer(port + 1, retries - 1);
    } else {
      logger.error('Unable to connect to the database or no retries left:', err);
      process.exit(1);
    }
  }
};

//logger.info('Initiating server startup process');
syncAndStartServer(PORT);

module.exports = { app };
