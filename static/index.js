

const currentDateDisplay = document.getElementById('currentDate');
const customerView = document.getElementById('customerView');
const customerNavItems = document.querySelectorAll('.customer-navbar li');
const defaultView = document.getElementById('defaultView');
const customerItems = document.querySelectorAll('.customer-item');
const customerSections = document.querySelectorAll('.customer-section');
const addCustomerBtn = document.getElementById('addCustomerBtn');
const closeModalButtons = document.querySelectorAll('.close-modal, .cancel-modal');
const editButtons = document.querySelectorAll('.edit-btn');
const addContactBtn = document.getElementById('addContactBtn');
const editContactBtn = document.getElementById('editContactBtn');
const addOrdertBtn = document.getElementById('addOrderBtn');
const addMeetingBtn = document.getElementById('addMeetingBtn');
const addUpdateBtn = document.getElementById('addUpdateBtn');
const viewOrderBtn = document.getElementById('view-order');
const viewMeetingBtn = document.getElementById('view-meeting');
const viewUpdateBtn = document.getElementById('view-update');
const updateActionBtn = document.getElementById('updateActionBtn');



function setupEventListeners() {
  // Add customer button
  addCustomerBtn.addEventListener('click', () => {
    addCustomerModal.style.display = 'block';
  });

  addContactBtn.addEventListener('click', () => {
    addContactModal.style.display = 'block';
  });

  addOrdertBtn.addEventListener('click', () => {
    addOrderModal.style.display = 'block';
  });

  addMeetingBtn.addEventListener('click', () => {
    addMeetingModal.style.display = 'block';
  });

  updateActionBtn.addEventListener('click', () => {
    editActionItemModal.style.display = 'block';
  });

  addUpdateBtn.addEventListener('click', () => {
    addUpdateModal.style.display = 'block';
  });

  // Fix: Single event listener for dynamically added elements
  document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'editContactBtn') {
      editContactModal.style.display = 'block';
    }
  });

  document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'editContactBtn') {
      editContactModal.style.display = 'block';
    }
  });

  
  document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'view-order') {
      viewOrderModal.style.display = 'block';
    }
  });

  document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'view-meeting') {
      viewMeetingModal.style.display = 'block';
    }
  });

  document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'view-update') {
      viewUpdateModal.style.display = 'block';
    }
  });
}

function formatDate(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}


document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("customerSearch");
  const customersList = document.getElementById("customersList").getElementsByClassName("customer-item");

  searchInput.addEventListener("input", function () {
      let searchValue = searchInput.value.toLowerCase();

      for (let customer of customersList) {
          let customerNameElement = customer.querySelector("h3");
          let customerDetailsElement = customer.querySelector("p");

          // Ensure the elements exist before accessing textContent
          let customerName = customerNameElement ? customerNameElement.textContent.toLowerCase() : '';
          let customerDetails = customerDetailsElement ? customerDetailsElement.textContent.toLowerCase() : '';

          if (customerName.includes(searchValue) || customerDetails.includes(searchValue)) {
              customer.style.display = "block"; // Show if matches the search
          } else {
              customer.style.display = "none"; // Hide if not matching
          }
      }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("contactsSearch");
  const contactsList = document.getElementById("contactCardsContainer").getElementsByClassName("contact-card");

  searchInput.addEventListener("input", function () {
      let searchValue = searchInput.value.toLowerCase();

      for (let contact of contactsList) {
          let contactNameElement = contact.querySelector("h3");

          // Ensure the elements exist before accessing textContent
          let customerName = contactNameElement ? contactNameElement.textContent.toLowerCase() : '';

          if (customerName.includes(searchValue)) {
            contact.style.display = "block"; // Show if matches the search
          } else {
            contact.style.display = "none"; // Hide if not matching
          }
      }
  });
});


  // Customer navbar tabs
  customerNavItems.forEach(item => {
    item.addEventListener('click', () => {
      // Remove active class from all tabs and sections
      customerNavItems.forEach(tab => tab.classList.remove('active'));
      customerSections.forEach(section => section.classList.remove('active'));
      
      // Add active class to clicked tab and corresponding section
      item.classList.add('active');
      const sectionId = item.dataset.section;
      const section = document.getElementById(sectionId);
      
      // Reset animation and then apply it
      section.style.animation = 'none';
      setTimeout(() => {
        section.style.animation = 'fadeInRight 0.5s ease-out';
        section.classList.add('active');
      }, 10);
    });
  });

