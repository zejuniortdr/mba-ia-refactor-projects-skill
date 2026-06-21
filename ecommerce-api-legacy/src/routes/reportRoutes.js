const { Router } = require('express');
const { asyncHandler } = require('../middlewares/asyncHandler');
const ReportController = require('../controllers/ReportController');

const router = Router();

router.get('/api/admin/financial-report', asyncHandler(ReportController.financialReport));

module.exports = router;
