<?php
//读取文本
$str = explode("\n", file_get_contents('https://cdn.jsdelivr.net/gh/zknb-666/-/pc.txt'));
$k = rand(0,count($str));
$sina_img = str_re($str[$k]);

$size_arr = array('kf', 'mw1024', 'mw690', 'bmiddle', 'small', 'thumb180', 'thumbnail', 'square');
$size = !empty($_GET['size']) ? $_GET['size'] : 'kf' ;
if(!in_array($size, $size_arr)){
	$size = 'large';
}
$url = ''.$sina_img.'';
//解析结果
$result=array("code"=>"200","acgurl"=>"$url");
//Type Choose参数代码
$type=$_GET['return'];
switch ($type)
{   
   
//格式解析        
case 'json':
$path = "$url";
$pathinfo = pathinfo($path);
$imageInfo = getimagesize($url);  
$result['width']="$imageInfo[0]";  
$result['height']="$imageInfo[1]";
$result['size']="$pathinfo[extension]";    
header('Content-type:text/json');
echo json_encode($result);
break;
//格式解析                             
case 'img':
$img = file_get_contents($url,true);
//使用图片头输出浏览器
header("Content-Type: image/jpeg;");
echo $img;
break;
//IMG
default:
header("Location:".$result['acgurl']);
break;
}
function str_re($str){
  $str = str_replace(' ', "", $str);
  $str = str_replace("\n", "", $str);
  $str = str_replace("\t", "", $str);
  $str = str_replace("\r", "", $str);
  return $str;
}
?>