customerItems.forEach(item => {
  item.addEventListener('click', function() {
    // Remove 'active' class from all items
    customerItems.forEach(item => item.classList.remove('active'));
    
    // Add 'active' class to the clicked item
    this.classList.add('active');
  });
});


  // Add animation to customer view
  customerView.style.animation = 'none';
  setTimeout(() => {
    customerView.style.animation = 'fadeInRight 0.5s ease-out';
    customerView.classList.add('active');
  }, 10);
  


function displayCurrentDate() {
  const now = new Date();
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  currentDateDisplay.textContent = now.toLocaleDateString('en-US', options);
}

document.querySelectorAll(".filter-input").forEach(input => {
  input.addEventListener("input", function() {
    var filterValue = input.value.toLowerCase();
    var columnIndex = Array.from(input.parentNode.parentNode.children).indexOf(input.parentNode);
    var rows = document.querySelectorAll("#action-items-table tr");

    rows.forEach(row => {
      var cell = row.cells[columnIndex];
      if (cell) {
        var text = cell.innerText.toLowerCase();
        if (text.indexOf(filterValue) === -1) {
          row.style.display = "none";
        } else {
          row.style.display = "";
        }
      }
    });
  });
});

// Function to filter status dropdown
document.getElementById("filter-status").addEventListener("change", function() {
  var filterValue = this.value.toLowerCase();
  var rows = document.querySelectorAll("#action-items-table tr");

  rows.forEach(row => {
    var statusCell = row.cells[4];
    if (statusCell) {
      var status = statusCell.innerText.trim().toLowerCase();
      if (filterValue && status.indexOf(filterValue) === -1) {
        row.style.display = "none";
      } else {
        row.style.display = "";
      }
    }
  });
});

// Function to sort the due date column (oldest to newest, reverse on click)
let isAscending = true;

function sortDueDate() {
  const table = document.querySelector(".data-table tbody");
  const rows = Array.from(table.rows);

  rows.sort((rowA, rowB) => {
    const dateA = new Date(rowA.cells[3].innerText.trim());
    const dateB = new Date(rowB.cells[3].innerText.trim());

    if (isAscending) {
      return dateA - dateB;
    } else {
      return dateB - dateA;
    }
  });

  rows.forEach(row => table.appendChild(row));
  isAscending = !isAscending;
}


function setCustomerId(customerId) {
  // Get all elements with the id "customerIdInput" 
  const elements = document.querySelectorAll('#customerIdInput');

  // Iterate over the NodeList and set the value for each element
  elements.forEach(function(element) {
    element.value = customerId;
  });
}




