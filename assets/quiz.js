// ===== Atmart — quiz (retry until pass) + self-assessment poll =====
(function () {
  document.querySelectorAll(".quiz").forEach(function (quiz) {
    var pass = +(quiz.dataset.pass || 80);
    var check = quiz.querySelector(".quiz-check");
    var retry = quiz.querySelector(".quiz-retry");
    var result = quiz.querySelector(".quiz-result");
    if (!check) return;
    check.addEventListener("click", function () {
      var qs = quiz.querySelectorAll(".q");
      var total = qs.length, correct = 0, answered = 0;
      qs.forEach(function (q) {
        var sel = q.querySelector("input:checked");
        q.classList.remove("q-right", "q-wrong");
        if (sel) { answered++;
          if (+sel.value === +q.dataset.correct) { correct++; q.classList.add("q-right"); }
          else { q.classList.add("q-wrong"); }
        }
      });
      if (answered < total) {
        result.innerHTML = '<span class="quiz-warn">' + (quiz.dataset.answerall || "Please answer every question.") + "</span>";
        return;
      }
      var score = Math.round((correct / total) * 100);
      if (score >= pass) {
        result.innerHTML = '<span class="quiz-pass">✅ ' + score + "% — " + (quiz.dataset.passmsg || "Passed! You can move on.") + "</span>";
        check.style.display = "none"; if (retry) retry.style.display = "none";
        if (quiz.id) try { localStorage.setItem("atmart_" + quiz.id, "1"); } catch (e) {}
        var li = document.querySelector('.tuto-toc a[href="#' + (quiz.dataset.module || "") + '"]');
        if (li && li.textContent.indexOf("✅") === -1) li.textContent = "✅ " + li.textContent;
      } else {
        result.innerHTML = '<span class="quiz-fail">' + score + "% — " + (quiz.dataset.failmsg || ("Not yet. Aim for " + pass + "%. Review the module and try again.")) + "</span>";
        if (retry) retry.style.display = "";
      }
    });
    if (retry) retry.addEventListener("click", function () {
      quiz.querySelectorAll("input:checked").forEach(function (i) { i.checked = false; });
      quiz.querySelectorAll(".q").forEach(function (q) { q.classList.remove("q-right", "q-wrong"); });
      result.innerHTML = ""; check.style.display = ""; retry.style.display = "none";
      quiz.scrollIntoView({ block: "nearest" });
    });
  });

  document.querySelectorAll(".poll").forEach(function (poll) {
    var btn = poll.querySelector(".poll-check");
    var out = poll.querySelector(".poll-result");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var rows = poll.querySelectorAll(".poll-row"), lines = [], done = true;
      rows.forEach(function (r) {
        var sel = r.querySelector("input:checked");
        if (sel) lines.push("<li><strong>" + r.dataset.skill + ":</strong> " + sel.dataset.label + "</li>");
        else done = false;
      });
      if (!done) { out.innerHTML = '<span class="quiz-warn">' + (poll.dataset.answerall || "Please rate every line.") + "</span>"; return; }
      out.innerHTML = "<p style='margin-bottom:.4rem'>" + (poll.dataset.resultmsg || "Your self-assessment:") + "</p><ul>" + lines.join("") + "</ul>";
    });
  });
})();
