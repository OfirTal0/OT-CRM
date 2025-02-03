// Ensures the script runs only after the DOM is fully loaded

document.addEventListener('DOMContentLoaded', () => {

        // Update modal buttons
    const addUpdateBtn = document.querySelector('.add-update-btn');
    const closeUpdateBtn = document.querySelector('.close-btn');
    if (addUpdateBtn) addUpdateBtn.addEventListener('click', (e) => { e.preventDefault(); openModal('updateModal'); });
    if (closeUpdateBtn) closeUpdateBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal('updateModal'); });
    
        // Order modal buttons
    const addOrderBtn = document.querySelector('.add-order-btn');
    const closeOrderBtn = document.querySelector('.close-order-btn');
    if (addOrderBtn) addOrderBtn.addEventListener('click', (e) => { e.preventDefault(); openModal('orderModal'); });
    if (closeOrderBtn) closeOrderBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal('orderModal'); });
    
        // Edit customer details
    const editDetailsBtn = document.querySelector('.edit-details');
    if (editDetailsBtn) editDetailsBtn.addEventListener('click', (e) => { e.preventDefault(); toggleEditDetails(); });
    
    const orderDetailsBtn = document.querySelector('.toggle-order-details-btn');
    if (orderDetailsBtn) orderDetailsBtn.addEventListener('click', (e) => { e.preventDefault(); toggleOrderDetails(orderId); });
    
    const meetingDetailsBtn = document.querySelector('.toggle-meeting-details-btn');
    if (meetingDetailsBtn) meetingDetailsBtn.addEventListener('click', (e) => { e.preventDefault(); toggleMeetingDetails(orderId); });
    
    const meetingUpdateBtn = document.querySelector('.toggle-update-details-btn');
    if (meetingUpdateBtn) meetingUpdateBtn.addEventListener('click', (e) => { e.preventDefault(); toggleUpdateDetails(updateId); });
  
    const addCustomerBtn = document.querySelector('.add-customer-btn');
    if (addCustomerBtn) {
        addCustomerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleAddCustomerForm();
        });
    }

    function toggleListView() {
        const customerList = document.querySelector('.customer-list');
        const customerDetails = document.querySelector('.customer-details');
        const addCustomerSection = document.querySelector('.add-customer-section');
        
        if (customerList) customerList.style.display = 'block';
        if (customerDetails) customerDetails.style.display = 'block';
        if (addCustomerSection) addCustomerSection.style.display = 'none';
    }

    function closeListView() {
        // Logic for closing the list view, e.g., hide the element
        document.querySelector('.customer-list').style.display = 'none';
    }

    document.querySelector('.close-list-view-btn').addEventListener('click', closeListView);

    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();  // Get the value entered in the search
            document.querySelectorAll('.customer-item').forEach(item => {
                const customerName = item.querySelector('h3').textContent.toLowerCase();  // Ensure you are getting the name from the <h3> tag
                item.style.display = customerName.includes(searchTerm) ? 'block' : 'none';  // Show or hide based on search term
            });
        });
    }

    function toggleEdit(section, id) {
        const form = document.querySelector(`#${section}-${id} .edit-${section}-form`);
        const display = document.querySelector(`#${section}-${id} .edit-display`);
        if (form && display) {
            if (form.style.display === 'none' || form.style.display === '') {
                form.style.display = 'block';
                display.style.display = 'none';
            } else {
                form.style.display = 'none';
                display.style.display = 'block';
            }
        }
    }
    

    const customerListBtn = document.querySelector('.customer-list-btn');
    if (customerListBtn) {
        customerListBtn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleListView();
        });
    }


    const openContactModalBtn = document.querySelector('.add-contact-btn');
    const closeContactModalBtn = document.querySelector('.close-contact-btn');
    if (openContactModalBtn) openContactModalBtn.addEventListener('click', () => openModal('contactModal'));
    if (closeContactModalBtn) closeContactModalBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal('contactModal'); });

    // Set active customer item
    function setActive(selectedForm) {
        document.querySelectorAll('.customer-item').forEach(item => item.classList.remove('active'));
        selectedForm.classList.add('active');
    }

    function loadMore(section, itemsPerPage) {
        const items = document.querySelectorAll(`.timeline-item[id^="${section}-"]`);
        const loadMoreBtn = document.getElementById(`load-more-${section}-btn`);
        let visibleCount = 0;
    
        // Count currently visible items
        items.forEach(item => {
            if (item.style.display !== 'none') visibleCount++;
        });
    
        // Show the next batch of items
        for (let i = visibleCount; i < visibleCount + itemsPerPage; i++) {
            if (items[i]) {
                items[i].style.display = 'block';
            }
        }
    
        // Hide the button if all items are visible
        if (visibleCount + itemsPerPage >= items.length) {
            loadMoreBtn.style.display = 'none';
        }
    }
    
    // Initialize all sections with hidden items
    function initializeSections(sections, itemsPerPage) {
        sections.forEach(section => {
            const items = document.querySelectorAll(`.timeline-item[id^="${section}-"]`);
            const loadMoreBtn = document.getElementById(`load-more-${section}-btn`);
    
            // Hide all items initially
            items.forEach(item => (item.style.display = 'none'));
    
            // // Add click event for "Load More" button
            loadMoreBtn.addEventListener('click', () => loadMore(section, itemsPerPage));
    
            // // Show the first batch of items
            loadMore(section, itemsPerPage);
        });
    }
    
    // Call initializeSections for your sections
    initializeSections(['meeting', 'order', 'update'], 3);


    // Toggle visibility of Add Customer section
    function toggleAddCustomerForm() {
        const customerDetails = document.querySelector('.customer-details');
        const addCustomerSection = document.querySelector('.add-customer-section');
        const customerList = document.querySelector('.customer-list');
        if (customerList) customerList.style.display = 'none';
        if (customerDetails) customerDetails.style.display = 'none';
        if (addCustomerSection) addCustomerSection.style.display = 'block';
    }

    // Open and close modals
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = 'flex';
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = 'none';
    }


    window.closeListView = closeListView;


    function toggleEditDetails() {
        const form = document.getElementById('edit-details-form');
        const displayProfile = document.querySelector('.display-profile');
        const editButton = document.querySelector('.edit-details');
        
        if (form.style.display === 'none' || form.style.display === '') {
            // Show the form and hide the profile display
            form.style.display = 'block';
            if (displayProfile) displayProfile.style.display = 'none';
            
            // Change button text to "Close Edit"
            if (editButton) editButton.textContent = 'Close Edit';
        } else {
            // Hide the form and show the profile display
            form.style.display = 'none';
            if (displayProfile) displayProfile.style.display = 'block';
            
            // Change button text back to "Edit Details"
            if (editButton) editButton.textContent = 'Edit Details';
        }
    }

    
    function toggleOrderDetails(orderId) {
        const details = document.getElementById(`details-order-${orderId}`);
        const button = document.getElementById(`order-btn-${orderId}`);
        if (details.style.display === 'none' || details.style.display === '') {
            details.style.display = 'block';
            button.textContent = 'Close';
        } else {
            details.style.display = 'none';
            button.textContent = 'Open More';
        }
    }
    window.toggleOrderDetails = toggleOrderDetails;

    function toggleMeetingDetails(meetingId) {
        const details = document.getElementById(`details-meeting-${meetingId}`);
        const button = document.getElementById(`meeting-btn-${meetingId}`);
        if (details.style.display === 'none' || details.style.display === '') {
            details.style.display = 'block';
            button.textContent = 'Close';
        } else {
            details.style.display = 'none';
            button.textContent = 'Open More';
        }
    }
    window.toggleMeetingDetails = toggleMeetingDetails;

    function toggleUpdateDetails(updateId) {
        const details = document.getElementById(`details-update-${updateId}`);
        const button = document.getElementById(`update-btn-${updateId}`);
        if (details.style.display === 'none' || details.style.display === '') {
            details.style.display = 'block';
            button.textContent = 'Close';
        } else {
            details.style.display = 'none';
            button.textContent = 'Open More';
        }
    }
    window.toggleUpdateDetails = toggleUpdateDetails;

    const openMeetingModalBtn = document.querySelector('.add-meeting-btn');
    if (openMeetingModalBtn) {
        openMeetingModalBtn.addEventListener('click', () => {
            openModal('meeting-modal');
        });
    }


    const closeMeetingModalBtn = document.querySelector('.close-meeting-btn');
    if (closeMeetingModalBtn) closeMeetingModalBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal('meeting-modal'); });


    // Customer item click
    document.querySelectorAll('.customer-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            setActive(item);
            item.submit();
        });
    });



    // Expose toggleEdit globally
    window.toggleEdit = toggleEdit;


    const addActionItemBtn = document.getElementById('add-action-item-btn');
    const actionItemsList = document.getElementById('action-items-list');



    // Function to create and add a new action item form
    function addActionItem() {
        const actionItemDiv = document.createElement('div');
        actionItemDiv.classList.add('action-item');

        actionItemDiv.innerHTML = `
            <div class="info-item">
                <label for="action-item">Action Item:</label>
                <input type="text" name="action_item" required>
            </div>
            <div class="info-item">
                <label for="responsible">Responsible:</label>
                <input type="text" name="responsible" required>
            </div>
            <div class="info-item">
                <label for="due-date">Due Date:</label>
                <input type="date" name="due_date" required>
            </div>
            <div class="info-item">
                <label for="status">Status:</label>
                <select name="status" required>
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                </select>
            </div>
            <button type="button" class="remove-action-item-btn">Remove</button>
        `;
        
        // Add the new action item to the list
        actionItemsList.appendChild(actionItemDiv);

       // Add event listener to remove the action item
       const removeBtn = actionItemDiv.querySelector('.remove-action-item-btn');
       removeBtn.addEventListener('click', () => {
           actionItemsList.removeChild(actionItemDiv);
       });
   }
    