function fetchCustomerDetails(customerId) {
  fetch(`/get_customer/${customerId}`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert("Customer not found!");
        return;
      }
    
      setCustomerId(customerId);
      selectCustomer() 

    const sidebar = document.getElementById("sidebar");
    sidebar.classList.remove("open");


      // Extract data
      const { customerInfo, contacts, meetings, updates, technicalInfo, commercialInfo, orders, actionItems } = data;

      // Update the customer view dynamically
      const customerSections = document.getElementById("customerSections");
      customerSections.classList.add('active');

      // Update the fields in the 'Company Information' section
      const companyInfoFields = document.querySelectorAll('#companyInfo .info-value');

      const contactCardsContainer = document.querySelector('.contact-cards-container');
      contactCardsContainer.innerHTML = ''; // Clear existing content

      contacts.forEach(contact => {
        const contactCard = document.createElement('div');
        contactCard.classList.add('contact-card');
        contactCard.innerHTML = `
          <h3>${contact.name}</h3>
          <p class="role">${contact.role}</p>
          <div class="contact-details">
            <span>
              <i class="fas fa-envelope"></i>
              <strong>Email:</strong> 
              <a href="mailto:${contact.email}">${contact.email}</a>
            </span>
            <span>
              <i class="fas fa-phone"></i>
              <strong>Phone:</strong> ${contact.phone}
            </span>
          </div>
      <div class="actions">
        <button class="btn small primary edit-contact-btn"
                data-id="${contact.id}"
                data-name="${contact.name}"
                data-role="${contact.role}"
                data-email="${contact.email}"
                data-phone="${contact.phone}"
                title="Edit">
          <i class="fas fa-edit"></i>
        </button>
        <form action="/delete_contact/${contact.id}" method="POST" id="deleteContactForm" onsubmit="return confirmDelete(event)">
          <input type="hidden" value="${customerId}" name="customer_id" id="customerIdInput">
          <button class="btn small danger delete-contact" type="submit" title="Delete">
            <i class="fas fa-trash-alt"></i>
          </button>
        </form>
      </div>
        `;
        contactCardsContainer.appendChild(contactCard);
    });


    attachEditContactListeners();


    const ordersTable = document.getElementById('ordersTable').querySelector('tbody');
    ordersTable.innerHTML = '';
    
    orders.forEach((order, index) => {
      const row = document.createElement('tr');
      row.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s both`;  // Now index is defined as the second argument in the callback
    
      row.innerHTML = `
        <td>${formatDate(order.date)}</td>
        <td>${order.orderNo}</td>
        <td>${order.material}</td>
        <td>${order.amount}</td>
    <td class="action-cell">
        <button class="btn small primary view-order"
                data-id="${order.id}"
                data-orderNo="${order.orderNo}"
                data-material="${order.material}"
                data-amount="${order.amount}"
                data-goal="${order.goal}"
                data-date="${formatDate(order.date)}"
                data-orderFile="${order.orderFile}"
                data-orderInvoice="${order.invoiceFile}"
                data-orderFile="{{ url_for('static', filename='uploads/' ~ "${order.orderFile}") }}"
                data-invoiceFile="{{ url_for('static', filename='uploads/' ~ "${order.invoiceFile}") }}"
                title="View">
          <i class="fas fa-eye"></i>
        </button>
        <form action="/delete_order" method="POST" id="deleteOrderForm" onsubmit="return confirmDelete(event)">
          <input type="hidden" value="${order.id}" name="order_id">
          <button class="btn small danger delete-order" type="submit" title="Delete">
            <i class="fas fa-trash-alt"></i>
          </button>
        </form>
    </td>
      `;
      ordersTable.appendChild(row);
    });

    attachViewOrderListeners();

    const meetingsTable = document.getElementById('meetingsTable').querySelector('tbody');
    meetingsTable.innerHTML = '';

    meetings.forEach((meeting, index) => {
      const row = document.createElement('tr');
      row.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s both`;

      row.innerHTML = `
        <td>${formatDate(meeting.date)}</td>
        <td>${meeting.title}</td>
    <td class="action-cell">
              <button class="btn small primary view-meeting"
                data-id="${meeting.id}"
                data-company="${meeting.company}"
                data-title="${meeting.title}"
                data-attendees="${meeting.attendees}"
                data-date="${formatDate(meeting.date)}"
                data-summary="${meeting.summary}"
                title="View">
          <i class="fas fa-eye"></i>
        </button>
      <form action="/delete_meeting" method="POST" id="deleteMeetingForm" onsubmit="return confirmDelete(event)">
        <input type="hidden" value="${meeting.id}" name="meeting_id">
        <button class="btn small danger delete-meeting" type="submit" title="Delete">
          <i class="fas fa-trash-alt"></i>
        </button>
      </form>
    </td>
      `;
      meetingsTable.appendChild(row);
    });

    attachViewMeetingListeners()

    function buildActionItemsListMeeting(actionItems) {
      const actionsMeetingList = document.getElementById("viewMeetingActions");
      actionsMeetingList.innerHTML = ''; // Clear any existing content
      
      // Create the table container
      const tableMeetingActionContainer = document.createElement('div');
      tableMeetingActionContainer.classList.add('table-container');
      
      // Create the table structure
      const tableMeetingAction = document.createElement('table');
      tableMeetingAction.classList.add('data-table'); // Apply the data-table class
      
      // Create the table header row
      const tableHeader = document.createElement('thead');
      tableHeader.innerHTML = `
        <tr>
          <th>Item</th>
          <th>Responsible</th>
          <th>Due Date</th>
          <th>Status</th>
        </tr>
      `;
      tableMeetingAction.appendChild(tableHeader);
      
      // Create the table body
      const tableBody = document.createElement('tbody');
      
      // Filter the action items to only include those with category "meeting"
      const meetingActionItems = actionItems.filter(actionItem => actionItem.category === "meeting");
      console.log(meetingActionItems)
      // Check if there are any meeting action items
      if (meetingActionItems.length === 0) {
        // If no action items with category "meeting", display a "No action items available" message
        const noActionRow = document.createElement('tr');
        noActionRow.innerHTML = `
          <td colspan="4" style="text-align: center; padding: 15px;">No action items available</td>
        `;
        tableBody.appendChild(noActionRow);
      } else {
        // Loop through each filtered meeting action item and create a table row (<tr>)
        meetingActionItems.forEach(actionItem => {
          const row = document.createElement('tr');
          
          // Determine the status class based on the action item status
          let statusClass = '';
          switch(actionItem.status.toLowerCase()) {
            case 'pending':
              statusClass = 'status pending';
              break;
            case 'in-progress':
              statusClass = 'status in-progress';
              break;
            case 'not-started':
              statusClass = 'status not-started';
              break;
            case 'completed':
              statusClass = 'status completed';
              break;
            default:
              statusClass = 'status';
              break;
          }
          
          // Add item details to the table row
          row.innerHTML = `
            <td>${actionItem.item}</td>
            <td>${actionItem.responsible}</td>
            <td>${actionItem.dueDate}</td>
            <td><span class="${statusClass}">${actionItem.status}</span></td>
          `;
          
          tableBody.appendChild(row); // Add the row to the table body
        });
      }
      
      // Append the table body to the table
      tableMeetingAction.appendChild(tableBody);
      
      // Append the table to the table container
      tableMeetingActionContainer.appendChild(tableMeetingAction);
      
      // Append the table container to the list container
      actionsMeetingList.appendChild(tableMeetingActionContainer);
    }
    
    // Example of calling the function with an empty list (no action items)
    buildActionItemsListMeeting(actionItems);

    const updatesTable = document.getElementById('updatesTable').querySelector('tbody');
      updatesTable.innerHTML = '';

      updates.forEach((update, index) => {
        const row = document.createElement('tr');
        row.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s both`;

        row.innerHTML = `
          <td>${formatDate(update.date)}</td>
          <td>${update.title}</td>
    <td class="action-cell">
        <button class="btn small primary view-update"
                data-id="${update.id}"
                data-title="${update.title}"
                data-update="${update.content}"
                data-date="${formatDate(update.date)}"
                data-nextStep="${update.nextStep}"
                data-file="${update.file}"
                data-updateFile="{{ url_for('static', filename='uploads/' ~ "${update.file}") }}

                title="View">
          <i class="fas fa-eye"></i>
        </button>
      <form action="/delete_update" method="POST" id="deleteUpdateForm" onsubmit="return confirmDelete(event)">
        <input type="hidden" value="${update.id}" name="update_id">
        <button class="btn small danger delete-update" type="submit" title="Delete">
          <i class="fas fa-trash-alt"></i>
        </button>
      </form>
    </td>
        `;
        updatesTable.appendChild(row);
      });

    attachViewUpdateListeners()

    function buildActionItemsListUpdate(actionItems) {
      const actionsUpdateList = document.getElementById("viewUpdateActions");
      actionsUpdateList.innerHTML = ''; // Clear any existing content
      // Create the table container
      const tableUpdateActionContainer = document.createElement('div');
      tableUpdateActionContainer.classList.add('table-container');
      
      // Create the table structure
      const tableUpdateAction = document.createElement('table');
      tableUpdateAction.classList.add('data-table'); // Apply the data-table class
      
      // Create the table header row
      const tableHeader = document.createElement('thead');
      tableHeader.innerHTML = `
        <tr>
          <th>Item</th>
          <th>Responsible</th>
          <th>Due Date</th>
          <th>Status</th>
        </tr>
      `;
      tableUpdateAction.appendChild(tableHeader);
      
      // Create the table body
      const tableBody = document.createElement('tbody');
      
      // Filter the action items to only include those with category "meeting"
      const updateActionItems = actionItems.filter(actionItem => actionItem.category === "update");
      // Check if there are any meeting action items
      if (updateActionItems.length === 0) {
        // If no action items with category "meeting", display a "No action items available" message
        const noActionRow = document.createElement('tr');
        noActionRow.innerHTML = `
          <td colspan="4" style="text-align: center; padding: 15px;">No action items available</td>
        `;
        tableBody.appendChild(noActionRow);
      } else {
        // Loop through each filtered meeting action item and create a table row (<tr>)
        updateActionItems.forEach(actionItem => {
          const row = document.createElement('tr');
          
          // Determine the status class based on the action item status
          let statusClass = '';
          switch(actionItem.status.toLowerCase()) {
            case 'pending':
              statusClass = 'status pending';
              break;
            case 'in-progress':
              statusClass = 'status in-progress';
              break;
            case 'not-started':
              statusClass = 'status not-started';
              break;
            case 'completed':
              statusClass = 'status completed';
              break;
            default:
              statusClass = 'status';
              break;
          }
          
          // Add item details to the table row
          row.innerHTML = `
            <td>${actionItem.item}</td>
            <td>${actionItem.responsible}</td>
            <td>${actionItem.dueDate}</td>
            <td><span class="${statusClass}">${actionItem.status}</span></td>
          `;
          
          tableBody.appendChild(row); // Add the row to the table body
        });
      }
      
      // Append the table body to the table
      tableUpdateAction.appendChild(tableBody);
      
      // Append the table to the table container
      tableUpdateActionContainer.appendChild(tableUpdateAction);
      
      // Append the table container to the list container
      actionsUpdateList.appendChild(tableUpdateActionContainer);
    }
    
    // Example of calling the function with an empty list (no action items)
    buildActionItemsListUpdate(actionItems);
      
      companyInfoFields.forEach(field => {
        const fieldName = field.getAttribute('data-field');
      
        if (customerInfo && customerInfo.hasOwnProperty(fieldName)) {
          if (fieldName === 'status') {
              const statusSelect = document.querySelector(`#companyInfo select[data-field="${fieldName}"]`);
              if (statusSelect) {
                  statusSelect.value = customerInfo[fieldName] || ''; 
              }
          }
  
          if (fieldName === 'ndaFile') {
              const ndaLink = document.getElementById("ndaFileLink"); // Get the <a> element
  
              if (customerInfo[fieldName]) {
                  ndaLink.href = `/static/uploads/${customerInfo[fieldName]}`; // Correct path format
                  ndaLink.style.display = "inline"; // Show the link
                  ndaLink.textContent = "Download NDA"; // Set link text
              } else {
                  ndaLink.style.display = "none"; // Hide if no file
              }
          } else {
              field.textContent = customerInfo[fieldName] || 'N/A'; 
          }
          
          // Also populate the input field in edit mode
          const inputField = document.querySelector(`#companyInfo input[data-field="${fieldName}"]`);
          if (inputField) {
            inputField.value = customerInfo[fieldName] || ''; // Set the value for edit mode
          }
            

        } 
        // Check if the technical object exists and has the required field
        else if (technicalInfo && technicalInfo.hasOwnProperty(fieldName)) {
          field.textContent = technicalInfo[fieldName] || 'N/A'; // For view mode
          const inputField = document.querySelector(`#companyInfo input[data-field="${fieldName}"]`);
          if (inputField) {
            inputField.value = technicalInfo[fieldName] || ''; // Set the value for edit mode
          }
        } 
        // Check if the commercial object exists and has the required field
        else if (commercialInfo && commercialInfo.hasOwnProperty(fieldName)) {
          field.textContent = commercialInfo[fieldName] || 'N/A'; // For view mode
          const inputField = document.querySelector(`#companyInfo input[data-field="${fieldName}"]`);
          if (inputField) {
            inputField.value = commercialInfo[fieldName] || ''; // Set the value for edit mode
          }
        } 
        // If no data found
        else {
          field.textContent = 'N/A'; // For view mode
          const inputField = document.querySelector(`#companyInfo input[data-field="${fieldName}"]`);
          if (inputField) {
            inputField.value = ''; // Set the value for edit mode
          }
        }
      });

    })

    .catch(error => console.error("Error fetching customer data:", error));
  
}


