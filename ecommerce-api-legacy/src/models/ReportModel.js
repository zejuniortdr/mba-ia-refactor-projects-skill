const { all } = require('./database');

const PAID_STATUS = 'PAID';

// Relatório financeiro em UMA única query com JOINs (elimina o N+1 do legado).
// Mantém o mesmo formato de saída: lista de cursos com receita e alunos.
async function financialReport() {
    const rows = await all(`
        SELECT
            c.id    AS course_id,
            c.title AS course_title,
            e.id    AS enrollment_id,
            u.name  AS student_name,
            p.amount AS amount,
            p.status AS status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u       ON u.id = e.user_id
        LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id
    `);

    const byCourse = new Map();

    for (const row of rows) {
        if (!byCourse.has(row.course_id)) {
            byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
        }
        const courseData = byCourse.get(row.course_id);

        // Curso sem matrículas: o LEFT JOIN traz enrollment_id nulo.
        if (row.enrollment_id == null) continue;

        if (row.status === PAID_STATUS) {
            courseData.revenue += row.amount;
        }

        courseData.students.push({
            student: row.student_name || 'Unknown',
            paid: row.amount != null ? row.amount : 0,
        });
    }

    return Array.from(byCourse.values());
}

module.exports = { financialReport };