// Event listener for the "Add Action Item" button
if (addActionItemBtn) {
    addActionItemBtn.addEventListener('click', addActionItem);
}

document.querySelector('#meeting-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent normal form submission
    
    const actionItems = [];
    
    // Loop through each action item and collect its data
    document.querySelectorAll('.action-item').forEach(item => {
        const actionItem = item.querySelector('input[name="action_item"]').value;
        const responsible = item.querySelector('input[name="responsible"]').value;
        const dueDate = item.querySelector('input[name="due_date"]').value;
        const status = item.querySelector('select[name="status"]').value;

        actionItems.push({ item: actionItem, responsible: responsible, due_date: dueDate, status: status});
    });
    
    // Add the action items to the form as a hidden input
    const actionItemsInput = document.createElement('input');
    actionItemsInput.type = 'hidden';
    actionItemsInput.name = 'action_items';
    actionItemsInput.value = JSON.stringify(actionItems); // Convert to JSON string
    this.appendChild(actionItemsInput);
    
    // Submit the form
    this.submit();
});


});

document.addEventListener('DOMContentLoaded', function() {
    // Get all "Add Action Item" buttons
    const addActionButtons = document.querySelectorAll('#add-action-item-btn');

    // Loop over each button and attach the event listener
    addActionButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Get the table body where action items will be added
            const tableBody = button.closest('.edit-meeting-form').querySelector('#action-items-table');
              // Create a new row
              const newRow = document.createElement('tr');
              newRow.classList.add('action-item-row');
              
              // Add input fields to the new row
              newRow.innerHTML = `
                  <td><input type="text" name="action_item" required></td>
                  <td><input type="text" name="responsible" required></td>
                  <td><input type="date" name="due_date" required></td>
                  <td>
                      <select name="status" required>
                          <option value="Pending">Pending</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                      </select>
                  </td>
                  <td>
                      <button type="button" class="remove-action-item-btn" onclick="removeActionItem(this)">Remove</button>
                  </td>
              ;`
  
              // Append the new row to the table body
              tableBody.appendChild(newRow);
          });
      });
  });
  
  function removeActionItem(button) {
      // Remove the row of the clicked "Remove" button
      const row = button.closest('tr');
      row.remove();
  }
  
  
