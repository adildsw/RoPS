var SERVER_IP = "http://192.168.86.178:5000/";
// var SERVER_IP = "http://172.26.113.186:5000/";

$(document).ready(function() {
    $("#btnEasy").on("click", function() {
        console.log("Hi");
        setDifficulty("Easy");
    });
    $("#btnMedium").on("click", function() {
        setDifficulty("Medium");
    });
    $("#btnHard").on("click", function() {
        setDifficulty("Hard");
    });

    $("#btnSampleRhythm").on("click", function() {
        $("#labelStatus").html("STATUS: Sample Rhythm Playing");
        $.fn.getRequest(SERVER_IP + "playSampleRhythm", resetStatusLabel);
    });

    $("#btnStartGame").on("click", function() {
        $("#labelStatus").html("STATUS: Game Running");
        $.fn.getRequest(SERVER_IP + "startGame", resetStatusLabel);
    });

    function setDifficulty(difficulty) {
        if (difficulty == "Easy") {
            $.fn.getRequest(SERVER_IP + "setBpm?bpm=60", setBPM);
        }
        else if(difficulty == "Medium") {
            $.fn.getRequest(SERVER_IP + "setBpm?bpm=90", setBPM);
        }
        else if(difficulty == "Hard") {
            $.fn.getRequest(SERVER_IP + "setBpm?bpm=120", setBPM);
        }
    }

    function setBPM(data) {
        $("#labelBPM").html(data);
    }

    function resetStatusLabel(data) {
        $("#labelStatus").html("STATUS: Ready");
    }

    setDifficulty("Medium");
});

$.fn.getRequest = function(url, callback) {
    var http = new XMLHttpRequest();
    http.open("GET", url, true);
    http.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200) {
            if (callback != null) {
                callback(this.responseText);
            }
        }
    }
    http.send(null);
}