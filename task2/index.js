const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const logger = require('./middleware/logger');
const postsRouter = require('./routes/posts');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(logger);

app.use('/posts', postsRouter);

const PORT = 3000;
app.listen(PORT, () => console.log(`Express Blog API running at http://localhost:${PORT}`));