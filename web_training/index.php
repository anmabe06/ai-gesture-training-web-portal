<?php

include_once 'S3Manager.php';

$conditionB = isset($_GET["gesture_complexity"]) && isset($_GET["gesture_name"]) && isset($_GET["bucket"]) && isset($_GET["aws_access_key"]) && isset($_GET["aws_secret_key"]);
$conditionA = $_GET["gesture_complexity"] != "" && $_GET["gesture_name"] != "" && $_GET["bucket"] != "" && $_GET["aws_access_key"] != "" && $_GET["aws_secret_key"] != "";

if($conditionA && $conditionB){
  $s3Manager = new S3Manager($_GET["aws_access_key"], $_GET["aws_secret_key"], $_GET["bucket"], $_GET["gesture_complexity"]."/".$_GET["gesture_name"]."/csv/");
  echo "<h3 style='color: green' id='live-feedback'>🗣 The data of <i>'".$_GET["gesture_name"]."'</i> of complexity <i>'".$_GET["gesture_complexity"]."'</i> has been retrieved</h3>";

}else{
  echo "<h3 style='color: red' id='live-feedback'>🗣 Please fill in the input form to proceed</h3>";
}

//echo $s3Manager->generateVideosJsList();

?>

<!DOCTYPE html>
<html>
  <head>
    <title>ML5 NN training</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="info-container">
      <div style="flex-basis: 45%; max-width: 45%">
        <h4><u>Input: </u></h4>
        <div id="gesture-form-div">
          <form action="index.php" method="get">
            <label for="fname">Gesture complexity: </label>
            <input type="text" class="text-input" id="gesture_complexity" name="gesture_complexity" required><br><br>

            <label for="fname">Gesture name: </label>
            <input type="text" class="text-input" id="gesture_name" name="gesture_name" required><br><br>

            <label for="fname">Bucket: </label>
            <input type="text" class="text-input" id="bucket" name="bucket" value="chiara-gestures-dataset" required><br><br>

            <label for="fname">AWS Access Key: </label>
            <input type="text" class="text-input" id="aws_access_key" name="aws_access_key" value="-" required><br><br>

            <label for="fname">AWS Secret Key: </label>
            <input type="text" class="text-input" id="aws_secret_key" name="aws_secret_key" value="-" required><br><br>

            <input type="checkbox" class="checkbox" id="show_data" name="show_data">
            <label for="show_data"> Show retrieved data</label><br><br>

            <input type="submit" class="button" style="vertical-align:middle" value="Submit">
          </form>
        </div>
      </div>
      <div style="flex-basis: 45%; max-width: 45%">
        <?php
          if(isset($_GET["show_data"]) && $_GET["show_data"] == "on"){
            echo "<h4><u>Retrieved data (JSON): </u></h4><div id='retrieved-data'><pre>".$s3Manager->generateVideosJsList()."</pre></div><br>";
          }
        ?>
      </div>
    </div>
    <script>
        let videos = <?php echo $s3Manager->generateVideosJsList()?>;

        console.log(videos);
    </script>
  </body>
</html>

