<?php

require 'vendor/autoload.php';
use Aws\S3\S3Client;

// TODO: Remove antonio in front of prefix

class s3Manager{
    private $awsAccessKey;
    private $awsSecretKey;
    private $bucket;
    private $prefix;
    private $s3;
    private $gestureComplexity;

    function __construct($awsAccessKey, $awsSecretKey, $bucket, $prefix){
        $this->awsAccessKey = $awsAccessKey;
        $this->awsSecretKey = $awsSecretKey;
        $this->bucket = $bucket;
        $this->prefix = $prefix;
        /*
            Possible gesture complexity:
                - body
                - single-hand
                - single-hand-body
                - multi-hand
                - multi-hand-body
        */
        $this->gestureComplexity = $this->getGestureComplexity();

        $this->s3 = new S3Client([
            'version' => 'latest',
            'region'  => 'eu-west-1', // Your AWS region
            'credentials' => [
                'key'    => $this->awsAccessKey,
                'secret' => $this->awsSecretKey
            ]
        ]);
    }

    function changePrefix($newPrefix){
        $this->prefix = $newPrefix;
        $this->gestureComplexity = $this->getGestureComplexity();
        return true;
    }

    function getVideosNames($fileType='.csv'){
        $videosNames = array();
        // Get lists
        $results = $this->s3->getPaginator('ListObjects', [
            'Bucket' => $this->bucket,
            'Prefix' => 'antonio/'.$this->prefix
        ]);
        // Cycle through objects
        foreach ($results as $result) {
            foreach ($result['Contents'] as $object) {
                $name = $object['Key'];
                if(strrpos($name, $fileType) != False){
                    array_push($videosNames, $name);
                }
            }
        }
        
        return $videosNames;
    }
    
    function getS3FileContent($key){
        // Get the content
        $result = $this->s3->getObject([
            'Bucket' => $this->bucket,
            'Key'    => $key,
            'Body'   => 'this is the body!',
        ]);
        // Store it in array
        $content = array_slice(explode("\n", $result['Body']), 1);
    
        return $content;
    }

    
    function getGestureComplexity(){
        return substr($this->prefix, 0, strpos($this->prefix, "/"));
    }

    function reverseAlphabeticalSort($videosNames){
        /*
            Possible gesture complexity:
                - body
                - single-hand
                - single-hand-body
                - multi-hand
                - multi-hand-body
        */

        switch($this->gestureComplexity){
            case "body":
            case "single-hand":
                return $videosNames;
                break;
        
            case "single-hand-body":
            case "multi-hand":
                $middle = count($videosNames)/2;
                $result = array();
                
                $l1 = array_slice($videosNames, 0, $middle);
                $l2 = array_slice($videosNames, $middle);
                
                for($a = 0; $a < count($l1); $a++){
                    array_push($result, $l1[$a], $l2[$a]);
                }
                return $result;
                break;
        
            case "multi-hand-body":
                $third = count($videosNames)/3;
                $result = array();

                $l1 = array_slice($videosNames, 0, $third);
                $l2 = array_slice($videosNames, $third, $third);
                $l3 = array_slice($videosNames, $third*2);
                
                for($a = 0; $a < count($l1); $a++){
                    array_push($result, $l1[$a], $l2[$a], $l3[$a]);
                }
                return $result;
                break;
        }
    }

    private function getPosePart($str){
        $idx = strrpos($str, substr($str, strrpos($str, "/")));
        return substr(substr($str, 0, $idx), strrpos(substr($str, 0, $idx), "/")+1);
    }

    private function getFileName($str){
        return substr($str, strrpos($str, "/")+1, strrpos($str, ".")-strrpos($str, "/")-1);
    }

    function joinGestureData($videos){
        $finalArray = array();
        
        switch($this->gestureComplexity){
            case "body":
            case "single-hand":
                return $videos;
                break;
        
            case "single-hand-body":
            case "multi-hand":
                for($a = 0; $a < count($videos); $a = $a + 2){
                    $finalArray[$this->getFileName($videos[$a][0])] = array(
                        $this->getPosePart($videos[$a][0]) => $videos[$a][1],
                        $this->getPosePart($videos[$a+1][0]) => $videos[$a+1][1]
                    );
                }
                return $finalArray;
                break;
        
            case "multi-hand-body":
                for($a = 0; $a < count($videos); $a = $a + 3){
                    $finalArray[$this->getFileName($videos[$a][0])] = array(
                        $this->getPosePart($videos[$a][0]) => $videos[$a][1],
                        $this->getPosePart($videos[$a+1][0]) => $videos[$a+1][1],
                        $this->getPosePart($videos[$a+2][0]) => $videos[$a+2][1]
                    );
                }
                return $finalArray;
                break;
        }
    }

    function generateVideosJsList(){
        $videosNames = $this->getVideosNames();
        $videosNames = $this->reverseAlphabeticalSort($videosNames);
        $videosFull = array();


        for($idx = 0; $idx < count($videosNames); $idx++){
            $fileName = $videosNames[$idx];
            $fileContent = $this->getS3FileContent($fileName);
            array_push($videosFull, array($fileName, $fileContent));
        }
        return json_encode($this->joinGestureData($videosFull), JSON_PRETTY_PRINT);
    }
}

?>