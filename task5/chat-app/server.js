const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const path = require("path");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Serve index.html from "public" folder
app.use(express.static(path.join(__dirname, "public")));

let chatHistory = {};

io.on("connection", (socket) => {
  console.log("✅ User connected:", socket.id);

  socket.on("joinRoom", (room) => {
    socket.join(room);
    console.log(`User joined room: ${room}`);

    if (chatHistory[room]) {
      socket.emit("history", chatHistory[room]);
    }
  });

  socket.on("message", ({ room, user, text }) => {
    const msg = { user, text, timestamp: new Date() };

    if (!chatHistory[room]) chatHistory[room] = [];
    chatHistory[room].push(msg);

    io.to(room).emit("message", msg);
  });

  socket.on("disconnect", () => {
    console.log("❌ User disconnected:", socket.id);
  });
});

server.listen(3000, () => {
  console.log("🚀 Server running at http://localhost:3000");
});
