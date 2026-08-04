const express = require('express');
const router = express.Router();
const documentController = require('../controllers/documentController');
const authMiddleware = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

router.post('/upload', authMiddleware, upload.single('file'), documentController.uploadDocument);
router.get('/documents', authMiddleware, documentController.getDocuments);

module.exports = router;
