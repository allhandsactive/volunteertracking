function login () {
  const Authorization = 'Basic ' + window.btoa(document.getElementById('InputUsername').value + ':' + document.getElementById('InputPassword').value)
  $.ajax({
    type: 'POST',
    url: '/api/auth/login',
	  headers: { Authorization: Authorization },
    error: function (e) {
	    alert("Username or password incorrect");
	 }
  }).then(res => {
    console.log(res)
    if (res.status === 'user logged in') {
      location.href = '/index.html'
    }
  })
}

$(document).ready(function () {
  // should just call one function here
  $('#login-button').on('click', function (e) {
    e.preventDefault()
    login()
  })
  $('input').keyup(function (e) {
    if (event.which == 13) {
      e.preventDefault()
      login()
    }
  })
})
