(function () {

    toastr.options.closeButton = true;

    function playSound(mp3FileName, oggFilename) {
        var mp3Source = '<source src="' + mp3FileName + '" type="audio/mpeg">';
        var oggSource = '<source src="' + oggFilename + '" type="audio/ogg">';
        var embedSource = '<embed hidden="true" autostart="true" loop="false" src="' + mp3FileName + '">';
        var soundElement = document.getElementById("sound_wrapper");
        soundElement.innerHTML = '<audio autoplay="autoplay">' + mp3Source + oggSource + embedSource + '</audio>';
    }

    var socket = new ReconnectingWebSocket((window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/grows/' + GROW_IDENTIFIER + '/', null, {
        debug: true,
        reconnectInterval: 3000
    });

    socket.onopen = function open() {
        console.log('WebSockets connection created.');
        //socket.send('{}')
    };

    socket.onmessage = function (event) {
        var data = JSON.parse(event.data);
        if (data.type === 'sensor_update') {
            playSound(SOUND_URLS.success.mp3, SOUND_URLS.success.ogg);
            if (data.data.event === 'setup_download') {
                toastr["info"]("Sensor '" + data.data.sensor.name + "' has downloaded setup file.");
            } else if (data.data.event === 'setup_started') {
                toastr["info"]("Sensor '" + data.data.sensor.name + "' has started setup!");
            } else if (data.data.event === 'setup_executable_download') {
                toastr["info"]("Sensor '" + data.data.sensor.name + "' has downloaded the executable script.");
            } else if (data.data.event === 'setup_finished') {
                toastr["success"]("Sensor '" + data.data.sensor.name + "' has finished being setup!");
            } else {
                console.warn('Unknown sensor update: ', data);
            }
        } else {
            console.warn('Unknown message type: ', data)
        }
    };

    if (socket.readyState == WebSocket.OPEN) {
        socket.onopen();
    }

})();
