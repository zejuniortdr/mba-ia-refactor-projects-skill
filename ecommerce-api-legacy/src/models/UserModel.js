const crypto = require('crypto');
const { run, get } = require('./database');

// Parâmetros de hashing (substituem o "badCrypto" base64 reversível do legado).
const SCRYPT_KEYLEN = 64;
const SALT_BYTES = 16;

function hashPassword(plainPassword) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const derived = crypto.scryptSync(plainPassword, salt, SCRYPT_KEYLEN).toString('hex');
    return `${salt}:${derived}`;
}

async function findByEmail(email) {
    return get("SELECT id, name, email FROM users WHERE email = ?", [email]);
}

async function create({ name, email, password }) {
    const hash = hashPassword(password);
    const { lastID } = await run(
        "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
        [name, email, hash]
    );
    return lastID;
}

async function deleteById(id) {
    const { changes } = await run("DELETE FROM users WHERE id = ?", [id]);
    return changes;
}

module.exports = { findByEmail, create, deleteById, hashPassword };