function selectCustomer() {

  // Hide defaultView and show customerView
  defaultView.style.display = 'none';
  customerView.style.display = 'block';
  document.getElementById("contactsView").style.display = "none";
  // Add animation to customer view
  customerView.style.animation = 'none';
  setTimeout(() => {
    customerView.style.animation = 'fadeInRight 0.5s ease-out';
    customerView.classList.add('active');
  }, 10);

  // // Set first tab as active
  // customerNavItems[0].click();
}

// Ensure defaultView is displayed when the page loads
document.addEventListener("DOMContentLoaded", function () {
  defaultView.style.display = "block"; // Show defaultView
  customerView.style.display = "none"; // Hide customerView initially
});


  // Close modal buttons
  closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
      const modals = [addCustomerModal, addContactModal, editContactModal, addOrderModal, editActionItemModal,  addMeetingModal, addUpdateModal, viewOrderModal, viewMeetingModal, viewUpdateModal];
      
      modals.forEach(modal => {
        if (modal.style.display === 'block') {
          const modalContent = modal.querySelector('.modal-content');
          modalContent.style.animation = 'modalFadeOut 0.3s';
          
          setTimeout(() => {
            modal.style.display = 'none';
            modalContent.style.animation = 'modalFadeIn 0.3s';
          }, 300);
        }
      });
    });
  });



  document.getElementById("contactsListBtn").addEventListener("click", function () {
    fetch('/get_contacts')
        .then(response => response.json())
        .then(contacts => {
            const contactCardsContainer = document.getElementById("contactCardsContainer");
            contactCardsContainer.innerHTML = ''; // Clear previous content

            contacts.forEach(contact => {
                const contactCard = document.createElement('div');
                contactCard.classList.add('contact-card');
                contactCard.innerHTML = `
                    <h3>${contact.name}</h3>
                    <p class="role">${contact.role}</p>
                    <div class="contact-details">
                        <span>
                            <i class="fas fa-envelope"></i>
                            <strong>Email:</strong> 
                            <a href="mailto:${contact.email}">${contact.email}</a>
                        </span>
                        <span>
                            <i class="fas fa-phone"></i>
                            <strong>Phone:</strong> ${contact.phone}
                        </span>
                    </div>
                `;
                contactCardsContainer.appendChild(contactCard);
            });

            // Show the contacts view, hide default view
            document.getElementById("defaultView").style.display = "none";
            document.getElementById("contactsView").style.display = "block";
        });
});

