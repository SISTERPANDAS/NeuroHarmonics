require('dotenv').config();
const express = require('express');
const db = require('./config/db'); // this will initiate connection

const app = express();
const PORT = process.env.PORT || 5000;

// middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// routes
app.use('/api/users', require('./routes/users'));
app.use('/api/admins', require('./routes/admin'));
app.use('/api/community', require('./routes/community'));
app.use('/api/contacts', require('./routes/contact'));
app.use('/api/feedback', require('./routes/feedback'));

app.get('/', (req, res) => {
  res.json({ message: 'NeuroHarmonics API is running' });
});

app.listen(PORT, () => {
  console.log(`Server started on port ${PORT}`);
});