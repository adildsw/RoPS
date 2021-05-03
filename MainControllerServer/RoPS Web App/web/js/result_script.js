var SERVER_IP = "http://192.168.86.178:5000/";
// var SERVER_IP = "http://172.26.113.186:5000/";

$(document).ready(function() {
    function initiateLoadTable(table_data) {
        $.fn.getRequest(SERVER_IP + "gamelogs", loadTable);
    }

    function cleanRawTableData(raw_table_data) {
        var data = raw_table_data.substring(2, raw_table_data.length - 3);
        data = data.split("}, ");
        for (var i = 0; i < data.length - 1; i++) {
            data[i] = data[i] + "}"
        }
        for (var i = 0; i < data.length; i++) {
            data[i] = data[i].replaceAll("'", '"');
            data[i] = JSON.parse(data[i]);
        }
        
        return data
    }

    function loadTable(raw_table_data) {
        var data = cleanRawTableData(raw_table_data);

        var round_count = 0;
        var robot_win_count = 0;
        var human_win_count = 0;
        var draw_count = 0;
        var invalid_round_count = 0;

        data.forEach(item => {
            var markup = "<td>" + item.game_count + "</td><td>" + item.round_count + "</td><td>" + item.round_start_time + "</td><td>" + item.winner + "</td><td>" + item.robot_move + "</td><td>" + item.human_move + "</td><td>" + item.robot_rhythm + "</td><td>" + item.human_rhythm + "</td><td>" + item.move_delay + "</td><td>" + item.round_validity + "</td>";
            if (item.round_validity == "Valid" || item.round_validity == undefined) {
                if (item.winner == "Robot") {
                    markup = "<tr class='negative'>" + markup + "</tr>"
                }
                else if (item.winner == "Human") {
                    markup = "<tr class='positive'>" + markup + "</tr>"
                }
                else {
                    markup = "<tr>" + markup + "</tr>"
                }
            }
            else {
                markup = "<tr class='disabled'>" + markup + "</tr>"
            }
            $("#tableBody").append(markup);

            // Calculating Statistics Overview
            round_count++;
            if (item.round_validity == "Valid" || item.round_validity == undefined) {
                if (item.winner == "Robot") {
                    robot_win_count++;
                }
                else if (item.winner == "Human") {
                    human_win_count++;
                }
                else if (item.winner == "Draw") {
                    draw_count++;
                }
            }
            else {
                invalid_round_count++;
            }
        });

        $("#divRoundsPlayed").html(round_count);
        $("#divHumanWins").html(human_win_count);
        $("#divRobotWins").html(robot_win_count);
        $("#divDraws").html(draw_count);
        $("#divInvalidRounds").html(invalid_round_count);
    }

    initiateLoadTable();
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