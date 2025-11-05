
const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

let posts = [];

router.post('/', (req, res) => {
    const { title, content } = req.body;
    const newPost = { id: uuidv4(), title, content, createdAt: new Date() };
    posts.push(newPost);
    res.status(201).json(newPost);
});

router.get('/', (req, res) => {
    let filteredPosts = posts;
    if (req.query.title) {
        filteredPosts = filteredPosts.filter(p => p.title.includes(req.query.title));
    }
    res.json(filteredPosts);
});

router.get('/:id', (req, res) => {
    const post = posts.find(p => p.id === req.params.id);
    if (!post) return res.status(404).json({ error: "Post not found" });
    res.json(post);
});

router.put('/:id', (req, res) => {
    const post = posts.find(p => p.id === req.params.id);
    if (!post) return res.status(404).json({ error: "Post not found" });
    post.title = req.body.title || post.title;
    post.content = req.body.content || post.content;
    res.json(post);
});

router.delete('/:id', (req, res) => {
    posts = posts.filter(p => p.id !== req.params.id);
    res.json({ message: "Post deleted" });
});

module.exports = router;