function loadMoreContacts(itemsClass, itemsPerPage) {
    const items = document.querySelectorAll(`.${itemsClass}`); // Select all contact items
    const loadMoreBtn = document.getElementById('load-more-contact-btn');
    let visibleCount = 0;

    // Count currently visible items
    items.forEach(item => {
        if (item.style.display !== 'none') visibleCount++;
    });

    // Show the next batch of items
    for (let i = visibleCount; i < visibleCount + itemsPerPage; i++) {
        if (items[i]) {
            items[i].style.display = 'block'; // Make the item visible
        }
    }

    // Hide the button if all items are visible
    if (visibleCount + itemsPerPage >= items.length) {
        loadMoreBtn.style.display = 'none';
    }
}

// Initialization logic
document.addEventListener('DOMContentLoaded', () => {
    const itemsClass = 'contact-card'; // Class name of contact items
    const itemsPerPage = 3; // Number of items to show per click
    const loadMoreBtn = document.getElementById('load-more-contact-btn');
    const contacts = document.querySelectorAll(`.${itemsClass}`);

    // Initially hide all items
    contacts.forEach(item => (item.style.display = 'none'));

    // Show the first batch of items
    loadMoreContacts(itemsClass, itemsPerPage);

    // Add click event to the "Load More Contacts" button
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => loadMoreContacts(itemsClass, itemsPerPage));
    }
});

window.onscroll = function() {
    const button = document.getElementById("upButton");
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        button.style.display = "block"; // Show the button
    } else {
        button.style.display = "none"; // Hide the button
    }
};

// Function to scroll to the top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}
