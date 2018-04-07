// Stolen from W3
function move(elem, limit) {
    console.log("Moved bar.");
    console.log(elem);
    //var elem = document.getElementById("myBar");
    var width = 1;
    var id = setInterval(frame, 15);
    function frame() {
        if (width >= limit) {
            clearInterval(id);
        } else {
            width++;
            elem.style.width = width + '%';
        }
    }
}