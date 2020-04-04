var socket_url = $("#game-container").attr('data-socket-url')

var log_to_page = false

const coreapi = window.coreapi
const schema = window.schema

let auth = new coreapi.auth.SessionAuthentication({
    csrfCookieName: 'csrftoken',
    csrfHeaderName: 'X-CSRFToken'
})

let client = new coreapi.Client({auth: auth})

var game_id = $('#game-container').attr('data-game-id')
var buttons = ['btn0', 'btn1', 'btn2', 'btn3', 'btn4']

var role = $('#game-container').attr('data-role')
var active = $('#game-container').attr('data-active')

var delay = 800
var wrong_answer_pause = 7000

if (log_to_page){_log_to_page()}

// Check, if game is active

// REWRITE THAT GOVHISHCHE BRO!!111
if (active) { try{

    var socket = new WebSocket('ws://'+socket_url)

    socket.onopen = function (event) {
        socket.send('game_id='+game_id)
        console.log('ws connection open with game ', game_id);
    }

    // Switch for managing ws messages

    disable_all_buttons()

    socket.onmessage = function (event) {

        payload = JSON.parse(event.data)
        switch(payload['status']) {

            case 'initiate':
                console.log('received initiate')
                initiate()
                break

            case 'join':
                console.log('received join')
                initiate()
                break

            case 'refresh':
                if (payload['performed_action'] == role)
                    console.log('received refresh')
                    initiate()
                    break

            case 'miss':
    //            Expected payload json:
    //
    //            {status: 'miss',
    //             data:{
    //                   right_answer: str,
    //                   performed_action: 'host' or 'guest',
    //                   hp_rest: int;
    //                   next_question:{text: str,
    //                                  choices: list}}}
                console.log('received miss')

                animate_miss(payload['data']['performed_action'])

                set_shots(payload['data']['performed_action'], 0)
                set_power(payload['data']['performed_action'])

                setTimeout(function(){
                    $('#'+payload['data']['performed_action']+'_hp').text(payload['data']['hp_rest'])
                }, delay)

                if (payload['data']['performed_action'] == role) {

                    let right_button = find_button_by_text(payload['data']['right_answer']);
                    let initial_color_background = right_button.style.backgroundColor;
                    let initial_color_text = right_button.style.color;
                    right_button.style.backgroundColor = 'green';
                    right_button.style.color = 'white';

                    setTimeout(function(){
                        right_button.style.backgroundColor = initial_color_background;
                        right_button.style.color = initial_color_text;
                        enable_all_buttons();

                        set_question(payload['data']['next_question']['question_text'])
                        set_buttons(payload['data']['next_question']['choices'])

                    }, wrong_answer_pause)
                }

                break


            case 'right_answer':
    //            Expected payload json:
    //
    //            {status: 'right_answer',
    //             data:{performed_action: 'host' or 'guest',
    //                   right_answers_sum: int,
    //                   next_question:{text: str,
    //                                  choices: list}}}

                console.log('received right answer')
                animate_right(payload['data']['performed_action'])

                set_shots(payload['data']['performed_action'], payload['data']['right_answers_sum'])
                set_power(payload['data']['performed_action'])

    //          if you done that action:
                if (payload['data']['performed_action'] == role){

                    console.log('next question: ', payload['data']['next_question'])

                    set_question(payload['data']['next_question']['question_text'])
                    set_buttons(payload['data']['next_question']['choices'])
                    enable_all_buttons()
                }

                break

            case 'attack':

                console.log('received attack')
                let was_attacked;

                if (payload['data']['performed_action'] == 'host'){
                    was_attacked = 'guest'
                } else {
                    was_attacked = 'host'
                }

    //          if enemy attacked you
                if (payload['data']['performed_action'] != role ){

                    console.log('attack')
                    animate_attack(payload['data']['performed_action'])
                }

                setTimeout(function() {

                    set_shots(payload['data']['performed_action'], 0)
                    set_power(payload['data']['performed_action'])
                    $('#'+was_attacked+'_hp').text(payload['data']['hp_rest'])
                    enable_all_buttons()

                }, get_shots(payload['data']['performed_action'])*delay+delay)

                break

            case 'finish':
                console.log('received finish')

                setTimeout( function() {

                    invoke_modal(payload['data']['winner'])

                }, get_shots(payload['data']['performed_action'])*delay+delay)

                break
        }
    }

    socket.onclose = function(event){
        if(event.wasClean){
            console.log('Clean connection end')
        }else{
            console.log('Connection broken')
        }
    };

    socket.onerror = function(error){
        console.log(error);
    }

    window.onbeforeunload = function() {
        console.log('close socket manually')
        socket.close()
    }

    }catch(err){console.log(err)}
}

