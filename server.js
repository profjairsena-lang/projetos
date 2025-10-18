const express = require('express');
const http = require('http');
const socketIO = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIO(server);

app.use(express.static('public')); // pasta onde ficará seu HTML + JS

io.on('connection', socket => {
    console.log('Novo jogador conectado');

    socket.on('jogada', data => {
        socket.broadcast.emit('jogada', data); // envia para o outro jogador
    });

    socket.on('disconnect', () => {
        console.log('Jogador desconectado');
    });
});

server.listen(3000, () => {
    console.log('Servidor rodando em http://localhost:3000');
});
