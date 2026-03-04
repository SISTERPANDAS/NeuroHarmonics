const Feedback = require('../models/Feedback');

exports.getAllFeedback = async (req, res) => {
  try {
    const items = await Feedback.find({});
    res.json(items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.createFeedback = async (req, res) => {
  try {
    const fb = new Feedback(req.body);
    await fb.save();
    res.status(201).json(fb);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
