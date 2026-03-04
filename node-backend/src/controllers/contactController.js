const ContactMessage = require('../models/ContactMessage');

exports.getAllContacts = async (req, res) => {
  try {
    const contacts = await ContactMessage.find({});
    res.json(contacts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.createContact = async (req, res) => {
  try {
    const contact = new ContactMessage(req.body);
    await contact.save();
    res.status(201).json(contact);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
