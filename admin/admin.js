function show(id) {
    document.querySelectorAll("section").forEach(s => s.classList.remove("active"));
    document.getElementById(id).classList.add("active");
}

fetch("/admin/stats")
.then(r => r.json())
.then(d => {
    usersCount.innerText = "Users: " + d.users;
    uploadsCount.innerText = "Uploads: " + d.uploads;
    alertsCount.innerText = "Alerts: " + d.alerts;
});

fetch("/admin/users")
.then(r => r.json())
.then(users => {
    userTable.innerHTML = users.map(u =>
        `<tr>
            <td>${u.id}</td>
            <td>${u.name}</td>
            <td>${u.role}</td>
            <td>${u.status}</td>
        </tr>`
    ).join("");
});

fetch("/admin/logs")
.then(r => r.json())
.then(logs => {
    logList.innerHTML = logs.map(l =>
        `<li>[${l.level}] ${l.message} - ${l.time}</li>`
    ).join("");
});

function saveRecommendation() {
    fetch("/admin/recommendations", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            emotion: emotion.value,
            content: content.value
        })
    }).then(() => alert("Saved"));
}
