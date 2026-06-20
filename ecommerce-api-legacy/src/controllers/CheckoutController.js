const { AppError } = require('../middlewares/errorHandler');
const CourseModel = require('../models/CourseModel');
const UserModel = require('../models/UserModel');
const EnrollmentModel = require('../models/EnrollmentModel');
const PaymentModel = require('../models/PaymentModel');
const AuditLogModel = require('../models/AuditLogModel');
const paymentService = require('../services/paymentService');

const DEFAULT_PASSWORD = '123456';

// Orquestra o checkout: valida entrada, garante usuário, autoriza pagamento e matricula.
// Zero SQL aqui — toda persistência é delegada aos models.
async function checkout(req, res) {
    const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

    if (!name || !email || !courseId || !cardNumber) {
        throw new AppError('Bad Request', 400);
    }

    const course = await CourseModel.findActiveById(courseId);
    if (!course) {
        throw new AppError('Curso não encontrado', 404);
    }

    // Autoriza antes de persistir qualquer coisa.
    const status = paymentService.authorize(cardNumber);
    if (status === paymentService.PaymentStatus.DENIED) {
        throw new AppError('Pagamento recusado', 400);
    }

    let user = await UserModel.findByEmail(email);
    const userId = user
        ? user.id
        : await UserModel.create({ name, email, password: password || DEFAULT_PASSWORD });

    const enrollmentId = await EnrollmentModel.create({ userId, courseId });
    await PaymentModel.create({ enrollmentId, amount: course.price, status });
    await AuditLogModel.record(`Checkout curso ${courseId} por ${userId}`);

    res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
}

module.exports = { checkout };
