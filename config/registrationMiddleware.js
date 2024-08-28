const { S3Client, GetObjectCommand } = require('@aws-sdk/client-s3');
const logger = require('./logger');
const config = require('./config');
const { Readable } = require('stream');


// Configure AWS SDK for Scaleway
const s3Client = new S3Client({
  region: config.scalewayRegion,
  endpoint: `https://s3.${config.scalewayRegion}.scw.cloud`,
  credentials: {
    accessKeyId: config.scalewayAccessKey,
    secretAccessKey: config.scalewaySecretKey,
  },
  forcePathStyle: true, // Required for Scaleway
});

const BUCKET_NAME = 'bdo-market-ids';
const FILE_KEY = 'registrations.json';

const streamToString = (stream) =>
  new Promise((resolve, reject) => {
    const chunks = [];
    stream.on('data', (chunk) => chunks.push(chunk));
    stream.on('error', reject);
    stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
  });

const loadRegistrations = async (req, res, next) => {
  try {
    const params = {
      Bucket: BUCKET_NAME,
      Key: FILE_KEY,
    };

    const command = new GetObjectCommand(params);
    const data = await s3Client.send(command);
    const jsonData = await streamToString(data.Body);
    req.app.locals.registrations = JSON.parse(jsonData);
    logger.info('Registrations reloaded successfully from Scaleway Object Storage.');
  } catch (err) {
    logger.error('Error loading registrations.json from Scaleway Object Storage:', err);
  }
  next();
};

module.exports = loadRegistrations;