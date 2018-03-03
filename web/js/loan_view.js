function updatePercent() {
    document.getElementById("pct").innerHTML = Math.round(1000 * document.getElementById("input").value / [[loan_ceiling]]) / 10
}