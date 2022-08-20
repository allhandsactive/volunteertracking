$(document).ready(function () {
	$("#dataTable").DataTable({
		ajax: "/api/hours/month/all?per_page=100",
		columns: [
			{ data: "datetime", render: $.fn.dataTable.render.text() },
			{ data: "hours", render: $.fn.dataTable.render.text() },
			{ data: "description", render: $.fn.dataTable.render.text() },
		],
	});
});
