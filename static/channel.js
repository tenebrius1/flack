document.addEventListener('DOMContentLoaded', () => {
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    let messageForm = document.getElementById('message_form'),
        userList = document.getElementById("users_list"),
        nickname = localStorage.getItem("nickname"),
        prevNickname;
    
    // Converts the time to be in 24hr format 
    function checkTime(i) {
        return (i < 10) ? "0" + i : i;
    }
    var today = new Date(),
        h = checkTime(today.getHours()),
        m = checkTime(today.getMinutes());
        // Sets the variable time to be in the format eg. 15:53
        time = (h + ":" + m)

    $('#message').on('focus', function() {
        document.body.scrollTop = $(this).offset().top;
    });

    // Updates the channel's user list without reloading the page
    socket.on("current_user_list", data => {
        let remoteList = JSON.parse(data.users),
            li;
        while (userList.firstChild) {
            userList.removeChild(userList.firstChild);
        }

        for (let i = 0; i < remoteList.length; i++) {
            li = document.createElement("li");
            li.setAttribute("id", nickname)
            li.innerText = remoteList[i];
            userList.append(li);
        }
    });

    // Prevents the form from actually submitting 
    messageForm.addEventListener('submit', event => {
        event.preventDefault();
        // Grabs the msg the user want to send
        let msg = messageForm.message.value;
        // Trims any whitespace before and after the msg 
        msg = msg.trim();
        // Checks that the message being sent is not empty 
        if (msg !== "") {
            socket.emit('new_message', {'msg': msg});
            // Resets the input area to be empty after user finish sending message
            messageForm.message.value = null;
        }
    });

    socket.on("write_message", data => {
        let messageContainer = document.getElementById('message_list'),
            message = document.createElement("div"),
            receivedNickname = data.nickname,
            receivedText = data.message,
            author_paragraph = document.createElement("p"),
            text_paragraph = document.createElement("p"),
            msg_time = document.createElement("sub");
            msg_time.style.margin = "5px";
            msg_time.innerText = time;

        message.classList.add("message_element");
        author_paragraph.classList.add("has-text-weight-light", "message_author");
        author_paragraph.innerText = receivedNickname;
        text_paragraph.classList.add("box", "message_text");
        text_paragraph.innerText = receivedText;
        if (prevNickname !== receivedNickname) {
            message.append(author_paragraph);
            message.append(text_paragraph);
            message.append(msg_time);
        } 

        if (receivedNickname === nickname) {
            message.classList.add("has-text-right");
            text_paragraph.classList.add("current_user");
            message.append(msg_time);
            message.append(text_paragraph);
        }

        if (prevNickname === receivedNickname) {
            message.classList.add("message_author_repeated");
        }
        
        messageContainer.append(message);
        messageContainer.scrollIntoView({ block: "end", behavior: "smooth" });
        prevNickname = receivedNickname;
    });
});



