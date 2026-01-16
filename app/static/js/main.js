async function postJson(url, payload = null) {
  const res = await fetch(url, {
    method: "POST",
    headers: payload ? { "Content-Type": "application/json" } : {},
    body: payload ? JSON.stringify(payload) : null,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.error || `Request failed: ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

function updateCardFromTask(card, task) {
  const title = card.querySelector(".task-title");
  const checkbox = card.querySelector(".js-toggle");

  checkbox.checked = !!task.is_done;
  card.classList.toggle("task-done", !!task.is_done);

  const badgesRow = title.parentElement;
  let doneBadge = badgesRow.querySelector(".badge.text-bg-success");

  if (task.is_done) {
    if (!doneBadge) {
      doneBadge = document.createElement("span");
      doneBadge.className = "badge text-bg-success";
      doneBadge.textContent = "Done";
      badgesRow.appendChild(doneBadge);
    }
  } else {
    if (doneBadge) doneBadge.remove();
  }
}

document.addEventListener("click", async (e) => {
  const toggle = e.target.closest(".js-toggle");
  if (toggle) {
    const card = toggle.closest(".task-card");
    const taskId = card.dataset.taskId;
    try {
      const data = await postJson(`/tasks/${taskId}/toggle`);
      updateCardFromTask(card, data.task);
    } catch (err) {
      alert(err.message);
      toggle.checked = !toggle.checked;
    }
    return;
  }

  const delBtn = e.target.closest(".js-delete");
  if (delBtn) {
    const card = delBtn.closest(".task-card");
    const taskId = card.dataset.taskId;

    if (!confirm("Delete this task?")) return;

    try {
      await postJson(`/tasks/${taskId}/delete`);
      card.remove();
    } catch (err) {
      alert(err.message);
    }
  }
});
