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

// get the uploaded files
$(document).ready(function() {
    $("#submit-button").click(function() {
        // get uploaded files
        var fileInput1 = document.getElementById('file-input-1');
        var fileInput2 = document.getElementById('file-input-2');
        // extract uploaded files
        var str_request_1 = fileInput1.files[0]; // Get the file object
        var str_request_2 = fileInput2.files[0]; // Get the file object
        // form data
        var formData = new FormData();
        // file
        formData.append('str_request_1', str_request_1); // Append the file to the form data
        formData.append('str_request_2', str_request_2); // Append the file to the form data

        // post request
        $.ajax({
            url: '/submit_requests',
            type: 'POST',
            data: formData,
            processData: false,  // Prevent jQuery from automatically processing the data
            contentType: false,  // Prevent jQuery from setting the content type
            success: function(response) {
            	// Check if response is in the correct format
	            console.log(response); // Debugging line

	            // Create headers using filenames from the response
                var header1 = `<h3>${response.str_filename_1}</h3>`;
                var header2 = `<h3>${response.str_filename_2}</h3>`;

	            // show table
	            $('#response-table-1').html(header1 + response.df_html_1);
	            // show table
	            $('#response-table-2').html(header2 + response.df_html_2);
            },
            error: function(xhr, status, error) {
                // Handle errors
                console.error(xhr.responseText);
            }
        });
    });
});