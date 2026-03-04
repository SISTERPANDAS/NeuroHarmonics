const mongoose = require('mongoose');
const dotenv = require('dotenv');

dotenv.config();

const MONGO_URI = process.env.MONGO_URI;
if (!MONGO_URI) {
  console.error('MONGO_URI not set in .env');
  process.exit(1);
}

// connect with options to use existing database without creating new collections
mongoose.connect(MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  dbName: 'neuroharmonics',
})
  .then(() => console.log('[+] Connected to MongoDB Atlas (neuroharmonics)'))
  .catch(err => {
    console.error('[-] MongoDB connection error:', err);
    process.exit(1);
  });

module.exports = mongoose;