// Back Button to Return to Default View
document.getElementById("backToMainView").addEventListener("click", function () {
  document.getElementById("defaultView").style.display = "block";
  document.getElementById("contactsView").style.display = "none";
});


editButtons.forEach(button => {
  button.addEventListener('click', (e) => {
    const section = e.target.closest('.customer-section');
    const viewMode = section.querySelector('.section-content.view-mode');
    const editMode = section.querySelector('.section-content.edit-mode');
    
    // Toggle between view and edit modes with animation
    viewMode.style.animation = 'fadeOut 0.3s ease-out';
    
    setTimeout(() => {
      viewMode.style.display = 'none';
      editMode.style.display = 'block';
      editMode.style.animation = 'fadeIn 0.3s ease-out';
    
    }, 300);
    
    // Add event listener to save button
    const saveBtn = editMode.querySelector('.save-btn');
    saveBtn.onclick = () => {
      
      setTimeout(() => {
        editMode.style.display = 'none';
        viewMode.style.display = 'grid';
      }, 300);
    }
    
    // Add event listener to cancel button
    const cancelBtn = editMode.querySelector('.cancel-btn');
    cancelBtn.onclick = () => {
      editMode.style.animation = 'fadeOut 0.3s ease-out';
      
      setTimeout(() => {
        editMode.style.display = 'none';
        viewMode.style.display = 'grid';
        viewMode.style.animation = 'fadeIn 0.3s ease-out';
      }, 300);
    };
  });
});

