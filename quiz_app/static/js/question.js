const getWebSocketURI = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    return `${protocol}//${hostname}${port}/ws/team/`;
};

// Example usage
const websocketURI = getWebSocketURI();
console.log(websocketURI); // This will log the dynamically generated WebSocket URI

const socket = new WebSocket(getWebSocketURI())
// Connection closed
socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed');
});

socket.addEventListener('open', function (event) {
    console.log('WebSocket connection opened');
});

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Message received from server:', message);
    // Handle the message accordingly
    resolve_events(message)
};
function resolve_events(event_data){
    console.log(event_data)
    switch(event_data.type){
      case 'question_selected_event':
        question = event_data.message.question_id
        disableQuestion(question)
        break;
      case 'round_started_event':
        round_id = event_data.message.round_id
        localStorage.setItem('round_id', round_id)
        break;
      case 'no_running_round':
        localStorage.removeItem('round_id')
        localStorage.removeItem('roundTargetDate')
        localStorage.removeItem('targetDate')
        //clearInterval(roundTimerInterval)
        window.location.href = '/'
        break;
      case 'reset_round':
        localStorage.removeItem('round_id')
        localStorage.removeItem('roundTargetDate')
        localStorage.removeItem('targetDate')
        // clearInterval(roundTimerInterval)
        window.location.href = '/'
        break;
      case 'round_end_event':
        localStorage.removeItem('round_id')
        localStorage.removeItem('roundTargetDate')
        localStorage.removeItem('targetDate')
        //clearInterval(roundTimerInterval)
        window.location.href = '/'
        break;
      case 'answer':
        answer_text = event_data.answer_text
        labels = document.getElementsByTagName('label')
        for( let i = 0; i < labels.length; i++){
            console.log(labels[i])
            if(labels[i].innerHTML === answer_text){
                console.log(labels[i])
                labels[i].classList.remove('btn-outline-dark')
                labels[i].classList.add('bg-success')
                break;
            }
        }
        setTimeout(() => {
            window.location.href = '/'
        }, 10000)
        break;
      case 'answer_sa':
            answer_text = event_data.answer_text
            answer = document.getElementById('answer')
            answer.innerHTML = answer_text
            answer.classList.remove('hidden')
            setTimeout(() => {
                window.location.href = '/'
            }, 10000)
            break;
      case 'round':
        localStorage.setItem('round_id', event_data.round_id)
        break;
    }
  }
// Function to update the countdown timer
function updateTimer() {
    // Get the target date and time from localStorage
    const targetDate = new Date(localStorage.getItem('targetDate'));
    
    // Update the countdown every second
    let timerInterval = setInterval(() => {
        // Get the current date and time
        const now = new Date().getTime();

        // Calculate the time remaining
        const timeRemaining = targetDate - now;
        console.log(timeRemaining)
        // If the countdown is finished, display a message
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            document.getElementById('timer').innerHTML = '00:00';
            localStorage.removeItem('targetDate');
            submit()
            // Navigate to the home page
            window.location.href = '/'

        } else {
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

            // Pad minutes and seconds with leading zeros if they are single-digit
            const paddedMinutes = minutes.toString().padStart(2, '0');
            const paddedSeconds = seconds.toString().padStart(2, '0');

            // Display the countdown timer
            document.getElementById('timer').innerHTML = `${paddedMinutes}:${paddedSeconds}`;
        }
    }, 1000); // Update every second
}

// Check if target date is stored in localStorage


// Update the countdown timer
window.onload = () => {
    if (!localStorage.getItem('targetDate')) {
        // Set the target date and time (replace with your desired date and time)
        const targetDate = new Date();
        targetDate.setSeconds(targetDate.getSeconds() + 45); // Example: 5 minutes from now
        localStorage.setItem('targetDate', targetDate);
        //emit event over a django channel about time up
    }
    updateTimer();
}
let choice_selected = null

const select_choice = (event) => {
    choice_selected = event.target.id
    console.log(choice_selected)
    //event.target.checked = true
    socket.send(JSON.stringify({
        type: 'ChoiceSelected', 
        choice_id: choice_selected, 
        team_id: document.getElementById('team_id').innerHTML,
        round_id: localStorage.getItem('round_id')
    }))
}

const submit = () => {
    console.log(choice_selected)
    localStorage.removeItem('targetDate');
    socket.send(JSON.stringify({
        type: 'QuestionAnswered',
        choice_id: choice_selected, 
        team_id: document.getElementById('team_id').innerHTML,
        round_id: localStorage.getItem('round_id')
    }))
    
}
let answer = null
const submit_sa = () => {
    
    localStorage.removeItem('targetDate');
    socket.send(JSON.stringify({
        type: 'QuestionAnsweredSA',
        answer_written: answer, 
        team_id: document.getElementById('team_id').innerHTML,
        round_id: localStorage.getItem('round_id')
    }))
}

const fill_answer = (event) => {
    answer = event.target.value
    console.log(answer)
    //event.target.checked = true
    socket.send(JSON.stringify({
        type: 'AnswerFilled', 
        answer_written: answer, 
        team_id: document.getElementById('team_id').innerHTML,
        round_id: localStorage.getItem('round_id')
    }))
}