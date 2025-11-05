const express = require('express');
const router = express.Router();
const Tag = require('../models/tag'); // make sure Tag model exists

// CREATE tag
router.post('/', async (req, res) => {
  try {
    const tag = new Tag(req.body);
    const savedTag = await tag.save();
    res.status(201).json(savedTag);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// READ all tags
router.get('/', async (req, res) => {
  try {
    const tags = await Tag.find();
    res.json(tags);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// READ single tag
router.get('/:id', async (req, res) => {
  try {
    const tag = await Tag.findById(req.params.id);
    if (!tag) return res.status(404).json({ message: 'Tag not found' });
    res.json(tag);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// UPDATE tag
router.put('/:id', async (req, res) => {
  try {
    const updatedTag = await Tag.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json(updatedTag);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// DELETE tag
router.delete('/:id', async (req, res) => {
  try {
    await Tag.findByIdAndDelete(req.params.id);
    res.json({ message: 'Tag deleted successfully' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
