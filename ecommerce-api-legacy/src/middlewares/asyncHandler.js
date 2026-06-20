// Encapsula handlers assíncronos e encaminha rejeições ao error handler central.
// (Express 4 não captura erros de Promises automaticamente.)
const asyncHandler = (handler) => (req, res, next) =>
    Promise.resolve(handler(req, res, next)).catch(next);

module.exports = { asyncHandler };
