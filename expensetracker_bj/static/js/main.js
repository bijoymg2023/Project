// Ensures the DOM is fully loaded before running scripts
document.addEventListener('DOMContentLoaded', function() {
    
    // Expense form validation (for add_expense.html)
    const expenseForm = document.querySelector("#expenseForm");
    
    if (expenseForm) {
        expenseForm.addEventListener('submit', function(e) {
            const amount = document.querySelector("input[name='amount']").value;
            const expenseDate = document.querySelector("input[name='expense_date']").value;
            const description = document.querySelector("input[name='description']").value;

            if (!amount || !expenseDate || !description) {
                e.preventDefault();
                alert("Please fill in all required fields.");
            }
        });
    }

    // Delete expense confirmation (for dashboard.html)
    const deleteLinks = document.querySelectorAll(".delete-expense");
    
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm("Are you sure you want to delete this expense?")) {
                e.preventDefault();
            }
        });
    });

    // Add date picker for the add_expense form (optional feature)
    const dateInput = document.querySelector("input[type='date']");
    
    if (dateInput) {
        dateInput.setAttribute('min', new Date().toISOString().split('T')[0]); // Set minimum date to today
    }
    
});
