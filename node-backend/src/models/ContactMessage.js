const mongoose = require('mongoose');

const contactSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.Mixed }, // could be ObjectId or null
  name: { type: String, required: true },
  email: { type: String, required: true },
  subject: { type: String },
  message: { type: String, required: true },
  is_resolved: { type: Boolean, default: false },
  admin_reply: { type: String, default: '' },
  timestamp: { type: Date, default: Date.now }
}, { collection: 'contact_message' });

module.exports = mongoose.model('ContactMessage', contactSchema);