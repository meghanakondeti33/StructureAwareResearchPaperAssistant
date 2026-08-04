const mongoose = require('mongoose');

const conversationSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    documentId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Document',
      required: true,
    },
    question: {
      type: String,
      required: [true, 'Please add a question'],
    },
    answer: {
      type: String,
      required: true,
    },
    retrievedSections: [
      {
        sectionTitle: String,
        pageNumber: Number,
        snippet: String,
      },
    ],
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model('Conversation', conversationSchema);
