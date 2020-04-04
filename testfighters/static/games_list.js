//WARNING!!11 I HARDCODED REDIRECT URL!!

console.log('WARNING!!11 I HARDCODED REDIRECT URL!!')

const coreapi = window.coreapi
const schema = window.schema

let auth = new coreapi.auth.SessionAuthentication({
    csrfCookieName: 'csrftoken',
    csrfHeaderName: 'X-CSRFToken'
})

let client = new coreapi.Client({auth: auth})

function join(id) {
    let password = $('#password_'+id).val()
    validation = $('#validation_'+id)

    if ($('#need_password_'+id).text() != 'No password') {

        if (password == "") {
            validation.text("Password not set");
            return 0
        }
    }

    let action=['games','join'];
    client.action(schema, action, {'id':id, 'password': password}).then(function(result){
        window.location.href = "/client/"+id+'/'
        }).catch(function(err){validation.text(
            'Something went wrong :( Maybe, you entered wrong password or already participate in a game.'
    )})
}