document.getElementById("editContactForm").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent the form from reloading the page
  
  // Get the form data
  const formData = new FormData(this);
  
  // Send the form data to the server
  fetch("/edit_contact", {
      method: "POST",
      body: formData
  })
  .then(response => {
      // Check if the response is JSON
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
          throw new Error("Invalid JSON response");
      }
      return response.json();
  })
  .then(data => {
      if (data.success) {
          alert("Contact updated successfully!");
          
          // Close the modal after successful update
          document.getElementById("editContactModal").style.display = "none";
          
          // Reload the customer details to reflect the changes
          fetchCustomerDetails(data.customer_id); // Refresh the customer details page
      } else {
          alert("Failed to update contact: " + (data.error || "Unknown error"));
      }
  })
  .catch(error => {
      console.error("Error:", error);
      alert("An error occurred while updating contact.");
  });
});





document.getElementById("addContactForm").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent default form submission

  // Get the form data
  const form = event.target;
  const formData = new FormData(form);

  // Send the data via Fetch API
  fetch(form.action, {
    method: form.method,
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert("Contact added successfully!");
      
      // Refresh the customer details page
      fetchCustomerDetails(data.customer_id);
      
      // Close the modal
      closeModal();
    } else {
      alert("Failed to add contact.");
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("An error occurred while adding the contact.");
  });
});

function closeModal() {
  const modal = document.getElementById("addContactModal");
    modal.style.display = 'none';
}


document.getElementById("addOrderForm").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent default form submission

  // Get the form data
  const form = event.target;
  const formData = new FormData(form);

  // Send the data via Fetch API
  fetch(form.action, {
    method: form.method,
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert("Order added successfully!");
      
      // Refresh the customer details page
      fetchCustomerDetails(data.customer_id);
      
      // Close the modal
      closeOrderModal();
    } else {
      alert("Failed to add order.");
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("An error occurred while adding the order.");
  });
});

function closeOrderModal() {
  const modal = document.getElementById("addOrderModal");
    modal.style.display = 'none';
}