function initiate()
{
    let action=['games','read'];
    client.action(schema, action, {'id':game_id}).then(function(result){

//        expected json schema:
//        result {
//            'id': game_id,
//            'topic': game topic str,
//            'host': host.name str,
//            'host_hp': int,
//            'host_right_answers': int,
//            'host_is_sexy': boolean,
//            'guest': guest.name str,
//            'guest_hp': int,
//            'guest_right_answers': int,
//            'question_text': str,
//            'choices': {
//                list of {'choice_id': id,
//                         'choice_text': str}
//            }
//        }

        console.log('question get in initiate '+result['question_text'])

        $('#greetings').css('display', 'none')
        $('#cowboy_left').css('display', 'block')

        if (result['guest'] == 'Nobody joined yet'){
            set_header(result)
            set_question('Wait for opponent, plz')

        } else {

           $('#cowboy_right').css('display', 'block')
           set_question(result["question_text"])
           create_buttons(result['choices'].length)
           set_buttons(result['choices'])
           set_header(result)
           enable_all_buttons()
       }
    })
}


function create_buttons(choices_num){

    if ($('.btn').length < 5) {
        buttons_box = $('#buttons-box')
        for (i = 0; i < choices_num; i++){
            buttons_box.append('<button id="btn' + i + '" class="btn choice btn-outline-dark"> </button>')
        }
    }
}


function set_question(text) {

    if (text.startsWith('. ')) {
        text = text.slice(2);
    }
    $('#question-text').html(text);
}


function set_header(result) {

       $('#host').text(result['host'])
       $('#host_hp').text(result['host_hp'])
       $('#guest_hp').text(result['guest_hp'])
       set_shots('host', result['host_right_answers'])
       set_power('host')
       set_shots('guest', result['guest_right_answers'])
       set_power('guest')
       $('#guest').text(result['guest'])
}

function set_buttons(choices) {

    create_buttons(choices.length)

    console.log(choices)

    for (i=0; i < buttons.length; i++)
    {
    button = $('#'+buttons[i]);
    button.text(choices[i]['choice_text']);
    button.attr('onclick', String('answer('+choices[i]['choice_id']+')'))
    }
}

        ///////////////////////////
        // shots and power block //
        ///////////////////////////

function set_shots(role, shots){
    $('#'+role+'_shots').attr('data-shots', shots)
}

function set_power(role){
    shots = get_shots(role)
    $('#'+role+'_shots').text(get_power(shots))
}

function get_shots(role) {
    return parseInt($('#'+role+'_shots').attr('data-shots'))
}

function get_power(shots){
    return shots*5+shots**2
}


        //////////////////////////
        // player actions block //
        //////////////////////////

function answer(answer_id)
{
    disable_all_buttons()
    let action=['games','answer'];
    client.action(schema, action, {'id': game_id, 'answer_id': answer_id})
}


function attack()
{
    if(get_shots(role) > 0){
        let action=['games','attack'];
        client.action(schema, action, {'id': game_id})
        animate_attack(role)
    }
}

