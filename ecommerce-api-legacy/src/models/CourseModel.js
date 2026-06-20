const { get } = require('./database');

async function findActiveById(courseId) {
    return get("SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
}

module.exports = { findActiveById };