document.getElementById("addUpdateForm").addEventListener("submit", function(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);

  // Collect action items
  let actionItems = [];
  document.querySelectorAll("#action-items-container .action-item").forEach(item => {
    actionItems.push({
      item: item.querySelector('input[name="action_item"]').value,
      responsible: item.querySelector('input[name="responsible"]').value,
      due_date: item.querySelector('input[name="due_date"]').value,
      status: item.querySelector('select[name="status"]').value
    });
  });

  formData.append("action_items", JSON.stringify(actionItems));

  // Send the data via Fetch API
  fetch(form.action, {
    method: form.method,
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert("Update added successfully!");
      fetchCustomerDetails(data.customer_id);
      closeUpdateModal();
    } else {
      alert("Failed to add meeting.");
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("An error occurred while adding the Update.");
  });
});

function closeUpdateModal() {
  const modal = document.getElementById("addUpdateModal");
    modal.style.display = 'none';
}


document.getElementById("updateCustomerDetails").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent the form from reloading the page
  
  // Get the form data
  const formData = new FormData(this);
  
  // Send the form data to the server
  fetch("/update_customer_details", {
      method: "POST",
      body: formData
  })
  .then(response => {
      // Check if the response is JSON
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
          throw new Error("Invalid JSON response");
      }
      return response.json();
  })
  .then(data => {
      if (data.success) {
          alert("Customer details updated successfully!");
          // Reload the customer details to reflect the changes
          fetchCustomerDetails(data.customer_id); // Refresh the customer details page
          
      } else {
          alert("Failed to update customer: " + (data.error || "Unknown error"));
      }
  })
  .catch(error => {
      console.error("Error:", error);
      alert("An error occurred while updating customer.");
  });
});


document.querySelectorAll(".add-action-item").forEach(button => {
  button.addEventListener("click", function() {
      // Identify the correct container based on the clicked button
      const container = this.closest(".modal-body").querySelector(".action-items-container");

      const div = document.createElement("div");
      div.classList.add("action-item");

      div.innerHTML = `
          <div class="form-group">
              <label>Item:</label>
              <input type="text" name="action_item" required>
          </div>
          <div class="form-group">
              <label>Responsible:</label>
              <input type="text" name="responsible" required>
          </div>
          <div class="form-group">
              <label>Due Date:</label>
              <input type="date" name="due_date" required>
          </div>
          <div class="form-group">
              <label>Status:</label>
              <select name="status" required>
                  <option value="Not Started">Not Started</option>
                  <option value="Pending">Pending</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
              </select>
          </div>
          <button type="button" class="remove-action-item btn danger">Remove</button>
      `;

      container.appendChild(div);

      // Add event listener for removing action items
      div.querySelector(".remove-action-item").addEventListener("click", function() {
          div.remove();
      });
  });
});

  document.getElementById("addMeetingForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    // Collect action items
    let actionItems = [];
    document.querySelectorAll("#action-items-container .action-item").forEach(item => {
      actionItems.push({
        item: item.querySelector('input[name="action_item"]').value,
        responsible: item.querySelector('input[name="responsible"]').value,
        due_date: item.querySelector('input[name="due_date"]').value,
        status: item.querySelector('select[name="status"]').value
      });
    });

    formData.append("action_items", JSON.stringify(actionItems));

    // Send the data via Fetch API
    fetch(form.action, {
      method: form.method,
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert("Meeting added successfully!");
        fetchCustomerDetails(data.customer_id);
        closeMeetingModal();
      } else {
        alert("Failed to add meeting.");
      }
    })
    .catch(error => {
      console.error("Error:", error);
      alert("An error occurred while adding the meeting.");
    });
  });

  function closeMeetingModal() {
    const modal = document.getElementById("addMeetingModal");
      modal.style.display = 'none';
  }
  
  
function addKeyframeAnimations() {
  if (!document.getElementById('custom-animations')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'custom-animations';
    styleSheet.textContent = `
      @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
      }
      
      @keyframes modalFadeOut {
        from {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
        to {
          opacity: 0;
          transform: translateY(50px) scale(0.9);
        }
      }
      
      @keyframes highlight {
        0% { background-color: rgba(52, 152, 219, 0.2); }
        100% { background-color: transparent; }
      }
    `;
    document.head.appendChild(styleSheet);
  }
}

