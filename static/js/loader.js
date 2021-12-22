$(document).ready(function() {
    $("#btnFetch").click(function() {
      // disable button
      $("#btnFetch").prop("disabled", true);
      // add spinner to button
      $("#btnFecth").html(
        `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
      );
    });
});