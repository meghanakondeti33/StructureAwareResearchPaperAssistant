const express = require('express');
const cors = require('cors');
const path = require('path');

const authRoutes = require('./routes/authRoutes');
const documentRoutes = require('./routes/documentRoutes');
const chatRoutes = require('./routes/chatRoutes');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve uploaded static files
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Mount routes at both / and /api for convenience
app.use('/', authRoutes);
app.use('/api', authRoutes);
app.use('/', documentRoutes);
app.use('/api', documentRoutes);
app.use('/', chatRoutes);
app.use('/api', chatRoutes);

app.get('/', (req, res) => {
  res.json({ message: "ResearchKnowledgeAssistant Backend API Gateway is operational" });
});

module.exports = app;
