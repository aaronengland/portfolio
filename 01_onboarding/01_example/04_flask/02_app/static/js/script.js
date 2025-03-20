window.addEventListener('load', function() {
    const loader = document.getElementById('loader');
    loader.classList.add('hidden');
});

// show tables
$('table.display').DataTable({
    searching: true,
    lengthChange: true,
    paging: true,
    info: true,
});

// submit form
// function submitForm() {
//     // Get form data
//     var formData = $('#values-form').serialize();

//     // Send AJAX request
//     $.ajax({
//         type: 'POST',
//         url: '/update_form',
//         data: formData,
//         success: function(response) {
//             // show table
//             $('#tableWrapper').html(response.df_theo_rev);
//             $('table[id^="DataTables_Table_"]').each(function() {
//                 $(this).DataTable().destroy();
//             });
//             $('table.display').DataTable({
//                 'order': [[2, 'desc']],
//                 'pageLength': 35,
//             });
//         },
//         error: function(error) {
//             console.error('Error:', error);
//         }
//     });
// }

$(document).ready(function() {
    $('#updateForm').on('submit', function(e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: '/update_values',
            data: $(this).serialize(),
            success: function(response) {
                if (response.error) {
                    console.error('Error:', response.error);
                } else {
                    console.log('Response:', response);
                    // Check if table_html exists in the response
                    if (response.df_theo_rev) {
                        console.log('Updated table HTML:', response.df_theo_rev);

                        // Destroy the existing DataTable before updating the HTML
                        if ($.fn.DataTable.isDataTable('.display')) {
                            $('.display').DataTable().destroy();
                        }

                        // Update the content of the table wrapper with the new table HTML
                        $('#tableWrapper').html(response.df_theo_rev)
                        // Reinitialize DataTables to apply sorting and pagination to the new table
                        $('table.display').DataTable({
                            'order': [[2, 'desc']],
                            'pageLength': 35,
                        });

                        // Ensure the DataTable initialization is logged
                        console.log('DataTable initialized.');
                    } else {
                        console.error('No df_theo_rev in response');
                    }
                }
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });
});