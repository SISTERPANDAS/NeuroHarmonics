const mongoose = require('mongoose');

const communitySchema = new mongoose.Schema({
  username: { type: String, required: true },
  content: { type: String, required: true },
  timestamp: { type: Date, default: Date.now }
}, { collection: 'community_message' });

module.exports = mongoose.model('CommunityMessage', communitySchema);