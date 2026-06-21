const sqlite3 = require('sqlite3').verbose();
const { config } = require('../config/settings');

// Conexão única compartilhada. Helpers promisificados substituem o estilo callback,
// removendo o "callback hell" e o workaround self/this do código legado.
const db = new sqlite3.Database(config.databaseFile);

function run(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function (err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            if (err) return reject(err);
            resolve(row);
        });
    });
}

function all(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

// Cria o schema e carrega os seeds. Sequencial para garantir ordem antes do listen.
async function init() {
    await run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
    await run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
    await run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
    await run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
    await run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

    await run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", ['Leonan', 'leonan@fullcycle.com.br', '123']);
    await run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)", ['Clean Architecture', 997.00, 1, 'Docker', 497.00, 1]);
    await run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
    await run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [1, 997.00, 'PAID']);
}

module.exports = { db, run, get, all, init };
