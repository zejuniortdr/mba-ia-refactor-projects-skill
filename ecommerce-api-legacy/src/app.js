const express = require('express');
const { config } = require('./config/settings');
const database = require('./models/database');
const routes = require('./routes');
const { errorHandler, notFoundHandler } = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());
app.use(routes);
app.use(notFoundHandler);
app.use(errorHandler);

database.init()
    .then(() => {
        app.listen(config.port, () => {
            console.log(`LMS API rodando na porta ${config.port}...`);
        });
    })
    .catch((err) => {
        console.error('Falha ao inicializar o banco:', err);
        process.exit(1);
    });

module.exports = app;
