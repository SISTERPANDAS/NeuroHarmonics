const mongoose = require('mongoose');

const feedbackSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.Mixed },
  rating: { type: Number, required: true },
  comment: { type: String },
  created_at: { type: Date, default: Date.now }
}, { collection: 'rfeedback' });

module.exports = mongoose.model('Feedback', feedbackSchema);