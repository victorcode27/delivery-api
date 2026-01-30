# Multi-Select Invoice Add Workflow

## Overview
This workflow implements multi-selection and bulk-add functionality for the "Available Invoices" modal without closing it after adding invoices.

---

## 1. HTML Structure Updates

### Available Invoices Modal
```html
<!-- Select All Checkbox -->
<div class="select-all-container">
  <input type="checkbox" id="selectAllInvoices">
  <label for="selectAllInvoices">Select All</label>
</div>

<!-- Invoice List with Individual Checkboxes -->
<div class="invoice-list">
  <div class="invoice-item" data-invoice-id="INV001">
    <input type="checkbox" class="invoice-checkbox" data-invoice-id="INV001">
    <span>Invoice INV001 - Customer A - $100.00</span>
  </div>
  <!-- More invoice items... -->
</div>

<!-- Action Button -->
<button id="addSelectedToManifest">Add Selected to Manifest</button>
```

---

## 2. JavaScript Logic

### Step 1: Track Current Manifest State
```javascript
// Maintain a Set of already-added invoice IDs to prevent duplicates
let manifestInvoiceIds = new Set();

// Initialize from existing manifest data on page load
function initializeManifestIds() {
  manifestInvoiceIds.clear();
  document.querySelectorAll('.manifest-invoice-item').forEach(item => {
    manifestInvoiceIds.add(item.dataset.invoiceId);
  });
}
```

### Step 2: Select All Functionality
```javascript
document.getElementById('selectAllInvoices').addEventListener('change', function() {
  const checkboxes = document.querySelectorAll('.invoice-checkbox');
  checkboxes.forEach(checkbox => {
    checkbox.checked = this.checked;
  });
});

// Update "Select All" state when individual checkboxes change
document.querySelectorAll('.invoice-checkbox').forEach(checkbox => {
  checkbox.addEventListener('change', updateSelectAllState);
});

function updateSelectAllState() {
  const allCheckboxes = document.querySelectorAll('.invoice-checkbox');
  const checkedCheckboxes = document.querySelectorAll('.invoice-checkbox:checked');
  const selectAllCheckbox = document.getElementById('selectAllInvoices');
  
  selectAllCheckbox.checked = allCheckboxes.length === checkedCheckboxes.length;
  selectAllCheckbox.indeterminate = checkedCheckboxes.length > 0 && 
                                     checkedCheckboxes.length < allCheckboxes.length;
}
```

### Step 3: Add Selected to Manifest
```javascript
document.getElementById('addSelectedToManifest').addEventListener('click', function() {
  // Get all checked invoice checkboxes
  const checkedBoxes = document.querySelectorAll('.invoice-checkbox:checked');
  
  // Validation: Check if at least one invoice is selected
  if (checkedBoxes.length === 0) {
    alert('Please select at least one invoice.');
    return;
  }
  
  // Collect selected invoice data
  const invoicesToAdd = [];
  checkedBoxes.forEach(checkbox => {
    const invoiceId = checkbox.dataset.invoiceId;
    
    // Duplicate prevention: Skip if already in manifest
    if (manifestInvoiceIds.has(invoiceId)) {
      console.log(`Invoice ${invoiceId} already in manifest - skipping`);
      return; // Skip this invoice
    }
    
    // Get invoice data from the row
    const invoiceRow = checkbox.closest('.invoice-item');
    const invoiceData = {
      id: invoiceId,
      customer: invoiceRow.dataset.customer,
      amount: invoiceRow.dataset.amount,
      orderNumber: invoiceRow.dataset.orderNumber
      // Add other relevant fields
    };
    
    invoicesToAdd.push(invoiceData);
  });
  
  // Add invoices to manifest
  if (invoicesToAdd.length > 0) {
    addInvoicesToManifest(invoicesToAdd);
    
    // Update the manifest ID set
    invoicesToAdd.forEach(invoice => {
      manifestInvoiceIds.add(invoice.id);
    });
    
    // Uncheck all checkboxes after adding
    checkedBoxes.forEach(checkbox => checkbox.checked = false);
    document.getElementById('selectAllInvoices').checked = false;
    
    // Optional: Show success message
    showToast(`${invoicesToAdd.length} invoice(s) added to manifest`);
  } else {
    alert('All selected invoices are already in the manifest.');
  }
  
  // DO NOT CLOSE MODAL - keep it open for more selections
});
```

### Step 4: Add Invoices to Manifest (Helper Function)
```javascript
function addInvoicesToManifest(invoices) {
  const manifestContainer = document.getElementById('manifestInvoices');
  
  invoices.forEach(invoice => {
    // Create manifest row element
    const row = document.createElement('div');
    row.className = 'manifest-invoice-item';
    row.dataset.invoiceId = invoice.id;
    
    row.innerHTML = `
      <span class="invoice-number">${invoice.id}</span>
      <span class="customer-name">${invoice.customer}</span>
      <span class="amount">${invoice.amount}</span>
      <button class="remove-invoice" data-invoice-id="${invoice.id}">Remove</button>
    `;
    
    manifestContainer.appendChild(row);
    
    // Attach remove handler
    row.querySelector('.remove-invoice').addEventListener('click', function() {
      removeInvoiceFromManifest(invoice.id);
    });
  });
}

function removeInvoiceFromManifest(invoiceId) {
  // Remove from DOM
  const row = document.querySelector(`.manifest-invoice-item[data-invoice-id="${invoiceId}"]`);
  if (row) row.remove();
  
  // Remove from tracking set
  manifestInvoiceIds.delete(invoiceId);
}
```

### Step 5: Refresh Available Invoices List
```javascript
// When opening the modal, disable checkboxes for invoices already in manifest
function refreshAvailableInvoices() {
  document.querySelectorAll('.invoice-checkbox').forEach(checkbox => {
    const invoiceId = checkbox.dataset.invoiceId;
    
    if (manifestInvoiceIds.has(invoiceId)) {
      checkbox.disabled = true;
      checkbox.closest('.invoice-item').classList.add('already-added');
    } else {
      checkbox.disabled = false;
      checkbox.closest('.invoice-item').classList.remove('already-added');
    }
  });
}

// Call this when modal opens
document.getElementById('openInvoiceModal').addEventListener('click', function() {
  initializeManifestIds();
  refreshAvailableInvoices();
  // Show modal
});
```

---

## 3. Key Features Summary

✅ **Multi-Selection**: Users can select multiple invoices with individual checkboxes  
✅ **Select All**: Master checkbox to select/deselect all invoices  
✅ **Bulk Add**: Single button click adds all selected invoices  
✅ **Modal Stays Open**: Modal remains open after adding invoices for further selections  
✅ **Duplicate Prevention**: Invoices already in manifest are disabled or skipped  
✅ **Validation**: Alert shown if no invoices are selected  
✅ **Visual Feedback**: Indeterminate state for partial selection, toast notifications  

---

## 4. Optional Enhancements

- **Visual Indicator**: Add CSS class `.already-added` to gray out invoices already in manifest
- **Counter**: Display count of selected invoices (e.g., "3 invoices selected")
- **Keyboard Shortcuts**: Ctrl+A for select all, Enter to add selected
- **Undo**: Add ability to undo last bulk add operation