function surrender()
{
    if (confirm("Are you sure?")) {
        let action=['games','surrender'];
        client.action(schema, action, {'id': game_id})

    }
}


        //////////////////////
        //            block //
        //////////////////////


function find_button_by_text(text) {

    /* Hello! I'm Kostyl! Really nice to meet you here!
       I'm maybe not the best way, but simplest, so, that's why I'm here.
       Good bye! */

    var buttons = document.getElementsByTagName("button");
    var found;

    for (var i = 0; i < buttons.length; i++) {
      if (buttons[i].textContent == text) {
        found = buttons[i];
        break;
      }
    }
    return found;
}


function disable_all_buttons() {
    var all_btns = document.getElementsByClassName('choice')
    for (i=0; i < all_btns.length; i++){
        all_btns[i].disabled = true;
    }
}

function enable_all_buttons(){
    var all_btns = document.getElementsByClassName('choice')
    for (i=0; i < all_btns.length; i++){
        all_btns[i].disabled = false;
    }
}

        //////////////////////
        // Animations block //
        //////////////////////

function animate_miss(missed){

    let miss = $('#'+missed+'_miss');
    miss.css('display', 'block')
    let pos = 0
    let miss_interval = setInterval(frame, 50)

    function frame(){
        if (pos == 70) {
            clearInterval(miss_interval)
            miss.css('display', 'none')
            miss.css('top', '0px')
        } else {
            pos = pos + 5
            miss.css('top', pos+'px')
        }
    }
}

function animate_right(righted){

    let right = $('#'+righted+'_right');
    right.css('display', 'block')
    let pos = 70
    let right_interval = setInterval(frame, 50)

    function frame(){
        if (pos == 0) {
            clearInterval(right_interval)
            right.css('display', 'none')
            right.css('top', '80px')
        } else {
            pos = pos - 5
            right.css('top', pos+'px')
        }
    }
}

function animate_attack(attacking) {

    disable_all_buttons()

    if (attacking == 'host'){

        var cowboy = $('#cowboy_left')
        var cowboy_idle_anim = cowboy_left_idle
        var cowboy_shoot_anim = cowboy_left_shoot
        var blood = $('#blood_right')
        var blood_anim = blood_right
        var shots = get_shots('host')

    }
    if (attacking == 'guest'){

        var cowboy = $('#cowboy_right')
        var cowboy_idle_anim = cowboy_right_idle
        var cowboy_shoot_anim = cowboy_right_shoot
        var blood = $('#blood_left')
        var blood_anim = blood_left
        var shots = get_shots('guest')
    }

    let counter = 0;
    let interval = setInterval(function() {

        if(counter >= shots) {

            cowboy.attr('src', cowboy_idle_anim)
//            console.log('set iddle anim')
            blood.attr('src', '')
            clearInterval(interval);
            return 0;
        }

        cowboy.attr('src', cowboy_shoot_anim)
        console.log('set shooting anim')
        blood.attr('src', blood_anim)
//        console.log('set bleeding')
//        console.log(counter)

        counter++
    }, delay)
}



        /////////////////
        // Modal block //
        /////////////////


var modal = $('#ContainerModal')
var span = $('#close')

span.attr('onclick', "close_modal()")

function invoke_modal(winner) {
    $('#winner').text(winner+' has won! Congratz!')
    modal.css('display', 'block')
}

function close_modal() {
    window.location.href = "/index/"
}

//$(window).on("unload", function(e) {
//    console.log("page refresh");
//    if (game_id) {
//        socket.send('drop me')
//    }
//});

function _log_to_page() {
    var old = console.log;
    var logger = document.getElementById('mylog');
    console.log = function () {
      for (var i = 0; i < arguments.length; i++) {
        if (typeof arguments[i] == 'object') {
            logger.innerHTML += (JSON && JSON.stringify ? JSON.stringify(arguments[i], undefined, 2) : arguments[i]) + '<br />';
        } else {
            logger.innerHTML += arguments[i] + '<br />';
        }
      }
    }
};


