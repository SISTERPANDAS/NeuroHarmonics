(function () {
    "use strict";

    var currentUserPage = 1;
    var currentEmotionPage = 1;
    var allUsers = [];

    function showSection(sectionId) {
        document.querySelectorAll(".admin-section").forEach(function (s) {
            s.classList.remove("active");
        });
        document.querySelectorAll(".admin-nav-btn").forEach(function (b) {
            b.classList.toggle("active", b.getAttribute("data-section") === sectionId);
        });
        var el = document.getElementById("section-" + sectionId);
        if (el) el.classList.add("active");
        if (sectionId === "users") loadUsers(1);
        if (sectionId === "emotions") loadEmotions(1);
        if (sectionId === "features") loadFeatures();
        if (sectionId === "recommendations") loadRecommendations();
        if (sectionId === "logs") loadLogs();
    }

    document.querySelectorAll(".admin-nav-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            showSection(this.getAttribute("data-section"));
        });
    });

    function api(path, options) {
        options = options || {};
        return fetch(path, {
            method: options.method || "GET",
            headers: options.headers || { "Content-Type": "application/json" },
            body: options.body
        }).then(function (r) {
            if (r.status === 401 || r.status === 403) {
                window.location.href = "/login";
                throw new Error("Unauthorized");
            }
            return r.json ? r.json() : r;
        });
    }

    // ---------- Dashboard (stats already in HTML; optional refresh) ----------
    function refreshStats() {
        api("/admin/stats").then(function (d) {
            var el = document.getElementById("stat-users");
            if (el) el.textContent = d.users;
            el = document.getElementById("stat-scans");
            if (el) el.textContent = d.total_emotion_scans != null ? d.total_emotion_scans : d.uploads;
            el = document.getElementById("stat-emotion");
            if (el) el.textContent = d.most_common_emotion || "—";
            el = document.getElementById("stat-sessions");
            if (el) el.textContent = d.active_sessions != null ? d.active_sessions : d.alerts;
        }).catch(function () {});
    }

    // ---------- Users ----------
    function loadUsers(page) {
        currentUserPage = page || 1;
        api("/admin/users?page=" + currentUserPage).then(function (d) {
            allUsers = d.users || [];
            var tbody = document.getElementById("users-tbody");
            var search = (document.getElementById("user-search") || {}).value || "";
            search = search.toLowerCase();
            var list = search
                ? allUsers.filter(function (u) {
                    return (u.username && u.username.toLowerCase().indexOf(search) >= 0) ||
                           (u.email && u.email.toLowerCase().indexOf(search) >= 0);
                })
                : allUsers;
            tbody.innerHTML = list.map(function (u) {
                var active = u.is_active !== false ? "Active" : "Inactive";
                return "<tr data-id=\"" + u.id + "\">" +
                    "<td>" + u.id + "</td>" +
                    "<td>" + (u.username || "—") + "</td>" +
                    "<td>" + (u.email || "—") + "</td>" +
                    "<td>" + (u.role || "user") + "</td>" +
                    "<td>" + (u.status || active) + "</td>" +
                    "<td>" + (u.total_scans || 0) + "</td>" +
                    "<td>" + (u.created_at || "—") + "</td>" +
                    "<td><button type=\"button\" class=\"admin-btn edit-user\" data-id=\"" + u.id + "\">Edit</button></td>" +
                    "</tr>";
            }).join("");
            renderPagination("users-pagination", currentUserPage, d.pages || 1, loadUsers);
            tbody.querySelectorAll(".edit-user").forEach(function (b) {
                b.addEventListener("click", function () { openUserModal(parseInt(this.getAttribute("data-id"), 10)); });
            });
            tbody.querySelectorAll("tr[data-id]").forEach(function (row) {
                row.addEventListener("click", function (e) {
                    if (e.target.tagName !== "BUTTON") openUserModal(parseInt(this.getAttribute("data-id"), 10));
                });
            });
        }).catch(function () {});
    }

    document.getElementById("users-refresh") && document.getElementById("users-refresh").addEventListener("click", function () {
        loadUsers(currentUserPage);
    });
    document.getElementById("user-search") && document.getElementById("user-search").addEventListener("input", function () {
        loadUsers(1);
    });

    function openUserModal(userId) {
        api("/admin/user/" + userId).then(function (u) {
            document.getElementById("modal-user-id").value = u.id;
            document.getElementById("modal-username").value = u.username || "";
            document.getElementById("modal-email").value = u.email || "";
            document.getElementById("modal-role").value = u.role || "user";
            document.getElementById("modal-is-active").checked = u.is_active !== false;
            var meta = "Scans: " + (u.total_scans || 0) + (u.last_login_at ? " · Last login: " + u.last_login_at : "");
            document.getElementById("modal-meta").textContent = meta;
            document.getElementById("user-modal").classList.add("show");
        }).catch(function () {});
    }

    document.querySelectorAll("[data-close=\"user-modal\"]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            document.getElementById("user-modal").classList.remove("show");
        });
    });
    document.getElementById("user-modal") && document.getElementById("user-modal").addEventListener("click", function (e) {
        if (e.target === this) this.classList.remove("show");
    });

    document.getElementById("user-save") && document.getElementById("user-save").addEventListener("click", function () {
        var id = document.getElementById("modal-user-id").value;
        if (!id) return;
        api("/admin/user/" + id + "/update", {
            method: "POST",
            body: JSON.stringify({
                username: document.getElementById("modal-username").value,
                email: document.getElementById("modal-email").value,
                role: document.getElementById("modal-role").value,
                is_active: document.getElementById("modal-is-active").checked
            })
        }).then(function () {
            document.getElementById("user-modal").classList.remove("show");
            loadUsers(currentUserPage);
        }).catch(function (e) { alert(e.message || "Failed to save"); });
    });

    document.getElementById("user-deactivate") && document.getElementById("user-deactivate").addEventListener("click", function () {
        if (!confirm("Deactivate this user (soft delete)?")) return;
        var id = document.getElementById("modal-user-id").value;
        if (!id) return;
        api("/admin/user/" + id + "/delete", { method: "POST" }).then(function () {
            document.getElementById("user-modal").classList.remove("show");
            loadUsers(currentUserPage);
        }).catch(function (e) { alert(e.message || "Failed"); });
    });

    // ---------- Emotions ----------
    function buildEmotionsQuery(page) {
        var q = "page=" + (page || 1);
        var emotion = document.getElementById("filter-emotion");
        if (emotion && emotion.value) q += "&emotion=" + encodeURIComponent(emotion.value);
        var from = document.getElementById("filter-date-from");
        if (from && from.value) q += "&date_from=" + encodeURIComponent(from.value);
        var to = document.getElementById("filter-date-to");
        if (to && to.value) q += "&date_to=" + encodeURIComponent(to.value);
        var conf = document.getElementById("filter-confidence");
        if (conf && conf.value !== "") q += "&min_confidence=" + encodeURIComponent(conf.value);
        return q;
    }

    function loadEmotions(page) {
        currentEmotionPage = page || 1;
        api("/admin/emotions?" + buildEmotionsQuery(currentEmotionPage)).then(function (d) {
            var tbody = document.getElementById("emotions-tbody");
            var list = d.emotions || [];
            tbody.innerHTML = list.map(function (e) {
                var conf = e.confidence_score != null ? Math.round(e.confidence_score * 100) + "%" : "—";
                return "<tr>" +
                    "<td>" + e.id + "</td>" +
                    "<td>" + (e.username || "user#" + e.user_id) + "</td>" +
                    "<td>" + (e.dominant_emotion || "—") + "</td>" +
                    "<td>" + conf + "</td>" +
                    "<td>" + (e.created_at || "—") + "</td>" +
                    "<td><button type=\"button\" class=\"admin-btn danger delete-emotion\" data-id=\"" + e.id + "\">Delete</button></td>" +
                    "</tr>";
            }).join("");
            renderPagination("emotions-pagination", currentEmotionPage, d.pages || 1, function (p) {
                loadEmotions(p);
            });
            tbody.querySelectorAll(".delete-emotion").forEach(function (b) {
                b.addEventListener("click", function () {
                    if (!confirm("Remove this log entry?")) return;
                    var id = this.getAttribute("data-id");
                    api("/admin/emotion/" + id + "/delete", { method: "POST" }).then(function () {
                        loadEmotions(currentEmotionPage);
                    });
                });
            });
        }).catch(function () {});
    }

    document.getElementById("emotions-refresh") && document.getElementById("emotions-refresh").addEventListener("click", function () {
        loadEmotions(1);
    });

    // ---------- Features ----------
    function loadFeatures() {
        api("/admin/features").then(function (d) {
            var tbody = document.getElementById("features-tbody");
            var list = d.features || [];
            tbody.innerHTML = list.map(function (f) {
                var id = "feat-" + f.id;
                return "<tr>" +
                    "<td>" + (f.feature_name || "—") + "</td>" +
                    "<td><button type=\"button\" class=\"admin-toggle " + (f.is_enabled ? "on" : "") + "\" data-id=\"" + f.id + "\" data-name=\"" + (f.feature_name || "") + "\" data-enabled=\"" + (f.is_enabled ? "1" : "0") + "\"></button></td>" +
                    "</tr>";
            }).join("");
            tbody.querySelectorAll(".admin-toggle").forEach(function (t) {
                t.addEventListener("click", function () {
                    var on = this.classList.toggle("on");
                    this.setAttribute("data-enabled", on ? "1" : "0");
                });
            });
        }).catch(function () {});
    }

    document.getElementById("features-save") && document.getElementById("features-save").addEventListener("click", function () {
        var toggles = document.querySelectorAll("#features-tbody .admin-toggle");
        var features = [];
        toggles.forEach(function (t) {
            features.push({
                feature_name: t.getAttribute("data-name"),
                is_enabled: t.getAttribute("data-enabled") === "1"
            });
        });
        api("/admin/features/update", {
            method: "POST",
            body: JSON.stringify({ features: features })
        }).then(function () {
            alert("Saved");
        }).catch(function (e) { alert(e.message || "Failed"); });
    });

    // ---------- Recommendations ----------
    function loadRecommendations() {
        api("/admin/recommendations").then(function (d) {
            var tbody = document.getElementById("recommendations-tbody");
            var list = d.recommendations || [];
            tbody.innerHTML = list.map(function (r, i) {
                var safeEmotion = (r.emotion || "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                return "<tr data-index=\"" + i + "\">" +
                    "<td><input type=\"text\" class=\"admin-input rec-emotion\" value=\"" + safeEmotion + "\" placeholder=\"emotion\"></td>" +
                    "<td><textarea class=\"cell-content rec-content\" placeholder=\"suggestion text\"></textarea></td>" +
                    "<td><button type=\"button\" class=\"admin-btn danger rec-remove\">Remove</button></td>" +
                    "</tr>";
            }).join("");
            list.forEach(function (r, i) {
                var row = tbody.rows[i];
                if (row) {
                    var contentEl = row.querySelector(".rec-content");
                    if (contentEl) contentEl.value = r.content || "";
                }
            });
            tbody.querySelectorAll(".rec-remove").forEach(function (b) {
                b.addEventListener("click", function () {
                    this.closest("tr").remove();
                });
            });
        }).catch(function () {});
    }

    document.getElementById("rec-add-row") && document.getElementById("rec-add-row").addEventListener("click", function () {
        var tbody = document.getElementById("recommendations-tbody");
        var tr = document.createElement("tr");
        tr.innerHTML = "<td><input type=\"text\" class=\"admin-input rec-emotion\" placeholder=\"emotion\"></td>" +
            "<td><textarea class=\"cell-content rec-content\" placeholder=\"suggestion text\"></textarea></td>" +
            "<td><button type=\"button\" class=\"admin-btn danger rec-remove\">Remove</button></td>";
        tbody.appendChild(tr);
        tr.querySelector(".rec-remove").addEventListener("click", function () { tr.remove(); });
    });

    document.getElementById("rec-save") && document.getElementById("rec-save").addEventListener("click", function () {
        var rows = document.querySelectorAll("#recommendations-tbody tr");
        var recommendations = [];
        rows.forEach(function (row) {
            var emotionEl = row.querySelector(".rec-emotion");
            var contentEl = row.querySelector(".rec-content");
            var emotion = (emotionEl && emotionEl.value || "").trim();
            var content = (contentEl && contentEl.value || "").trim();
            if (emotion) recommendations.push({ emotion: emotion, content: content });
        });
        api("/admin/recommendations/update", {
            method: "POST",
            body: JSON.stringify({ recommendations: recommendations })
        }).then(function () {
            alert("Saved");
            loadRecommendations();
        }).catch(function (e) { alert(e.message || "Failed"); });
    });

    // ---------- Logs ----------
    function loadLogs() {
        api("/admin/logs").then(function (logs) {
            var ul = document.getElementById("logs-list");
            ul.innerHTML = (logs || []).map(function (l) {
                return "<li>[" + (l.level || "") + "] " + (l.message || "") + " — " + (l.time || "");
            }).join("");
        }).catch(function () {});
    }

    // ---------- Pagination ----------
    function renderPagination(containerId, page, pages, onPage) {
        var container = document.getElementById(containerId);
        if (!container) return;
        if (pages <= 1) {
            container.innerHTML = "<span>Page 1 of 1</span>";
            return;
        }
        var html = "<button type=\"button\" " + (page <= 1 ? "disabled" : "") + " data-page=\"" + (page - 1) + "\">Prev</button>";
        html += " <span>Page " + page + " of " + pages + "</span> ";
        html += "<button type=\"button\" " + (page >= pages ? "disabled" : "") + " data-page=\"" + (page + 1) + "\">Next</button>";
        container.innerHTML = html;
        container.querySelectorAll("button[data-page]").forEach(function (b) {
            if (b.disabled) return;
            b.addEventListener("click", function () {
                onPage(parseInt(this.getAttribute("data-page"), 10));
            });
            b.removeAttribute("data-page");
        });
    }
})();
