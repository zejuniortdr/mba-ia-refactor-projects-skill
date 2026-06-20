const UserModel = require('../models/UserModel');

async function deleteUser(req, res) {
    await UserModel.deleteById(req.params.id);
    res.send('Usuário deletado');
}

module.exports = { deleteUser };
