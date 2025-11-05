/**
 * Posts Routes
 * 
 * Handles blog post CRUD operations with authentication and validation
 * Includes pagination, search, and user ownership controls
 */

const express = require('express');
const { body, query, validationResult } = require('express-validator');
const rateLimit = require('express-rate-limit');
const Post = require('../models/Post');
const { authenticate, optionalAuth, adminOnly, checkOwnership } = require('../middleware/auth');

const router = express.Router();

// Rate limiting for post creation
const createPostLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 post creations per 15 minutes
  message: {
    success: false,
    message: 'Too many posts created. Please try again later.'
  }
});

// Validation rules
const createPostValidation = [
  body('title')
    .trim()
    .isLength({ min: 3, max: 200 })
    .withMessage('Title must be between 3 and 200 characters'),
  body('body')
    .trim()
    .isLength({ min: 10, max: 5000 })
    .withMessage('Post body must be between 10 and 5000 characters'),
  body('status')
    .optional()
    .isIn(['draft', 'published', 'archived'])
    .withMessage('Status must be one of: draft, published, archived'),
  body('tags')
    .optional()
    .isArray()
    .withMessage('Tags must be an array'),
  body('tags.*')
    .optional()
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Each tag must be between 1 and 50 characters')
];

const updatePostValidation = [
  body('title')
    .optional()
    .trim()
    .isLength({ min: 3, max: 200 })
    .withMessage('Title must be between 3 and 200 characters'),
  body('body')
    .optional()
    .trim()
    .isLength({ min: 10, max: 5000 })
    .withMessage('Post body must be between 10 and 5000 characters'),
  body('status')
    .optional()
    .isIn(['draft', 'published', 'archived'])
    .withMessage('Status must be one of: draft, published, archived'),
  body('tags')
    .optional()
    .isArray()
    .withMessage('Tags must be an array')
];

/**
 * @route   GET /posts
 * @desc    Get all published posts with pagination and search
 * @access  Public
 */
