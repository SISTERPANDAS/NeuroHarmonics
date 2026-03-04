const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, default: 'user' },
  status: { type: String, default: 'active' },
  created_at: { type: Date, default: Date.now },
  avatar: { type: String, default: '' }
}, { collection: 'users' });

module.exports = mongoose.model('User', userSchema);