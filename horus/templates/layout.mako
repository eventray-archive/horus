<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Horus Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="${request.static_url('horus:static/assets/css/bootstrap.css')}" rel="stylesheet">
    <link href="${request.static_url('horus:static/assets/css/bootstrap-responsive.css')}" rel="stylesheet">

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
  </head>

  <body>
    <div>
      <div class="container-fluid">
        <div class="row-fluid">
          <div class="span2">
            &nbsp;
            <!-- this div keeps the content centered -->
          </div>
          <div class="span4">
            ${next.body()}
        </div>
      </div> <!-- /container -->
    </div>

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="${request.static_url('horus:static/assets/js/jquery.js')}"></script>
  </body>
</html>
