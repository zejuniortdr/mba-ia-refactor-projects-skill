// Erro de aplicação com status HTTP — lançado pelos controllers/models.
class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.statusCode = statusCode;
    }
}

// Middleware de erro centralizado (substitui os try/catch duplicados do legado).
// Nunca expõe stack trace ao cliente.
function errorHandler(err, req, res, next) {
    if (err instanceof AppError) {
        return res.status(err.statusCode).send(err.message);
    }
    console.error(err.stack || err);
    return res.status(500).send('Erro interno do servidor');
}

// Handler para rotas não encontradas (404).
function notFoundHandler(req, res) {
    res.status(404).send('Recurso não encontrado');
}

module.exports = { AppError, errorHandler, notFoundHandler };
