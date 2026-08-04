const axios = require('axios');
const Conversation = require('../models/Conversation');

// @desc    Process question via FastAPI AI service, persist conversation & return answer to React
// @route   POST /ask or POST /api/ask
// @access  Private (JWT Validated)
const askQuestion = async (req, res) => {
  try {
    const { documentId, question } = req.body;

    // 1. Validate payload
    if (!documentId || !question) {
      return res.status(400).json({ message: 'Please provide both documentId and question' });
    }

    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';

    try {
      // 2. Send request to FastAPI AI service /query
      const aiResponse = await axios.post(`${aiServiceUrl}/query`, {
        document_id: documentId,
        query: question,
      });

      // 3. Receive answer & retrieved sections
      if (aiResponse.data && aiResponse.data.status === 'success') {
        const { answer, retrieved_sections } = aiResponse.data;

        // 4. Save conversation record in MongoDB
        const conversation = await Conversation.create({
          userId: req.user._id,
          documentId,
          question,
          answer,
          retrievedSections: retrieved_sections,
        });

        // 5. Return response to React
        return res.status(200).json({
          status: 'success',
          answer,
          retrievedSections: retrieved_sections,
          conversationId: conversation._id,
          timestamp: conversation.createdAt,
        });
      } else {
        return res.status(500).json({
          message: 'AI Service failed to generate answer',
        });
      }
    } catch (aiError) {
      console.error('FastAPI AI Service Query Error:', aiError.response ? aiError.response.data : aiError.message);
      return res.status(500).json({
        message: 'Error communicating with AI Service',
        error: aiError.response ? aiError.response.data : aiError.message,
      });
    }
  } catch (error) {
    console.error('Ask Controller Error:', error.message);
    return res.status(500).json({ message: error.message || 'Server Error' });
  }
};

// @desc    Get chat conversation history for a document
// @route   GET /history or GET /api/history
// @access  Private (JWT Validated)
const getHistory = async (req, res) => {
  try {
    const { documentId } = req.query;

    if (!documentId) {
      return res.status(400).json({ message: 'Please provide documentId as a query parameter' });
    }

    const history = await Conversation.find({
      userId: req.user._id,
      documentId,
    }).sort({ createdAt: 1 });

    return res.status(200).json({ history });
  } catch (error) {
    console.error('Get History Error:', error.message);
    return res.status(500).json({ message: error.message || 'Server Error' });
  }
};

module.exports = {
  askQuestion,
  getHistory,
};
