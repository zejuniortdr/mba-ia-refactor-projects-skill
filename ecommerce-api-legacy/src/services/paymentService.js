// Regra de aprovação de pagamento isolada do controller e da rota.
// Mantém o comportamento legado: cartões iniciados no dígito de teste são aprovados.
const APPROVED_CARD_PREFIX = '4';

const PaymentStatus = {
    PAID: 'PAID',
    DENIED: 'DENIED',
};

function authorize(cardNumber) {
    return cardNumber.startsWith(APPROVED_CARD_PREFIX)
        ? PaymentStatus.PAID
        : PaymentStatus.DENIED;
}

module.exports = { authorize, PaymentStatus };
