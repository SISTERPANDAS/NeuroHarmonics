const express = require('express');
const router = express.Router();
const communityController = require('../controllers/communityController');

router.get('/', communityController.getAllMessages);
router.post('/', communityController.postMessage);

module.exports = router;