router.get('/', [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('Page must be a positive integer'),
  query('limit')
    .optional()
    .isInt({ min: 1, max: 50 })
    .withMessage('Limit must be between 1 and 50'),
  query('search')
    .optional()
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Search query must be between 1 and 100 characters'),
  query('tag')
    .optional()
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Tag must be between 1 and 50 characters'),
  query('author')
    .optional()
    .isMongoId()
    .withMessage('Author must be a valid user ID')
], optionalAuth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const { search, tag, author } = req.query;

    // Build query object
    let query = { status: 'published' };

    // Add search functionality
    if (search) {
      query.$text = { $search: search };
    }

    // Filter by tag
    if (tag) {
      query.tags = { $in: [tag.toLowerCase()] };
    }

    // Filter by author
    if (author) {
      query.user = author;
    }

    // Execute query with population and pagination
    const posts = await Post.find(query)
      .populate('user', 'email role createdAt')
      .sort(search ? { score: { $meta: 'textScore' } } : { createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .lean();

    // Get total count for pagination
    const totalPosts = await Post.countDocuments(query);
    const totalPages = Math.ceil(totalPosts / limit);

    res.json({
      success: true,
      message: 'Posts retrieved successfully',
      data: {
        posts,
        pagination: {
          currentPage: page,
          totalPages,
          totalPosts,
          hasNextPage: page < totalPages,
          hasPrevPage: page > 1
        }
      }
    });

  } catch (error) {
    console.error('Get posts error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * @route   GET /posts/my
 * @desc    Get current user's posts
 * @access  Private
 */
router.get('/my', authenticate, [
  query('status')
    .optional()
    .isIn(['draft', 'published', 'archived'])
    .withMessage('Status must be one of: draft, published, archived'),
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('Page must be a positive integer'),
  query('limit')
    .optional()
    .isInt({ min: 1, max: 50 })
    .withMessage('Limit must be between 1 and 50')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const status = req.query.status || 'published';

    const posts = await Post.findByUser(req.user._id, {
      status,
      limit,
      skip,
      sort: { createdAt: -1 }
    });

    const totalPosts = await Post.countDocuments({ 
      user: req.user._id, 
      status 
    });

    const totalPages = Math.ceil(totalPosts / limit);

    res.json({
      success: true,
      message: 'User posts retrieved successfully',
      data: {
        posts,
        pagination: {
          currentPage: page,
          totalPages,
          totalPosts,
          hasNextPage: page < totalPages,
          hasPrevPage: page > 1
        }
      }
    });

  } catch (error) {
    console.error('Get user posts error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * @route   GET /posts/:id
 * @desc    Get single post by ID
 * @access  Public
 */
router.get('/:id', optionalAuth, async (req, res) => {
  try {
    const post = await Post.findById(req.params.id)
      .populate('user', 'email role createdAt');

    if (!post) {
      return res.status(404).json({
        success: false,
        message: 'Post not found'
      });
    }

    // Check if post is published or user owns it or user is admin
    if (post.status !== 'published') {
      if (!req.user || 
          (req.user._id.toString() !== post.user._id.toString() && 
           req.user.role !== 'admin')) {
        return res.status(404).json({
          success: false,
          message: 'Post not found'
        });
      }
    }

    res.json({
      success: true,
      message: 'Post retrieved successfully',
      data: { post }
    });

  } catch (error) {
    console.error('Get post error:', error);

    if (error.name === 'CastError') {
      return res.status(400).json({
        success: false,
        message: 'Invalid post ID format'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * @route   POST /posts
 * @desc    Create new post
 * @access  Private
 */
router.post('/', authenticate, createPostLimiter, createPostValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { title, body, status = 'published', tags = [] } = req.body;

    // Process tags (convert to lowercase and remove duplicates)
    const processedTags = [...new Set(
      tags.map(tag => tag.toLowerCase().trim())
        .filter(tag => tag.length > 0)
    )];

    const post = new Post({
      title,
      body,
      user: req.user._id,
      status,
      tags: processedTags
    });

    await post.save();
    await post.populate('user', 'email role createdAt');

    res.status(201).json({
      success: true,
      message: 'Post created successfully',
      data: { post }
    });

  } catch (error) {
    console.error('Create post error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * @route   PUT /posts/:id
 * @desc    Update post
 * @access  Private (Owner or Admin)
 */
router.put('/:id', authenticate, checkOwnership(Post), updatePostValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { title, body, status, tags } = req.body;
    const post = req.resource; // Set by checkOwnership middleware

    // Update fields if provided
    if (title !== undefined) post.title = title;
    if (body !== undefined) post.body = body;
    if (status !== undefined) post.status = status;
    if (tags !== undefined) {
      post.tags = [...new Set(
        tags.map(tag => tag.toLowerCase().trim())
          .filter(tag => tag.length > 0)
      )];
    }

    await post.save();
    await post.populate('user', 'email role createdAt');

    res.json({
      success: true,
      message: 'Post updated successfully',
      data: { post }
    });

  } catch (error) {
    console.error('Update post error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * @route   DELETE /posts/:id
 * @desc    Delete post
 * @access  Private (Owner or Admin)
 */
router.delete('/:id', authenticate, checkOwnership(Post), async (req, res) => {
  try {
    const post = req.resource; // Set by checkOwnership middleware
    await post.deleteOne();

    res.json({
      success: true,
      message: 'Post deleted successfully'
    });

  } catch (error) {
    console.error('Delete post error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * @route   GET /posts/tags/popular
 * @desc    Get popular tags
 * @access  Public
 */
router.get('/tags/popular', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 20;

    // Aggregate to get popular tags
    const popularTags = await Post.aggregate([
      { $match: { status: 'published' } },
      { $unwind: '$tags' },
      { $group: { _id: '$tags', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: limit },
      { $project: { tag: '$_id', count: 1, _id: 0 } }
    ]);

    res.json({
      success: true,
      message: 'Popular tags retrieved successfully',
      data: { tags: popularTags }
    });

  } catch (error) {
    console.error('Get popular tags error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

module.exports = router;
