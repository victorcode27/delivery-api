// Quick test to check if there are JavaScript errors in the console
console.log("=== BUTTON DEBUG ===");

// Check if buttons exist in DOM
const settingsBtn = document.getElementById('settings-btn');
const loadInvoicesBtn = document.getElementById('load-invoices-btn');
const loadInvoicesBtn2 = document.getElementById('load-invoices-btn-2');

console.log("Settings button exists:", settingsBtn !== null);
console.log("Load Invoices button exists:", loadInvoicesBtn !== null);
console.log("Load Invoices button 2 exists:", loadInvoicesBtn2 !== null);

if (settingsBtn) {
    console.log("Settings button style.display:", settingsBtn.style.display);
    console.log("Settings button classList:", settingsBtn.classList);
}

if (loadInvoicesBtn) {
    console.log("Load Invoices button style.display:", loadInvoicesBtn.style.display);
    console.log("Load Invoices button classList:", loadInvoicesBtn.classList);
}

console.log("=== END DEBUG ===");
