const express = require('express');
const router = express.Router();
const Comment = require('../models/comment'); // make sure Comment model exists

// CREATE comment
router.post('/', async (req, res) => {
  try {
    const comment = new Comment(req.body);
    const savedComment = await comment.save();
    res.status(201).json(savedComment);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// READ all comments
router.get('/', async (req, res) => {
  try {
    let query = Comment.find();

    // Optional filter by post
    if (req.query.post) query = query.where('post').equals(req.query.post);

    const comments = await query.populate('author', 'username email').sort({ createdAt: -1 });
    res.json(comments);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// READ single comment
router.get('/:id', async (req, res) => {
  try {
    const comment = await Comment.findById(req.params.id).populate('author', 'username email');
    if (!comment) return res.status(404).json({ message: 'Comment not found' });
    res.json(comment);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// UPDATE comment
router.put('/:id', async (req, res) => {
  try {
    const updatedComment = await Comment.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json(updatedComment);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// DELETE comment
router.delete('/:id', async (req, res) => {
  try {
    await Comment.findByIdAndDelete(req.params.id);
    res.json({ message: 'Comment deleted successfully' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
