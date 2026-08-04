const axios = require('axios');
const Document = require('../models/Document');

// @desc    Upload PDF document and trigger AI processing
// @route   POST /upload or POST /api/upload
// @access  Private (JWT Required)
const uploadDocument = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'Please upload a PDF file' });
    }

    const { originalname, path: filePath } = req.file;

    // 1. Create document record in MongoDB with status PROCESSING
    const document = await Document.create({
      userId: req.user._id,
      paperName: originalname,
      filePath: filePath,
      status: 'PROCESSING',
    });

    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';

    try {
      // 2. Call FastAPI AI service /process-pdf
      const aiResponse = await axios.post(`${aiServiceUrl}/process-pdf`, {
        document_id: document._id.toString(),
        file_path: filePath,
      });

      if (aiResponse.data && aiResponse.data.status === 'success') {
        // 3. Update document status to COMPLETED
        document.status = 'COMPLETED';
        await document.save();

        return res.status(201).json({
          message: 'Document uploaded and processed successfully',
          document,
          aiResult: aiResponse.data,
        });
      } else {
        document.status = 'FAILED';
        await document.save();

        return res.status(500).json({
          message: 'AI Service failed to process PDF',
          document,
        });
      }
    } catch (aiError) {
      console.error('FastAPI AI Service Error:', aiError.response ? aiError.response.data : aiError.message);
      document.status = 'FAILED';
      await document.save();

      return res.status(500).json({
        message: 'Error communicating with AI Service',
        error: aiError.response ? aiError.response.data : aiError.message,
        document,
      });
    }
  } catch (error) {
    console.error('Upload Controller Error:', error.message);
    return res.status(500).json({ message: error.message || 'Server Error' });
  }
};

// @desc    Get user's uploaded documents
// @route   GET /documents or GET /api/documents
// @access  Private (JWT Required)
const getDocuments = async (req, res) => {
  try {
    const documents = await Document.find({ userId: req.user._id }).sort({ createdAt: -1 });
    return res.status(200).json({ documents });
  } catch (error) {
    console.error('Get Documents Error:', error.message);
    return res.status(500).json({ message: error.message || 'Server Error' });
  }
};

module.exports = {
  uploadDocument,
  getDocuments,
};
