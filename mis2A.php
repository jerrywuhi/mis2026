<!DOCTYPE html>
<html lang="zh-TW">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>jerrywu</title>
	<style type="text/css">
		* { font-family:"標楷體"; margin-left:auto; margin-right:auto;}
		h1 {color:blue; font-size:60px;}
		h2 {color:#33ff33; font-size:40px;}
	</style>

	<script>
		function change1() {
  			document.getElementById("pic").src = "mountain.jpg";
  			document.getElementById("h2text").innerText = "靜宜資管";
		}

		function change2() {
  			document.getElementById("pic").src = "cliff.jpg";
  			document.getElementById("h2text").innerText = "jerrywu";
		}
	</script>


</head>
<body>
	
</body>
</html>
    <table width="70%">
		<tr>
			<td>
				<img src="cliff.jpg" width="110%"id="pic" onmouseover="change1()" onmouseout="change2()"></img>
			</td>

			<td>


    <h1>吳冠頡<h1>
    <h2>wu guan jie<h2>

    </td>
		</tr>
	</table>

<?php echo date("Y-m-d") ?>

<table width="70%" border="1">
		<tr>
			<td>

    
    個人網頁<br>
    fb:https:<a href="//www.facebook.com/">https://www.facebook.com/</a><br>
    Tel:<br>
    E-mail: <a href="mailto:wu0952686160@gmail.com">tcyang@pu.edu.tw</a><br>
</body>


    </td>

			<td>


    大象席地而坐電影配樂<br>
	<audio controls>
		<source src="elephant.mp3" type="audio/mP3">
	</audio><br>

	</td>

			<td>



    不要去台灣<br>
    <iframe src="https://www.youtube.com/embed/pW88QFpHXa8" allowfullscreen></iframe>


    </td>
		</tr>
	</table>		


</body>    
</html>