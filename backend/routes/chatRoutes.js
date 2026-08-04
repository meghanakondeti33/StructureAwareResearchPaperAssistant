const express = require('express');
const router = express.Router();
const chatController = require('../controllers/chatController');
const authMiddleware = require('../middleware/authMiddleware');

router.post('/ask', authMiddleware, chatController.askQuestion);
router.get('/history', authMiddleware, chatController.getHistory);

module.exports = router;
