const { Router } = require('express');
const { asyncHandler } = require('../middlewares/asyncHandler');
const CheckoutController = require('../controllers/CheckoutController');

const router = Router();

router.post('/api/checkout', asyncHandler(CheckoutController.checkout));

module.exports = router;
