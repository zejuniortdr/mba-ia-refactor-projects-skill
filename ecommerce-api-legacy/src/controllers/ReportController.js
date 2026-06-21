const ReportModel = require('../models/ReportModel');

async function financialReport(req, res) {
    const report = await ReportModel.financialReport();
    res.json(report);
}

module.exports = { financialReport };
