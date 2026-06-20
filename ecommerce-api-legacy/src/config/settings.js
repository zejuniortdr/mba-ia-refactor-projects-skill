// Carrega variáveis de ambiente do .env (se existir) sem quebrar caso o pacote falhe.
try {
    require('dotenv').config();
} catch (_) {
    // dotenv é opcional; em produção as variáveis vêm do ambiente.
}

const config = {
    port: parseInt(process.env.PORT, 10) || 3000,

    // Caminho do banco. ':memory:' mantém o comportamento original (SQLite em memória).
    databaseFile: process.env.DATABASE_FILE || ':memory:',

    // Credenciais e secrets — NUNCA hardcoded. Lidos do ambiente.
    dbUser: process.env.DB_USER || '',
    dbPass: process.env.DB_PASS || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
};

module.exports = { config };
