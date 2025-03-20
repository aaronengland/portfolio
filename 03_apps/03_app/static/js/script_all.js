window.addEventListener('load', function() {
	const loader = document.getElementById('loader');
	loader.classList.add('hidden');
});

$(document).ready(function() {
	$("#submit-button").click(function() {
		// file
		var fileInput = document.getElementById('file-input');
		var str_request = fileInput.files[0]; // Get the file object
		// form data
		var formData = new FormData();

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
				var str_decision = response.str_decision
				var str_color = response.str_color
				var str_filename = response.str_filename

				$('#error-message').hide();  // Hide the error message element

				// rm previous output
				$('#response-output-decision').prev('h3').remove();
				// decision
				$('#response-output-decision').before(`<h3 style="color: ${str_color};">${str_decision}</h3>`)

				// rm previous output
				$('#response-output-raw').prev('h3').remove();
				// add header
				$('#response-output-raw').before(`<h3><center>Raw Data (${str_filename}):</center></h3>`);
				// create/update table
				$('#response-output-raw').html(response.df_html_raw);
				// diplay table
				$('table.display').DataTable();

				// rm previous output
				$('#response-output-clean').prev('h3').remove();
				// add header
				$('#response-output-clean').before(`<h3><center>Clean Data (${str_filename}):</center></h3>`);
				// create/update table
				$('#response-output-clean').html(response.df_html_clean);
				// diplay table
				$('table.display').DataTable();

				// show plot
                $('#graphJSON_features').html(''); // clear plot
                $('#graphJSON_features').show(); // show plot container
                var graphs = JSON.parse(response.graphJSON_features);
                Plotly.newPlot('graphJSON_features', graphs, {});

				// rm previous output
				$('#response-output-features').prev('h3').remove();
				// add header
				$('#response-output-features').before(`<h3><center>Features (${str_filename}):</center></h3>`);
				// create/update table
				$('#response-output-features').html(response.df_html_features);
				// diplay table
				$('table.display').DataTable();

				// rm previous output
				$('#response-output-response').prev('h3').remove();
				// add header
				$('#response-output-response').before(`<h3><center>Response (${str_filename}):</center></h3>`);
				// create/update
				$('#response-output-response').html(`<pre>${response.dict_response}</pre>`);
				//$('#response-output-response').html(response.dict_response);

				// rm previous output
				$('#response-output-counters').prev('h3').remove();
				// add header
				$('#response-output-counters').before(`<h3><center>Counters (${str_filename}):</center></h3>`);
				// create/update table
				$('#response-output-counters').html(response.df_html_counters);
				// diplay table
				$('table.display').DataTable();

				// show output
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