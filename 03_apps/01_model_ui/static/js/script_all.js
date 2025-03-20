window.addEventListener('load', function() {
	const loader = document.getElementById('loader');
	loader.classList.add('hidden');
});

$(document).ready(function() {
	$("#submit-button").click(function() {
		// input
		var int_income = $('#income-input').val() || '3500';
		var flt_amtfinanced = $('#amtfinanced-input').val() || '20000';
		var flt_bookvalue = $('#bookvalue-input').val() || '16000';
		var int_mileage = $('#mileage-input').val() || '100000';
		var int_bk = $('#bk-input').val() || '0';
		var int_franchise = $('#franchise-input').val() || '1';
		var int_class = $('#class-input').val() || '1';
		var str_state = $('#state-input').val() || 'Utah';
		
		// file
		var fileInput = document.getElementById('file-input');
		var str_request = fileInput.files[0]; // Get the file object
		// form data
		var formData = new FormData();

		// input
		formData.append('int_income', int_income);
		formData.append('flt_amtfinanced', flt_amtfinanced);
		formData.append('flt_bookvalue', flt_bookvalue);
		formData.append('int_mileage', int_mileage);
		formData.append('int_bk', int_bk);
		formData.append('int_franchise', int_franchise);
		formData.append('int_class', int_class);
		formData.append('str_state', str_state);
		
		// file
		formData.append('str_request', str_request); // Append the file to the form data

		// post request
		$.ajax({
			url: '/parse_payload',
			type: 'POST',
			data: formData,
			processData: false,  // Prevent jQuery from automatically processing the data
			contentType: false,  // Prevent jQuery from setting the content type
			success: function(response) {
				// extract data from response
				var str_filename = response.str_filename

				$('#error-message').hide();  // Hide the error message element
				
				// add header
				$('#response-output').prev('h3').remove(); // Remove existing <h3> if any
				$('#response-output').before(`<h3><center>Score Output (${str_filename}):</center></h3>`);
				// create/update table
				$('#response-output').html(response.df_html_score);
				// diplay table
				$('table.display').DataTable();

				// add header for df_html_score table
				$('#response-output').append('<h3><center>Features Output:</center></h3>');
				// append df_html_score
				$('#response-output').append(response.df_html_fin);
				// initialize DataTable for df_html_score
				$('table.display').DataTable();

				// add header for df_html_counters
				$('#response-output').append('<h3><center>Counter Offers:</center></h3>');
				// append df_html_counters
				$('#response-output').append(response.df_html_counters);
				// initialize DataTable for df_html_score
				$('table.display').DataTable();

				$('#response-output').show();
			},
			error: function(xhr, status, error) {
				// Handle errors
				console.error(xhr.responseText);
				$('#error-message').text('An error occurred while processing your request. Please try again.');
				$('#error-message').show(); // Show the error message

				// hide things
				$('#response-output').prev('h3').remove();
				$('#response-output').hide();
			}
		});
	});
});