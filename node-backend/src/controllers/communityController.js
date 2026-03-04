const CommunityMessage = require('../models/CommunityMessage');

exports.getAllMessages = async (req, res) => {
  try {
    const msgs = await CommunityMessage.find({});
    res.json(msgs);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.postMessage = async (req, res) => {
  try {
    const msg = new CommunityMessage(req.body);
    await msg.save();
    res.status(201).json(msg);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
