const { Router } = require('express');
const { asyncHandler } = require('../middlewares/asyncHandler');
const UserController = require('../controllers/UserController');

const router = Router();

router.delete('/api/users/:id', asyncHandler(UserController.deleteUser));

module.exports = router;
