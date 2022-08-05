var collect = (function () {
    let $els = null;
    let maxRecordingTime = null;
    let recordedBlob = null;
    let startRecordingDelay = null;
    let stream = null;

    let _initElements = function () {
        $els = {
            controls: document.getElementById("controls"),

            loader: document.getElementById("loader"),
            countdown: document.getElementById("countdown"),
            countdownText: document.getElementById("countdown-text"),

            startBtn: document.getElementById("startBtn"),
            stopBtn: document.getElementById("stopBtn"),
            uploadBtn: document.getElementById("uploadBtn"),

            maxRecordingTimeInput: document.getElementById("maxRecordingTimeInput"),
            startRecordingDelayInput: document.getElementById("startRecordingDelay"),

            preview: document.getElementById("preview"),
            previewContainer: document.getElementById("preview-container"),
            recording: document.getElementById("recording"),
            recordingContainer: document.getElementById("recording-container"),
            recorded: document.getElementById("recorded"),
            recordedContainer: document.getElementById("recorded-container"),
        }

        $els.stopBtn.disabled = true;
        $els.uploadBtn.disabled = true;

        _hideElement($els.recordingContainer);
        _hideElement($els.recordedContainer);
        _hideElement($els.countdown);
    }

    function _fadeOutElement(el){
        $(el).fadeOut(500);
    }

    function _showCountdown(msecs){
        $els.countdownText.innerHTML = msecs / 1000;
        _showElement($els.countdown);
        msecs = msecs + 1000;

        setTimeout(function(){
            clearInterval(timerInterval);
            _fadeOutElement($els.countdown);
        },msecs);

        let timerInterval = setInterval(function(){
            $els.countdownText.innerHTML -= 1;
        }, 1000);
    }

    let _hideElement = function (el) {
        el.style.display = "none";
    }

    let _showElement = function (el) {
        el.style.display = "flex";
    }

    let _isPositiveInteger = function (str) {
        if (typeof str !== 'string') {
            return false;
        }

        const num = Number(str);

        if (Number.isInteger(num) && num > 0) {
            return true;
        }

        return false;
    }

    let _getPositiveNumFromInput = function (inputEl) {
        if (_isPositiveInteger(inputEl.value)) {
            return inputEl.value * 1000;
        }
    }

    let _bindEvents = function () {
        $els.startBtn.addEventListener("click", function () {
            _showCountdown(startRecordingDelay);
            setTimeout(startRecording, startRecordingDelay);
        }, false);
        $els.stopBtn.addEventListener("click", stopRecording, false);
        $els.uploadBtn.addEventListener("click", upload, false);
        $els.maxRecordingTimeInput.addEventListener("keyup", function () {
            maxRecordingTime = _getPositiveNumFromInput($els.maxRecordingTimeInput);
        });
        $els.startRecordingDelayInput.addEventListener("keyup", function () {
            startRecordingDelay = _getPositiveNumFromInput($els.startRecordingDelayInput);
        });
    }

    let _initWebcam = async function () {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        let { width, height } = stream.getTracks()[0].getSettings();
        console.log(`Webcam opened at ${width}x${height} px resolution`);
    }

    let _wait = function (msecs) {
        return new Promise(resolve => setTimeout(resolve, msecs));
    }

    let startPreview = function () {
        navigator.mediaDevices.getUserMedia({
            // video: { width: 1920, height: 1080 },
            video: true,
            audio: false
        }).then(stream => {
            $els.preview.srcObject = stream;
            $els.uploadBtn.href = stream;
            $els.preview.captureStream = $els.preview.captureStream || $els.preview.mozCaptureStream;
            console.log(`max recording time: ${maxRecordingTime}`);
            return new Promise(resolve => $els.preview.onplaying = resolve);
        })
    }

    let startRecording = function () {
        function _startRecording(stream, lengthInMS) {
            let recorder = new MediaRecorder(stream, {
                videoBitsPerSecond: 2500000,
                // mimeType: 'video/mp4' not supported so far
            });
            let data = [];

            recorder.ondataavailable = event => data.push(event.data);
            recorder.start();
            console.log(recorder.state + " for " + (lengthInMS / 1000) + " seconds...");

            let stopped = new Promise((resolve, reject) => {
                recorder.onstop = resolve;
                recorder.onerror = event => reject(event.name);
            });

            let recorded = _wait(lengthInMS).then(
                () => recorder.state == "recording" && recorder.stop()
            );

            return Promise.all([
                stopped,
                recorded
            ])
                .then(() => data);
        }

        $els.startBtn.disabled = true;
        $els.stopBtn.disabled = false;
        _hideElement($els.previewContainer);
        _showElement($els.recordingContainer);

        navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        })
        .then(stream => {
            $els.recording.srcObject = stream;
            // $els.uploadBtn.href = stream;
            $els.recording.captureStream = $els.recording.captureStream || $els.recording.mozCaptureStream;
            console.log(`max recording time: ${maxRecordingTime}`);
            return new Promise(resolve => $els.recording.onplaying = resolve);
        })
        .then(() => _startRecording($els.recording.captureStream(), maxRecordingTime))
        .then(recordedChunks => {
            $els.stopBtn.disabled = true;
            $els.uploadBtn.disabled = false;
            $els.startBtn.disabled = false;
            $els.startBtn.innerHTML = "Restart";
            // outputDiv.style.display = "block";
            recordedBlob = new Blob(recordedChunks, { type: "video/webm" });
            $els.recorded.src = URL.createObjectURL(recordedBlob);
            // $els.uploadBtn.href = $els.recorded.src;
            // $els.uploadBtn.download = "RecordedVideo.webm";
            _hideElement($els.recordingContainer);
            _showElement($els.recordedContainer);

            console.log("Successfully recorded " + recordedBlob.size + " bytes of " + recordedBlob.type + " media.");
        })
        .catch(function (err) {
            console.log(`Error: ${err}`);
        });
    }

    let stopRecording = function () {
        $els.preview.srcObject.getTracks().forEach(track => track.stop());
    }

    let upload = function () {
        var data = new FormData()
        data.append('file', recordedBlob, 'file.mp4')
        data.append('namespace', namespace_selected)
        data.append('gesture', gesture_selected)

        fetch('/upload', {
            method: 'POST',
            body: data

        })
        .then(response => response.json())
        .then(json => {
            console.log(json)
        });
    }

    async function init() {
        _initElements();

        maxRecordingTime = _getPositiveNumFromInput($els.maxRecordingTimeInput);
        startRecordingDelay = _getPositiveNumFromInput($els.startRecordingDelayInput)

        _bindEvents();
        _initWebcam();
        startPreview();
    }

    return {
        init,
    }
})();

document.addEventListener("DOMContentLoaded", function (event) {
    collect.init();
});
