<?php session_start(); include("./meta.php"); ?>   

<link rel="stylesheet" type="text/css" href="./jqplot/jquery.jqplot.min.css" media="screen" />
<link rel="stylesheet" type="text/css" href="./jqplot/jquery.jqplot.css" media="screen" />

<script type="text/javascript" src="./js/jquery.min.js"></script>

<!--[if lt IE 9]><script language="javascript" type="text/javascript" src=
                 "./jqplot/excanvas.js"></script><![endif]-->
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/jquery.min.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/jquery.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/jquery.jqplot.min.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/plugins/jqplot.logAxisRenderer.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/plugins/jqplot.dateAxisRenderer.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/plugins/jqplot.dateTickFormatter.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/plugins/jqplot.categoryAxisRenderer.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/plugins/jqplot.highlighter.js"></script>
    <script language="javascript" type="text/javascript" src=
                     "./jqplot/plugins/jqplot.cursor.js"></script>
    <script language="javascript" type="text/javascript" src=
                   "./jqplot/plugins/jqplot.enhancedLegendRenderer.js"></script> 
    <script type="text/javascript" src=
                     "./jqplot/plugins/jqplot.canvasOverlay.min.js"></script>
    <script type="text/javascript" src=
                   "./jqplot/plugins/jqplot.canvasTextRenderer.min.js"></script>
    <script type="text/javascript" src=
              "./jqplot/plugins/jqplot.canvasAxisLabelRenderer.min.js"></script>
    <script type="text/javascript" src=
               "./jqplot/plugins/jqplot.canvasAxisTickRenderer.min.js"></script>
    <script type="text/javascript" src=
                   "./jqplot/plugins/jqplot.dateAxisRenderer.min.js"></script>
    <script type="text/javascript" src=
                   "../it/jqueryui/jquery-ui.min.js"></script>

<style type="text/css">  
div#chart1 {height:30%; width:90%; max-width:92%; z-index:-10; margin:-20 auto;} 
</style> 
</head>

<body>
<?php
 $_SESSION['s_pageurl'] = "visgraph.php";
 $_SESSION['s_selezione'] = "3";  
 include("func.php");
 echo "<div id=\"wrap\">";
 include("inte.php");
 include("menu.php");
 echo "<div id=\"contentalt\">";
 
 $pulsante = $_POST['pulsa'];

 $file = fopen("./config/setup.cfg", "r");
 $stringa = fgets($file);
 $p = explode(";", $stringa); 
 $gapfile = $p[0];
 $fusefile = $p[1]; 
 $ch1 = $p[2];
 $ch2 = $p[3];
 $ch3 = $p[4];
 $ch4 = $p[5];
 $ch5 = $p[6];
 $ch6 = $p[7];
 $X1 = $p[8]; 
 $X2 = $p[9]; 
 $X3 = $p[10]; 
 $X4 = $p[11]; 
 $X5 = $p[12]; 
 $X6 = $p[13]; 
 $A1 = $p[14]; 
 $A2 = $p[15]; 
 $A3 = $p[16]; 
 $A4 = $p[17]; 
 $A5 = $p[18]; 
 $A6 = $p[19];
 $RT = $p[20];
 fclose($file); 
 
 switch ($RT){
    case 6: $chan = $ch6; break;
    case 5: $chan = $ch5; break;
    case 4: $chan = $ch4; break;
    case 3: $chan = $ch3; break;
    case 2: $chan = $ch2; break;
    case 1: 
    default: $chan = $ch1; break;
 
 }
//////////////////////////////////////////
?>
  <script type="text/javascript">
  
$(document).ready(function(){   

    var receivedData = [];
    var storedData = [];
    var sto = [];
    var plot1;
    let timerId = setInterval(renderGraph, 1000);

    $.jqplot.config.enablePlugins = true;   

///////////////////////////////
function renderGraph() {
        
     const xhr = new XMLHttpRequest();
     const method = "POST";
     const url = "./tmp/graph1.txt";

     xhr.open(method, url, true);
     xhr.onreadystatechange = () => {
       if (xhr.readyState === XMLHttpRequest.DONE) {
          const status = xhr.status;
          if (status === 0 || (status >= 200 && status < 400)) {
               //document.getElementById("chart1").innerHTML = xhr.responseText;
               sto = xhr.responseText;
               storedData = sto.replace(/'/g,"");
               //document.getElementById("chart1").innerHTML = storedData;
               storedData = JSON.parse(storedData);
               
          } else { // error! 
          }
       }
     };
     xhr.send();        
       
        if (plot1) {
            plot1.destroy();  
        }
       
        plot1 = $.jqplot('chart1', [storedData], {
            title: ' ',
            cursor: {
                show: true,
                zoom: true
            },            

            seriesDefaults:{
               showMarker: false,
               shadow: false,
               showLine:true,
               markerOptions: { style:"circle", size: 3 },
               lineWidth: 3
            },
                        
             series: [
                {   breakOnNull: false,
                    color: 'rgba(0,0,129,1)'
                }            
            ], 
                        
            axes: {
                xaxis: {
                   label :'Time',
                     min:'-5',
                     max:'105' 
                },
                yaxis: {
                   labelRenderer: $.jqplot.CanvasAxisLabelRenderer,                
                   label: ''
                }
            }
        }).replot();
    }
///////////////////////////////
});
</script>

<?php
    echo $chan;
    echo "<br /><div id=\"chart1\"></div>"; 
echo "<br />";
include("./app_footer.php");
echo "</div>";
echo "</body>";
echo "</html>";

?>
