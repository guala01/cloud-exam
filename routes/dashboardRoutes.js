const express = require('express');
const router = express.Router();
const { isAuthenticated } = require('../config/middlewares');
const { fetchDashboardData } = require('../utils/sqlQueries'); 
const logger = require('../config/logger');


//Route to render the dashboard view
router.get('/dashboard', isAuthenticated, (req, res) => {
  try {
    logger.info(`Rendering dashboard for user: ${req.user.id}`);
    const registrations = req.app.locals.registrations; 

    res.render('dashboard', { user: req.user, registrations: registrations[req.user.id] || [] });
  } catch (error) {
    logger.error('Error rendering dashboard:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});

//Route to fetch user registrations
router.get('/user-registrations', isAuthenticated, (req, res) => {
  try {
    const userId = req.user.id;
    const registrations = req.app.locals.registrations; 
    logger.info(`Checking registrations for user: ${userId}`);
    if (registrations[userId]) {
      res.json(registrations[userId]);
    } else {
      res.status(404).json({ message: 'User not registered' });
    }
  } catch (error) {
    logger.error('Error fetching user registrations:', error.message, error.stack);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});

module.exports = router;