# Secure Blog API

A comprehensive RESTful API for a blog platform built with Node.js, Express.js, and MongoDB. Features JWT-based authentication, role-based access control, and comprehensive security measures.

## 🚀 Features

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Admin and user roles with different permissions
- **Password Hashing** - Secure password storage using bcryptjs
- **Rate Limiting** - Protection against brute force and DDoS attacks
- **Input Validation** - Comprehensive data validation using express-validator
- **Security Headers** - Helmet.js for security headers
- **CORS Protection** - Configurable cross-origin resource sharing
- **MongoDB Integration** - Mongoose ODM for database operations
- **Search & Pagination** - Full-text search and paginated responses
- **Tag System** - Blog post categorization with tags
- **Error Handling** - Comprehensive error handling and logging

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Testing with Postman](#testing-with-postman)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)

## 🛠 Prerequisites

Before running this application, make sure you have the following installed:

- **Node.js** (v14.0.0 or higher)
- **npm** (v6.0.0 or higher)
- **MongoDB** (v4.0 or higher) - Local installation or MongoDB Atlas account

## 📦 Installation

1. **Extract the project files** or clone the repository:
   ```bash
   # If you have the ZIP file, extract it
   unzip secure-blog-api.zip
   cd secure-blog-api
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

## ⚙️ Configuration

Edit the `.env` file with your specific configuration:

### Required Configuration

```env
# Server Configuration
NODE_ENV=development
PORT=5000
HOST=0.0.0.0

# Database Configuration (REQUIRED)
MONGODB_URI=mongodb://localhost:27017/secure-blog-api

# JWT Configuration (REQUIRED)
JWT_SECRET=your-super-secret-jwt-key-here-make-it-very-long-and-random
JWT_EXPIRES_IN=7d

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Generate a Secure JWT Secret

```bash
# Generate a random JWT secret
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

### Database Setup

#### Option 1: Local MongoDB
```bash
# Install MongoDB locally and start the service
# On macOS with Homebrew:
brew install mongodb-community
brew services start mongodb-community

# On Ubuntu:
sudo systemctl start mongod
```

#### Option 2: MongoDB Atlas (Cloud)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Get your connection string and update `MONGODB_URI` in `.env`

Example Atlas connection string:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/secure-blog-api?retryWrites=true&w=majority
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Start the server with nodemon (auto-restart on changes)
npm run dev
```

### Production Mode
```bash
# Start the server
npm start
```

### Verify Installation
Once the server is running, you should see output similar to:
```
✓ MongoDB Connected: localhost:27017
🚀 Server running in development mode
📡 Listening on http://0.0.0.0:5000
📚 API Documentation: http://0.0.0.0:5000/api
❤️  Health Check: http://0.0.0.0:5000/api/health

⚡ Ready to accept connections!
```

### Health Check
Visit `http://localhost:5000/api/health` to verify the server is running properly.

## 📖 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/auth/register` | Register a new user | Public |
| POST | `/auth/login` | Login user | Public |
| GET | `/auth/me` | Get current user profile | Private |
| PUT | `/auth/profile` | Update user profile | Private |
| POST | `/auth/change-password` | Change password | Private |

### Blog Post Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/posts` | Get all published posts | Public |
| GET | `/posts/my` | Get current user's posts | Private |
| GET | `/posts/:id` | Get single post by ID | Public |
| POST | `/posts` | Create new post | Private |
| PUT | `/posts/:id` | Update post | Private (Owner/Admin) |
| DELETE | `/posts/:id` | Delete post | Private (Owner/Admin) |
| GET | `/posts/tags/popular` | Get popular tags | Public |

### Request/Response Examples

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Login User
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Create Post
```bash
POST /api/posts
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "title": "My First Blog Post",
  "body": "This is the content of my blog post...",
  "status": "published",
  "tags": ["technology", "nodejs", "api"]
}
```

#### Get Posts with Pagination
```bash
GET /api/posts?page=1&limit=10&search=nodejs&tag=technology
```

## 🔐 Authentication

This API uses JWT (JSON Web Tokens) for authentication. Here's how it works:

1. **Register** or **Login** to receive a JWT token
2. **Include the token** in the Authorization header for protected routes:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

### Token Expiration
- Default expiration: 7 days
- Configure via `JWT_EXPIRES_IN` in `.env`

### Password Requirements
- Minimum 6 characters
- Must contain at least one uppercase letter, lowercase letter, and number

## 🛡 Rate Limiting

The API implements multiple layers of rate limiting:

- **Global**: 100 requests per 10 minutes per IP
- **Authentication**: 5 attempts per 15 minutes per IP
- **Registration**: 3 attempts per hour per IP
- **Post Creation**: 5 posts per 15 minutes per IP

## 🧪 Testing with Postman

### Import Postman Collection
1. Open Postman
2. Click "Import" button
3. Select the `Secure_Blog_API.postman_collection.json` file
4. The collection will be imported with all endpoints ready to test

### Authentication Flow
1. Use the "Register User" request to create a new account
2. Use the "Login User" request to get your JWT token
3. Copy the token from the response
4. In Postman, go to the collection settings and add the token to the Authorization header
5. Now you can test all protected endpoints

### Environment Variables (Optional)
Create a Postman environment with:
- `baseUrl`: `http://localhost:5000/api`
- `token`: `<your-jwt-token>`

## 🚀 Deployment

### Environment Variables for Production
```env
NODE_ENV=production
PORT=5000
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/secure-blog-api
JWT_SECRET=your-production-jwt-secret-very-long-and-secure
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
TRUST_PROXY=true
```

### Deployment Platforms

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set NODE_ENV=production
heroku config:set MONGODB_URI=your-mongodb-atlas-uri
heroku config:set JWT_SECRET=your-jwt-secret
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
railway login
railway init
railway add
railway deploy
```

#### DigitalOcean App Platform
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy directly from the dashboard

## 🔒 Security Considerations

### Implemented Security Measures
- **Helmet.js** - Security headers
- **CORS** - Cross-origin resource sharing protection
- **Rate Limiting** - Brute force attack prevention
- **Input Validation** - Data sanitization and validation
- **Password Hashing** - bcryptjs with salt rounds
- **JWT Tokens** - Secure authentication
- **Environment Variables** - Sensitive data protection

### Additional Recommendations for Production
1. **Use HTTPS** - Always use SSL/TLS in production
2. **Database Security** - Enable MongoDB authentication
3. **Firewall Rules** - Restrict database access to application servers only
4. **Monitoring** - Implement logging and monitoring (Winston, Morgan)
5. **Backup Strategy** - Regular database backups
6. **Update Dependencies** - Keep dependencies up to date

## 📁 Project Structure

```
secure-blog-api/
├── models/              # Mongoose models
│   ├── User.js         # User model with authentication
│   └── Post.js         # Blog post model
├── routes/              # Express routes
│   ├── auth.js         # Authentication routes
│   └── posts.js        # Blog post routes
├── middleware/          # Custom middleware
│   └── auth.js         # JWT authentication middleware
├── config/              # Configuration files (empty for now)
├── server.js           # Main application entry point
├── package.json        # Dependencies and scripts
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    // Validation errors (if applicable)
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Error
```
Error: connect ECONNREFUSED 127.0.0.1:27017
```
**Solution**: Make sure MongoDB is running locally or check your Atlas connection string.

#### JWT Secret Error
```
Error: secretOrPrivateKey has a value of undefined
```
**Solution**: Set the `JWT_SECRET` in your `.env` file.

#### Port Already in Use
```
Error: listen EADDRINUSE :::5000
```
**Solution**: Change the port in `.env` or stop the process using port 5000.

### Debug Mode
Set `NODE_ENV=development` in `.env` to see detailed error stack traces.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Express.js team for the excellent web framework
- MongoDB team for the powerful database
- All the open-source contributors who made the dependencies possible

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the API documentation
3. Test with the provided Postman collection
4. Ensure all environment variables are set correctly

---

**Happy coding! 🚀**
