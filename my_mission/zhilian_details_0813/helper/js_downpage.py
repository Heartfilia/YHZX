jd = """
(function () {
    var y = 0;
    var step = 100;
    window.scroll(0, 0);
    function f() {
        if (y < document.body.scrollHeight) {
            y += step;
            window.scroll(0, y);
            setTimeout(f, 100);
        } 
        /* else {
            window.scroll(0, 0);
            document.title += "scroll-done";
        } */
    }
    setTimeout(f, 1000);
})();
"""