const express = require('express');
const router = express.Router();
const Post = require('../models/post');

// CREATE post
router.post('/', async (req, res) => {
  try {
    const post = new Post(req.body);
    const savedPost = await post.save();
    res.status(201).json(savedPost);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// READ all posts
router.get('/', async (req, res) => {
  try {
    let query = Post.find();

    // Optional filters
    if (req.query.author) query = query.where('author').equals(req.query.author);
    if (req.query.category) query = query.where('category').equals(req.query.category);
    if (req.query.status) query = query.where('status').equals(req.query.status);

    const posts = await query
      .populate('author', 'username email')
      .populate('category', 'name')
      .populate('tags', 'name')
      .sort({ createdAt: -1 });

    res.json(posts);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// READ single post
router.get('/:id', async (req, res) => {
  try {
    const post = await Post.findById(req.params.id)
      .populate('author', 'username email')
      .populate('category', 'name')
      .populate('tags', 'name');

    if (!post) return res.status(404).json({ message: 'Post not found' });

    // Increment view count
    await post.incrementViews();

    res.json(post);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// UPDATE post
router.put('/:id', async (req, res) => {
  try {
    const post = await Post.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!post) return res.status(404).json({ message: 'Post not found' });
    res.json(post);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// DELETE post
router.delete('/:id', async (req, res) => {
  try {
    await Post.findByIdAndDelete(req.params.id);
    res.json({ message: 'Post deleted successfully' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
