document.addEventListener('DOMContentLoaded', () => {
    userList = document.getElementById("users_list");
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on("current_user_list", data => {
        let remoteList = JSON.parse(data.users),
            li;
        console.log(remoteList);
        while (userList.firstChild) {
            userList.removeChild(userList.firstChild);
        }

        for (let i = 0; i < remoteList.length; i++) {
            li = document.createElement("li");
            li.innerText = remoteList[i];
            userList.append(li);
        }
    });
});