function attachEditContactListeners() {
  document.querySelectorAll(".edit-contact-btn").forEach(button => {
      button.addEventListener("click", function() {
          // Extract contact details from the button's data attributes
          const contactId = this.getAttribute("data-id");
          const contactName = this.getAttribute("data-name");
          const contactRole = this.getAttribute("data-role");
          const contactEmail = this.getAttribute("data-email");
          const contactPhone = this.getAttribute("data-phone");

          // Populate the modal fields
          document.getElementById("editContactId").value = contactId;
          document.getElementById("editContactName").value = contactName;
          document.getElementById("editContactRole").value = contactRole;
          document.getElementById("editContactEmail").value = contactEmail;
          document.getElementById("editContactPhone").value = contactPhone;

          // Show the modal
          document.getElementById("editContactModal").style.display = "block";
      });
  });
}


function attachViewOrderListeners() {
  document.querySelectorAll(".view-order").forEach(button => {
      button.addEventListener("click", function() {
          // Extract contact details from the button's data attributes
          const orderID = this.getAttribute("data-id");
          const orderNo = this.getAttribute("data-orderNo");
          const material = this.getAttribute("data-material");
          const amount = this.getAttribute("data-amount");
          const goal = this.getAttribute("data-goal");
          const date = this.getAttribute("data-date");
          const orderFile = this.getAttribute("data-orderFile");
          const invoiceFile = this.getAttribute("data-orderInvoice");
          const notes = this.getAttribute("data-notes");


          // Populate the modal fields
          document.getElementById("viewOrderMaterial").textContent = material; // Input field
          document.getElementById("viewOrderNo").textContent = orderNo; 
          document.getElementById("viewOrderAmount").textContent = amount;
          document.getElementById("viewOrderGoal").textContent = goal;
          document.getElementById("viewOrderDate").textContent = date; 
          document.getElementById("viewOrderNotes").textContent = notes; 


          const orderFileLink = document.getElementById("viewOrderFileLink");
          const invoiceFileLink = document.getElementById("viewinvoiceFileLink");

          if (orderFile && orderFile !== "null") {
            orderFileLink.href = "/static/uploads/" + orderFile;
            orderFileLink.style.display = "inline";
        } else {
            orderFileLink.textContent = "None";
        }
        
        if (invoiceFile && invoiceFile !== "null") {
            invoiceFileLink.href = "/static/uploads/" + invoiceFile;
            invoiceFileLink.style.display = "inline";
        } else {
          invoiceFileLink.textContent = "None";

        }

          // Show the modal
          document.getElementById("viewOrderModal").style.display = "block";
      });
  });
}

function attachViewMeetingListeners() {
  document.querySelectorAll(".view-meeting").forEach(button => {
      button.addEventListener("click", function() {
          const meetingID = this.getAttribute("data-id");
          const meetingTitle = this.getAttribute("data-title");
          const Attendees = this.getAttribute("data-attendees");
          const date = this.getAttribute("data-date");
          const summary = this.getAttribute("data-summary");


          // Populate the modal fields
          document.getElementById("viewMeetingTitle").textContent = meetingTitle; // Input field
          document.getElementById("viewMeetingAttendees").textContent = Attendees; 
          document.getElementById("viewMeetingDate").textContent = date;
          document.getElementById("viewMeetingSummary").textContent = summary;

    
          // Show the modal
          document.getElementById("viewMeetingModal").style.display = "block";
      });
  });
}


function attachViewUpdateListeners() {
  document.querySelectorAll(".view-update").forEach(button => {
      button.addEventListener("click", function() {
          const updateID = this.getAttribute("data-id");
          const updateTitle = this.getAttribute("data-title");
          const update = this.getAttribute("data-update");
          const date = this.getAttribute("data-date");
          const nextStep = this.getAttribute("data-nextStep");
          const file = this.getAttribute("data-file");
          const updateFile = this.getAttribute("data-updateFile");

          // Populate the modal fields
          document.getElementById("viewUpdateTitle").textContent =updateTitle; // Input field
          document.getElementById("viewUpdateUpdate").textContent = update; 
          document.getElementById("viewUpdateDate").textContent = date;
          document.getElementById("viewUpdateNextStep").textContent = nextStep;

          const updateFileLink = document.getElementById("viewUpdateFileLink");

          if (file !== "null") {
            updateFileLink.href = "/static/uploads/" + file;
            updateFileLink.style.display = "inline";
        } else {
          updateFileLink.textContent = "None";
        }

          // Show the modal
          document.getElementById("viewUpdateModal").style.display = "block";
      });
  });
}



function initApp() {
  displayCurrentDate();  
  setupEventListeners();

}


// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  addKeyframeAnimations();
  initApp();
});