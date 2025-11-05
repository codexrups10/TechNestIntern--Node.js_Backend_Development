/**
 * Post Model
 * 
 * Defines the Post schema for MongoDB with Mongoose
 * Includes validation, user reference, and automatic timestamps
 */

const mongoose = require('mongoose');

// Post Schema Definition
const postSchema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, 'Title is required'],
    trim: true,
    minlength: [3, 'Title must be at least 3 characters long'],
    maxlength: [200, 'Title cannot exceed 200 characters']
  },
  body: {
    type: String,
    required: [true, 'Post body is required'],
    minlength: [10, 'Post body must be at least 10 characters long'],
    maxlength: [5000, 'Post body cannot exceed 5000 characters']
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'User reference is required']
  },
  status: {
    type: String,
    enum: ['draft', 'published', 'archived'],
    default: 'published'
  },
  tags: [{
    type: String,
    trim: true,
    lowercase: true
  }],
  readTime: {
    type: Number, // in minutes
    default: function() {
      // Calculate approximate read time (200 words per minute)
      const wordCount = this.body.split(' ').length;
      return Math.ceil(wordCount / 200);
    }
  }
}, {
  timestamps: true, // Adds createdAt and updatedAt fields automatically
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for better performance
postSchema.index({ user: 1, createdAt: -1 }); // For user's posts sorted by date
postSchema.index({ status: 1, createdAt: -1 }); // For published posts
postSchema.index({ tags: 1 }); // For tag-based queries
postSchema.index({ title: 'text', body: 'text' }); // For text search

// Virtual for excerpt (first 150 characters of body)
postSchema.virtual('excerpt').get(function() {
  if (this.body.length <= 150) return this.body;
  return this.body.substring(0, 150) + '...';
});

// Pre-save middleware to update readTime
postSchema.pre('save', function(next) {
  if (this.isModified('body')) {
    const wordCount = this.body.split(' ').length;
    this.readTime = Math.ceil(wordCount / 200) || 1;
  }
  next();
});

// Static method to get posts by user
postSchema.statics.findByUser = function(userId, options = {}) {
  const { status = 'published', limit = 10, skip = 0, sort = { createdAt: -1 } } = options;

  return this.find({ user: userId, status })
    .populate('user', 'email role createdAt')
    .sort(sort)
    .limit(limit)
    .skip(skip);
};

// Static method to get published posts with pagination
postSchema.statics.getPublishedPosts = function(options = {}) {
  const { limit = 10, skip = 0, sort = { createdAt: -1 } } = options;

  return this.find({ status: 'published' })
    .populate('user', 'email role createdAt')
    .sort(sort)
    .limit(limit)
    .skip(skip);
};

// Instance method to check if user can edit this post
postSchema.methods.canEdit = function(userId, userRole) {
  // Admin can edit any post, users can only edit their own posts
  return userRole === 'admin' || this.user.toString() === userId.toString();
};

module.exports = mongoose.model('Post', postSchema);
